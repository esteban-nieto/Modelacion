"""Calibra los parámetros del modelo Vensim con los datos exportados del CRUD.

Protocolo (evita validar con los mismos datos que se usaron para calibrar):
  1. Calibración: primeros 30 días del CRUD. Se toman la duración de atención, los
     profesionales y una tasa de llegadas inicial (pacientes/hora de jornada de 9 h).
  2. Ajuste: el modelo incluye un efecto de confianza que aumenta las llegadas durante la
     simulación. La tasa se corrige una vez para que el modelo reproduzca el volumen de
     calibración.
  3. Validación: últimos 30 días, que no se usan para calibrar.

Escribe diagramas/calibracion_vensim.json. diagramas/definicion.py lo usa para reemplazar
los valores fijos, y generar_vensim.py regenera el .mdl.

Uso: python diagramas/calibrar_vensim.py
"""

import json
from pathlib import Path

import pandas as pd

CARPETA = Path(__file__).resolve().parent
DATOS = CARPETA.parent / "simulacion" / "datos" / "citas_historicas.csv"
SALIDA = CARPETA / "calibracion_vensim.json"
JORNADA_H = 9  # 540 min, igual que simulacion/modelo.py


def atendidas_por_dia(citas):
    return len(citas) / citas["llegada"].dt.date.nunique()


def calibrar():
    import correr_vensim  # import local: pysd solo se carga al calibrar

    citas = pd.read_csv(DATOS, parse_dates=["llegada"])
    fechas = sorted(citas["llegada"].dt.date.unique())
    mitad = len(fechas) // 2
    calibracion = citas[citas["llegada"].dt.date.isin(fechas[:mitad])]
    validacion = citas[citas["llegada"].dt.date.isin(fechas[mitad:])]

    tasa_inicial = atendidas_por_dia(calibracion) / JORNADA_H
    simulado = correr_vensim.correr({"Tasa base de llegadas": tasa_inicial})["Atendidos"].iloc[-1]
    tasa = tasa_inicial * atendidas_por_dia(calibracion) / simulado

    resultado = {
        "fuente": "simulacion/datos/citas_historicas.csv",
        "protocolo": "calibracion: primeros 30 dias; validacion: ultimos 30 dias",
        "citas": int(len(citas)),
        "dias_calibracion": int(mitad),
        "dias_validacion": int(len(fechas) - mitad),
        "Tasa base de llegadas": round(tasa, 3),  # pacientes/hora, incluye el efecto de confianza
        "Duracion de atencion": round(calibracion["atencion_min"].mean() / 60, 4),  # horas
        "Profesionales": int(calibracion["profesional"].nunique()),
        "atendidas_por_dia": round(atendidas_por_dia(calibracion), 2),
        "atendidas_por_dia_validacion": round(atendidas_por_dia(validacion), 2),
        "espera_media_real_min": round(validacion["espera_min"].mean(), 2),
    }
    SALIDA.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    return resultado


if __name__ == "__main__":
    print(json.dumps(calibrar(), indent=2, ensure_ascii=False))
