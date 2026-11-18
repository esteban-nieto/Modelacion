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
}
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


if __name__ == "__main__":
    tabla = resumen()
    tabla.to_csv(CARPETA / "resultados_vensim.csv", index=False)
    print(tabla.to_string(index=False))
