from datetime import datetime

import pytest

from app import seguridad
from app.negocio import reportes, tablero, turnos


def fila(servicio, profesional, llegada, espera, atencion):
    return {
        "servicio": servicio,
        "profesional": profesional,
        "llegada": llegada,
        "espera_min": espera,
        "atencion_min": atencion,
    }


FILAS = [
    fila("Medicina", "A", datetime(2024, 3, 4, 8), 10, 20),
    fila("Medicina", "A", datetime(2024, 3, 4, 9), 30, 20),
    fila("Odontología", "B", datetime(2024, 3, 5, 8), 50, 30),
]


def test_hash_con_sal_distinta_y_verificacion():
    primero = seguridad.hashear_clave("Secreta123")
    segundo = seguridad.hashear_clave("Secreta123")
    assert primero != segundo
    assert seguridad.verificar_clave("Secreta123", primero)
    assert not seguridad.verificar_clave("Otra123456", primero)


def test_token_ida_y_vuelta():
    datos = seguridad.leer_token(seguridad.crear_token(7, "operador"))
    assert datos["sub"] == "7" and datos["rol"] == "operador"


def test_tiempos_por_servicio():
    resultado = reportes.tiempos_por_servicio(FILAS)
    medicina = next(r for r in resultado if r["servicio"] == "Medicina")
    assert medicina["citas"] == 2 and medicina["espera_media_min"] == 20


def test_ocupacion_por_profesional():
    resultado = reportes.ocupacion_por_profesional(FILAS)
    medico_a = next(r for r in resultado if r["profesional"] == "A")
    assert medico_a["minutos_atendidos"] == 40
    assert medico_a["minutos_disponibles"] == 2 * reportes.MINUTOS_JORNADA


def test_volumen_por_dia_y_por_mes():
    assert reportes.volumen_por_periodo(FILAS) == [
        {"periodo": "2024-03-04", "citas": 2},
        {"periodo": "2024-03-05", "citas": 1},
    ]
    assert reportes.volumen_por_periodo(FILAS, "mes") == [{"periodo": "2024-03", "citas": 3}]


def test_exportacion_csv():
    texto = reportes.a_csv(reportes.volumen_por_periodo(FILAS))
    assert texto.splitlines()[0] == "periodo,citas"
    assert reportes.a_csv([]) == ""


def test_alertas_de_capacidad_segun_umbral():
    alertas = turnos.alertas_capacidad(FILAS, umbral=30)
    assert [a["servicio"] for a in alertas] == ["Odontología"]


def test_indicadores_reales():
    indicadores = tablero.indicadores_reales(FILAS)
    assert indicadores["citas_atendidas"] == 3
    assert indicadores["espera_media_min"] == pytest.approx(30)


def test_proyectados_sin_resultados():
    assert tablero.proyectados(None) is None


def test_proyectados_con_recomendado():
    resultados = {"escenarios": {"base": {"espera": 1}, "mejor": {"espera": 0.5}}, "recomendado": "mejor"}
    proyectado = tablero.proyectados(resultados)
    assert proyectado["recomendado"] == {"nombre": "mejor", "espera": 0.5}


def test_cola_prioriza_y_sugerencia_de_profesional(cliente, entrar, cita_valida):
    cabecera = entrar("operador")
    normal = {**cita_valida, "estado": "programada", "inicio_atencion": None, "fin_atencion": None, "llegada": "2024-03-04T08:00:00"}
    prioritaria = {**normal, "prioridad": "prioritaria", "llegada": "2024-03-04T09:00:00"}
    cliente.post("/api/citas", json=normal, headers=cabecera)
    cliente.post("/api/citas", json=prioritaria, headers=cabecera)
    cola = cliente.get("/api/citas/cola?sede_id=1", headers=cabecera).json()
    assert [c["prioridad"] for c in cola] == ["prioritaria", "normal"]
    sugerido = cliente.get("/api/citas/profesional-sugerido?sede_id=1&servicio_id=1", headers=cabecera)
    assert sugerido.json()["id"] == 1
    assert cliente.get("/api/citas/profesional-sugerido?sede_id=1&servicio_id=2", headers=cabecera).status_code == 404


def test_reportes_y_exportacion_por_api(cliente, entrar, cita_valida):
    cabecera = entrar("operador")
    cliente.post("/api/citas", json=cita_valida, headers=cabecera)
    assert cliente.get("/api/reportes/tiempos", headers=cabecera).json()[0]["citas"] == 1
    assert cliente.get("/api/reportes/ocupacion?formato=csv", headers=cabecera).text.startswith("profesional,")
    assert cliente.get("/api/reportes/volumen?periodo=mes", headers=cabecera).json()[0]["periodo"] == "2024-03"
    assert cliente.get("/api/reportes/inexistente", headers=cabecera).status_code == 404
    assert cliente.get("/api/reportes/tiempos?desde=ayer", headers=cabecera).status_code == 422
    assert "espera_min" in cliente.get("/api/exportar/citas.csv", headers=cabecera).text
    assert cliente.get("/api/exportar/citas.csv", headers=entrar("consulta")).status_code == 403


def test_tablero_y_alertas(cliente, entrar, cita_valida, umbral):
    from app import config

    config.UMBRAL_ESPERA_MIN = 5
    cabecera = entrar("consulta")
    cliente.post("/api/citas", json=cita_valida, headers=entrar("operador"))
    datos = cliente.get("/api/tablero", headers=cabecera).json()
    assert datos["reales"]["citas_atendidas"] == 1
    assert datos["alertas"][0]["servicio"] == "Medicina general"
    assert cliente.get("/api/alertas/capacidad", headers=cabecera).json()
