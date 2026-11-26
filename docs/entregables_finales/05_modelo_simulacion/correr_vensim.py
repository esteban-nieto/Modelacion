import json
from pathlib import Path

import pandas as pd
import pysd

CARPETA = Path(__file__).resolve().parent
MODELO = CARPETA / "turnos_flujos_niveles.mdl"
ESCENARIOS = {
    "Base": {},
    "Demanda +25 %": {"Factor de demanda": 1.25},
    "Un profesional adicional": {"Profesionales": 5},
    "Demanda +25 % y un profesional adicional": {"Factor de demanda": 1.25, "Profesionales": 5},
    "Demanda +80 % (saturacion)": {"Factor de demanda": 1.8},
}
CALIBRACION = CARPETA / "calibracion_vensim.json"
COLUMNAS = ["Cola de espera", "En atencion", "Atendidos", "Abandonos acumulados", "Confianza comunitaria"]


def correr(parametros):
    modelo = pysd.read_vensim(str(MODELO))
    return modelo.run(params=parametros, return_columns=COLUMNAS + ["Tiempo de espera estimado"])


def resumen():
    filas = []
    for nombre, parametros in ESCENARIOS.items():
        trayectoria = correr(parametros)
        filas.append(
            {
                "escenario": nombre,
                "atendidos": round(trayectoria["Atendidos"].iloc[-1], 1),
                "abandonos": round(trayectoria["Abandonos acumulados"].iloc[-1], 2),
                "cola_maxima": round(trayectoria["Cola de espera"].max(), 2),
                "espera_maxima_min": round(60 * trayectoria["Tiempo de espera estimado"].max(), 1),
                "confianza_final": round(trayectoria["Confianza comunitaria"].iloc[-1], 3),
            }
        )
    return pd.DataFrame(filas)


def validar():
    """Compara los pacientes atendidos por día del modelo base con los datos reales del CRUD."""
    real = json.loads(CALIBRACION.read_text(encoding="utf-8"))["atendidas_por_dia_validacion"]  # días no usados para calibrar
    simulado = correr({})["Atendidos"].iloc[-1]
    error = 100 * (simulado - real) / real
    return {
        "atendidas_por_dia_real": real,
        "atendidas_por_dia_vensim": round(float(simulado), 2),
        "error_relativo_pct": round(float(error), 2),
        "conclusion": "Diferencia menor al 5 %: el modelo reproduce el volumen real" if abs(error) < 5 else "Diferencia mayor al 5 %: revisar supuestos",
    }


if __name__ == "__main__":
    tabla = resumen()
    tabla.to_csv(CARPETA / "resultados_vensim.csv", index=False)
    print(tabla.to_string(index=False))
    validacion = validar()
    (CARPETA / "validacion_vensim.json").write_text(json.dumps(validacion, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(validacion, indent=2, ensure_ascii=False))
