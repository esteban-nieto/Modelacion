import json
from pathlib import Path

from app import config
from app.negocio.reportes import ocupacion_por_profesional, promedio


def indicadores_reales(filas):
    ocupaciones = [o["ocupacion_pct"] for o in ocupacion_por_profesional(filas)]
    return {
        "citas_atendidas": len(filas),
        "espera_media_min": promedio([f["espera_min"] for f in filas]),
        "atencion_media_min": promedio([f["atencion_min"] for f in filas]),
        "ocupacion_media_pct": promedio(ocupaciones),
    }


def resultados_simulacion():
    ruta = Path(config.RESULTADOS_SIMULACION)
    if not ruta.exists():
        return None
    return json.loads(ruta.read_text(encoding="utf-8"))


def proyectados(resultados):
    if not resultados:
        return None
    escenarios = resultados["escenarios"]
    return {
        "base": escenarios["base"],
        "recomendado": {"nombre": resultados["recomendado"], **escenarios[resultados["recomendado"]]},
    }
