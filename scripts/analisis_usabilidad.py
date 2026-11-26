"""Respuestas SIMULADAS de la encuesta de usabilidad y su análisis estadístico.

Las cinco respuestas se derivan del recorrido automatizado de scripts/revision_usabilidad.py
(docs/usabilidad_simulada.json): cada tarea completada sin ayuda se registra como "Sin ayuda",
un error de captura resuelto con el mensaje como "Con ayuda", y un bloqueo por rol como "No pude".
La comodidad con la web, el dispositivo y la escala SUS son supuestos de perfil (semilla fija).
Son datos simulados: no reemplazan la prueba con usuarios reales.

Genera:
- docs/usabilidad/respuestas_simuladas.csv
- docs/usabilidad/analisis.json (puntaje SUS, tareas, dimensiones)
- docs/exposicion/evidencias/49_usabilidad_sus.png (gráfica para la exposición)

Uso: python scripts/analisis_usabilidad.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy import stats  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
RECORRIDO = RAIZ / "docs" / "usabilidad_simulada.json"
CARPETA = RAIZ / "docs" / "usabilidad"
EVIDENCIA = RAIZ / "docs" / "exposicion" / "evidencias"
TAREAS = ["Iniciar sesión", "Buscar paciente por documento", "Registrar una cita nueva",
          "Ver la cola de atención", "Descargar un reporte en CSV", "Interpretar el tablero real vs. simulado"]
SUS = ["Creo que me gustaría usar este sistema con frecuencia.",
       "Encontré el sistema innecesariamente complejo.",
       "Pensé que el sistema era fácil de usar.",
       "Creo que necesitaría ayuda de una persona con conocimientos técnicos para usarlo.",
       "Encontré las diferentes funciones del sistema bien integradas.",
       "Pensé que había demasiada inconsistencia en el sistema.",
       "Imagino que la mayoría de las personas aprendería a usar este sistema rápidamente.",
       "Encontré el sistema muy incómodo de usar.",
       "Me sentí muy seguro usando el sistema.",
       "Necesité aprender muchas cosas antes de poder manejar el sistema."]
# Escala SUS de cada perfil (1 = en desacuerdo, 5 = de acuerdo), según la experiencia simulada.
PERFIL_SUS = {
    "U1": [5, 1, 5, 1, 5, 1, 5, 1, 5, 1],
    "U2": [4, 2, 4, 2, 4, 2, 4, 1, 4, 2],
    "U3": [3, 2, 3, 3, 3, 2, 3, 2, 3, 3],
    "U4": [4, 2, 4, 2, 4, 2, 4, 2, 4, 2],
    "U5": [2, 3, 2, 4, 2, 3, 2, 4, 2, 4],
}
COMODIDAD = {"U1": 5, "U2": 4, "U3": 2, "U4": 3, "U5": 1}
DISPOSITIVO = {"U1": "Computador", "U2": "Computador", "U3": "Computador", "U4": "Celular", "U5": "Computador"}
ABIERTAS = {
    "U1": ("Ninguna relevante", "Mensajes de error más claros", "Sí"),
    "U2": ("Registrar la cita requiere varios clics", "Atajos de teclado", "Sí"),
    "U3": ("No sabía si el botón de registrar estaba disponible", "Ocultar acciones que el rol no puede usar", "Sí"),
    "U4": ("El tablero necesita explicación", "Textos de ayuda junto al tablero", "A veces"),
    "U5": ("Un error de fechas no se entendía", "Mostrar el campo con error", "A veces"),
}


def tabulacion_tareas(recorrido):
    filas = {}
    for u in recorrido["usuarios"]:
        uid = u["perfil"]["id"]
        for t, nombre in zip(u["tareas"], TAREAS):
            if t["resultado"] == "completada":
                valor = "Sin ayuda"
            elif t["resultado"] == "con ayuda":
                valor = "Con ayuda"
            elif t["resultado"] == "bloqueado por rol":
                valor = "No pude"  # el rol no tiene permiso; se cuenta como no completada
            else:
                valor = "No pude"
            filas.setdefault(uid, {})[nombre] = valor
    return filas


def puntaje_sus(respuestas):
    total = 0
    for i, r in enumerate(respuestas, start=1):
        total += (r - 1) if i % 2 == 1 else (5 - r)
    return total * 2.5


def construir():
    recorrido = json.loads(RECORRIDO.read_text(encoding="utf-8"))
    tareas = tabulacion_tareas(recorrido)
    filas = []
    for uid in PERFIL_SUS:
        fila = {"respuesta": uid, "perfil_rol": next(u["perfil"]["rol"] for u in recorrido["usuarios"] if u["perfil"]["id"] == uid),
                "dispositivo": DISPOSITIVO[uid], "comodidad_web_1_5": COMODIDAD[uid]}
        fila.update(tareas[uid])
        for i, pregunta in enumerate(SUS, start=1):
            fila[f"SUS{i:02d}"] = PERFIL_SUS[uid][i - 1]
        fila["abierta_dificil"], fila["abierta_mejorar"], fila["mensajes_claros"] = ABIERTAS[uid]
        fila["puntaje_sus"] = round(puntaje_sus(PERFIL_SUS[uid]), 1)
        filas.append(fila)
    return pd.DataFrame(filas)


def analizar(df):
    sus = df["puntaje_sus"].to_numpy()
    n = len(sus)
    media = float(sus.mean())
    sd = float(sus.std(ddof=1))
    ic_inf, ic_sup = stats.t.interval(0.95, n - 1, loc=media, scale=sd / np.sqrt(n))
    tareas_sin_ayuda = {t: int((df[t] == "Sin ayuda").sum()) for t in TAREAS}
    tareas_pct = {t: round(100 * v / n, 1) for t, v in tareas_sin_ayuda.items()}
    resultado = {
        "simulado": True,
        "respuestas": n,
        "puntaje_sus_media": round(media, 1),
        "puntaje_sus_desv": round(sd, 1),
        "puntaje_sus_ic95": [round(float(ic_inf), 1), round(float(ic_sup), 1)],
        "puntaje_sus_por_persona": dict(zip(df["respuesta"], df["puntaje_sus"])),
        "interpretacion_sus": "en el umbral aceptable (68)" if abs(media - 68) <= 1 else ("aceptable (> 68)" if media > 68 else "por debajo de 68"),
        "tareas_completadas_sin_ayuda_pct": tareas_pct,
        "dispositivos": df["dispositivo"].value_counts().to_dict(),
        "mensajes_claros": df["mensajes_claros"].value_counts().to_dict(),
        "hallazgos": [
            "Las tareas de administrador y operador se completan sin ayuda en el recorrido.",
            "El rol consulta no puede registrar citas (403). Es un diseño de permisos, pero el usuario no ve por qué: hallazgo de interfaz, se propone ocultar la acción.",
            "Un error de fechas en la captura se corrige con el mensaje del sistema (con ayuda); el mensaje ya fue corregido en el formulario.",
            "El tablero requiere explicación para el rol consulta: se propone un texto de ayuda junto a la gráfica.",
        ],
    }
    return resultado


def grafica(df, destino):
    fig, ejes = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1, 1.4]})
    ejes[0].bar(df["respuesta"], df["puntaje_sus"], color="#007a3d")
    ejes[0].axhline(68, color="#a33b20", ls="--", lw=1.2, label="Umbral aceptable (68)")
    ejes[0].set_title("Puntaje SUS por persona simulada", fontsize=12)
    ejes[0].set_ylim(0, 100)
    ejes[0].legend(fontsize=9, loc="lower right")
    ejes[0].grid(axis="y", alpha=0.3)
    tareas = TAREAS
    sin = [int((df[t] == "Sin ayuda").sum()) for t in tareas]
    ayuda = [int((df[t] == "Con ayuda").sum()) for t in tareas]
    no = [int((df[t] == "No pude").sum()) for t in tareas]
    y = np.arange(len(tareas))
    ejes[1].barh(y, sin, color="#007a3d", label="Sin ayuda")
    ejes[1].barh(y, ayuda, left=sin, color="#b7d7c4", label="Con ayuda")
    ejes[1].barh(y, no, left=np.array(sin) + np.array(ayuda), color="#a33b20", label="No pude")
    ejes[1].set_yticks(y)
    ejes[1].set_yticklabels(tareas, fontsize=9)
    ejes[1].set_xlim(0, len(df))
    ejes[1].set_title("Resultado por tarea (de 5 perfiles)", fontsize=12)
    ejes[1].legend(fontsize=9, loc="lower right")
    fig.tight_layout()
    fig.savefig(destino, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    CARPETA.mkdir(parents=True, exist_ok=True)
    EVIDENCIA.mkdir(parents=True, exist_ok=True)
    df = construir()
    df.to_csv(CARPETA / "respuestas_simuladas.csv", index=False, encoding="utf-8")
    res = analizar(df)
    (CARPETA / "analisis.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    grafica(df, EVIDENCIA / "49_usabilidad_sus.png")
    print(json.dumps({k: res[k] for k in ["puntaje_sus_media", "puntaje_sus_ic95", "interpretacion_sus", "tareas_completadas_sin_ayuda_pct"]}, indent=2, ensure_ascii=False))
