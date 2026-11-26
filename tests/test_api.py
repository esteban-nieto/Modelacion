def test_login_correcto_e_incorrecto(cliente):
    bueno = cliente.post("/api/auth/login", json={"correo": "administrador@prueba.co", "clave": "Prueba12345"})
    malo = cliente.post("/api/auth/login", json={"correo": "administrador@prueba.co", "clave": "otra"})
    assert bueno.status_code == 200 and bueno.json()["rol"] == "administrador"
    assert malo.status_code == 401


def test_requiere_autenticacion(cliente):
    assert cliente.get("/api/pacientes").status_code == 401
    assert cliente.get("/api/pacientes", headers={"Authorization": "Bearer falso"}).status_code == 401


def test_rol_consulta_solo_lee(cliente, entrar):
    cabecera = entrar("consulta")
    assert cliente.get("/api/pacientes", headers=cabecera).status_code == 200
    assert cliente.delete("/api/pacientes/1", headers=cabecera).status_code == 403
    assert cliente.post("/api/sedes", json={"nombre": "Nueva", "vereda": "Otra"}, headers=cabecera).status_code == 403


def test_operador_no_elimina_ni_administra_usuarios(cliente, entrar):
    cabecera = entrar("operador")
    assert cliente.delete("/api/pacientes/1", headers=cabecera).status_code == 403
    assert cliente.get("/api/usuarios", headers=cabecera).status_code == 403


def test_crud_completo_de_paciente_con_borrado_logico(cliente, entrar):
    cabecera = entrar("operador")
    datos = {"documento": "99999", "nombre": "Nuevo Paciente", "telefono": "3109876543", "fecha_nacimiento": "1985-05-05T00:00:00"}
    creado = cliente.post("/api/pacientes", json=datos, headers=cabecera)
    assert creado.status_code == 201
    identificador = creado.json()["id"]
    datos["nombre"] = "Nombre Cambiado"
    assert cliente.put(f"/api/pacientes/{identificador}", json=datos, headers=cabecera).json()["nombre"] == "Nombre Cambiado"
    administrador = entrar("administrador")
    assert cliente.delete(f"/api/pacientes/{identificador}", headers=administrador).status_code == 204
    assert cliente.get(f"/api/pacientes/{identificador}", headers=administrador).status_code == 404


def test_documento_duplicado_devuelve_conflicto(cliente, entrar):
    datos = {"documento": "123456", "nombre": "Repetido Doc", "telefono": "3109876543", "fecha_nacimiento": "1985-05-05T00:00:00"}
    assert cliente.post("/api/pacientes", json=datos, headers=entrar("operador")).status_code == 409


def test_validaciones_de_formulario(cliente, entrar):
    datos = {"documento": "abc", "nombre": "x", "telefono": "1", "fecha_nacimiento": "1985-05-05T00:00:00"}
    respuesta = cliente.post("/api/pacientes", json=datos, headers=entrar("operador"))
    assert respuesta.status_code == 422


def test_listado_con_busqueda_orden_y_paginacion(cliente, entrar):
    cabecera = entrar("administrador")
    for i in range(12):
        cliente.post(
            "/api/pacientes",
            json={"documento": f"5000{i:02d}", "nombre": f"Persona Lista {i}", "telefono": "3100000000", "fecha_nacimiento": "1980-01-01T00:00:00"},
            headers=cabecera,
        )
    pagina = cliente.get("/api/pacientes?tamano=5&pagina=2&orden=nombre&direccion=desc", headers=cabecera).json()
    assert pagina["total"] == 13 and pagina["paginas"] == 3 and len(pagina["items"]) == 5
    busqueda = cliente.get("/api/pacientes?busqueda=Lista 11", headers=cabecera).json()
    assert busqueda["total"] == 1
    assert cliente.get("/api/pacientes?orden=clave_hash", headers=cabecera).status_code == 422


def test_crear_cita_valida_y_validaciones_de_negocio(cliente, entrar, cita_valida):
    cabecera = entrar("operador")
    assert cliente.post("/api/citas", json=cita_valida, headers=cabecera).status_code == 201
    servicio_ajeno = {**cita_valida, "servicio_id": 2}
    assert cliente.post("/api/citas", json=servicio_ajeno, headers=cabecera).status_code == 422
    tiempos_invertidos = {**cita_valida, "fin_atencion": "2024-03-04T08:00:00"}
    assert cliente.post("/api/citas", json=tiempos_invertidos, headers=cabecera).status_code == 422
    paciente_inexistente = {**cita_valida, "paciente_id": 999}
    assert cliente.post("/api/citas", json=paciente_inexistente, headers=cabecera).status_code == 422


def test_profesional_con_relacion_muchos_a_muchos(cliente, entrar):
    cabecera = entrar("operador")
    datos = {"nombre": "Dr. Luis Mora", "sede_id": 1, "servicios_ids": [1, 2]}
    creado = cliente.post("/api/profesionales", json=datos, headers=cabecera)
    assert creado.status_code == 201 and len(creado.json()["servicios"]) == 2
    assert cliente.post("/api/profesionales", json={**datos, "servicios_ids": [99]}, headers=cabecera).status_code == 422


def test_usuarios_solo_administrador_y_clave_segura(cliente, entrar):
    cabecera = entrar("administrador")
    datos = {"nombre": "Nuevo Usuario", "correo": "nuevo@prueba.co", "clave": "Segura12345", "rol_id": 2}
    assert cliente.post("/api/usuarios", json=datos, headers=cabecera).status_code == 201
    assert cliente.post("/api/usuarios", json={**datos, "correo": "otro@prueba.co", "clave": "corta"}, headers=cabecera).status_code == 422
    sin_clave = {k: v for k, v in datos.items() if k != "clave"}
    assert cliente.post("/api/usuarios", json={**sin_clave, "correo": "sc@prueba.co"}, headers=cabecera).status_code == 422
    assert "clave_hash" not in cliente.get("/api/usuarios", headers=cabecera).text


def test_auditoria_registra_acciones(cliente, entrar):
    cabecera = entrar("administrador")
    cliente.post("/api/sedes", json={"nombre": "Sede Nueva", "vereda": "Cerca"}, headers=cabecera)
    cliente.delete("/api/sedes/2", headers=cabecera)
    registros = cliente.get("/api/auditoria", headers=cabecera).json()["items"]
    assert [r["accion"] for r in registros][:2] == ["eliminar", "crear"]
    assert cliente.get("/api/auditoria", headers=entrar("operador")).status_code == 403


def test_encabezados_de_seguridad(cliente):
    respuesta = cliente.get("/")
    assert respuesta.headers["X-Content-Type-Options"] == "nosniff"
    assert "default-src 'self'" in respuesta.headers["Content-Security-Policy"]


def test_filtro_numerico_invalido_responde_422(cliente, entrar):
    respuesta = cliente.get("/api/citas", params={"paciente_id": "abc"}, headers=entrar("operador"))
    assert respuesta.status_code == 422
    assert "paciente_id" in respuesta.text


def test_filtro_numerico_valido_funciona(cliente, entrar):
    respuesta = cliente.get("/api/citas", params={"paciente_id": "1"}, headers=entrar("operador"))
    assert respuesta.status_code == 200


def test_error_de_validacion_en_espanol(cliente, entrar):
    respuesta = cliente.post("/api/sedes", json={"vereda": "Fagua"}, headers=entrar("administrador"))
    assert respuesta.status_code == 422
    detalle = respuesta.json()["detail"]
    assert any(e["msg"] == "Campo obligatorio" and "nombre" in e["loc"] for e in detalle)
