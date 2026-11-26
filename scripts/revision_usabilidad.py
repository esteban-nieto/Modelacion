"""Revisión de usabilidad SIMULADA (recorrido automatizado por perfiles).

No sustituye a usuarios reales: la guía pide 5 usuarios "reales o simulados". Cada perfil
recorre las seis tareas de docs/encuesta_usabilidad.md contra la API real, con el rol que
tendría en el puesto. El resultado es lo que responde el sistema, no la opinión de una persona.
Los hallazgos de la fila "Usuario" de la tabla deben complementarse con pruebas con personas reales.

Uso: python scripts/revision_usabilidad.py   (requiere la base sembrada, ver README)
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

SALIDA = RAIZ / "docs" / "usabilidad_simulada.json"
CLAVES = {"administrador": "Admin12345", "operador": "Operador12345", "consulta": "Consulta12345"}
CORREOS = {"administrador": "administrador@saludrural.co", "operador": "operador@saludrural.co", "consulta": "consulta@saludrural.co"}

# Perfiles simulados: rol, nivel técnico (1-5 de la encuesta) y si comete un error de captura.
PERFILES = [
    {"id": "U1", "rol": "administrador", "tecnica": 5, "error_captura": False},
    {"id": "U2", "rol": "operador", "tecnica": 4, "error_captura": False},
    {"id": "U3", "rol": "consulta", "tecnica": 2, "error_captura": False},
    {"id": "U4", "rol": "consulta", "tecnica": 3, "error_captura": False},
    {"id": "U5", "rol": "operador", "tecnica": 1, "error_captura": True},
]


def tarea(nombre, respuesta, esperado=200):
    ok = respuesta.status_code == esperado
    if ok:
        resultado = "completada"
    elif respuesta.status_code == 403:
        resultado = "bloqueado por rol"  # diseño de permisos: no es un fallo de usabilidad
    else:
        resultado = "no pudo"
    mensaje = "" if ok else respuesta.text[:160]
    return {"tarea": nombre, "codigo": respuesta.status_code, "resultado": resultado, "mensaje": mensaje}


def recorrer(cliente, perfil):
    rol = perfil["rol"]
    resultados = []
    login = cliente.post("/api/auth/login", json={"correo": CORREOS[rol], "clave": CLAVES[rol]})
    resultados.append(tarea("Iniciar sesión", login))
    if login.status_code != 200:
        return resultados
    cabecera = {"Authorization": f"Bearer {login.json()['token']}"}

    paciente = cliente.get("/api/pacientes", params={"busqueda": "", "pagina": 1, "tamano": 1}, headers=cabecera)
    documento = paciente.json()["items"][0]["documento"] if paciente.status_code == 200 and paciente.json()["items"] else ""
    resultados.append(tarea("Buscar paciente por documento", cliente.get("/api/pacientes", params={"busqueda": documento}, headers=cabecera)))

    if perfil["error_captura"]:
        # Captura con tiempos invertidos: el sistema debe rechazarla con un mensaje claro.
        malo = {"paciente_id": 1, "profesional_id": 1, "servicio_id": 1, "sede_id": 1,
                "llegada": "2024-03-04T08:00:00", "inicio_atencion": "2024-03-04T07:00:00", "fin_atencion": "2024-03-04T07:30:00", "estado": "atendida"}
        rechazo = cliente.post("/api/citas", json=malo, headers=cabecera)
        # Un rechazo 422 con mensaje legible cuenta como "con ayuda": el usuario entiende qué corregir.
        resultados.append({"tarea": "Registrar cita (captura con error)", "codigo": rechazo.status_code,
                           "resultado": "con ayuda" if rechazo.status_code == 422 else "no pudo", "mensaje": rechazo.text[:160]})
    else:
        cita = {"paciente_id": 1, "profesional_id": 1, "servicio_id": 1, "sede_id": 1,
                "llegada": "2024-03-04T08:00:00", "inicio_atencion": "2024-03-04T08:10:00", "fin_atencion": "2024-03-04T08:30:00", "estado": "atendida"}
        resultados.append(tarea("Registrar una cita nueva", cliente.post("/api/citas", json=cita, headers=cabecera), esperado=201))

    sede = cliente.get("/api/sedes", params={"pagina": 1, "tamano": 1}, headers=cabecera).json()["items"][0]["id"]
    resultados.append(tarea("Ver la cola de atención", cliente.get("/api/citas/cola", params={"sede_id": sede}, headers=cabecera)))
    resultados.append(tarea("Descargar un reporte en CSV", cliente.get("/api/reportes/tiempos", params={"formato": "csv"}, headers=cabecera)))
    resultados.append(tarea("Interpretar el tablero real vs. simulado", cliente.get("/api/tablero", headers=cabecera)))
    return resultados


def ejecutar():
    cliente = TestClient(app)
    reporte = []
    for perfil in PERFILES:
        reporte.append({"perfil": perfil, "tareas": recorrer(cliente, perfil)})
    resumen = {"simulado": True, "nota": "Recorrido automatizado por perfiles; no reemplaza pruebas con usuarios reales.", "usuarios": reporte}
    SALIDA.write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    for u in reporte:
        fallos = [t["tarea"] for t in u["tareas"] if t["resultado"] != "completada"]
        print(u["perfil"]["id"], u["perfil"]["rol"], "tareas:", len(u["tareas"]), "no completadas:", fallos)


if __name__ == "__main__":
    ejecutar()
