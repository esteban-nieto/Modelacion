import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon

from definicion import AUXILIARES, CAUSAL, CONSTANTES, FLUJOS, NIVELES
from generar_vensim import nombres_en

SALIDA = Path(__file__).resolve().parent / "png"
VERDE, ROJO, GRIS, AZUL = "#0b6e4f", "#b42318", "#616e7c", "#1d4e89"


def lienzo(ancho, alto, titulo):
    figura, eje = plt.subplots(figsize=(ancho, alto))
    eje.set_aspect("equal")
    eje.axis("off")
    eje.set_title(titulo, fontsize=13, fontweight="bold")
    return figura, eje


def envolver(texto, ancho=18):
    return "\n".join(textwrap.wrap(texto, ancho))


def caja(eje, x, y, texto, ancho=150, alto=60, color="#ffffff", borde=GRIS, tam=9, ancho_texto=20):
    eje.add_patch(FancyBboxPatch((x - ancho / 2, y - alto / 2), ancho, alto, boxstyle="round,pad=4", fc=color, ec=borde, lw=1.5))
    eje.text(x, y, envolver(texto, ancho_texto), ha="center", va="center", fontsize=tam)


def flecha(eje, origen, destino, color=GRIS, curva=0.0, estilo="-|>", ancho=1.5):
    eje.add_patch(
        FancyArrowPatch(origen, destino, arrowstyle=estilo, mutation_scale=14, color=color, lw=ancho, connectionstyle=f"arc3,rad={curva}", shrinkA=0, shrinkB=0)
    )


def recorte(origen, destino, medio_ancho, medio_alto):
    dx, dy = destino[0] - origen[0], destino[1] - origen[1]
    escala = min(medio_ancho / abs(dx) if dx else 1e9, medio_alto / abs(dy) if dy else 1e9)
    return (origen[0] + dx * escala, origen[1] + dy * escala)


def figura_causal():
    figura, eje = lienzo(12, 8, "Diagrama causal del proceso de turnos")
    posiciones = CAUSAL["variables"]
    for nombre, (x, y) in posiciones.items():
        caja(eje, x, y, nombre, ancho=130, alto=46, color="#eef6f2", borde=VERDE)
    for origen, destino, signo in CAUSAL["enlaces"]:
        a, b = posiciones[origen], posiciones[destino]
        inicio, fin = recorte(a, b, 72, 28), recorte(b, a, 72, 28)
        curva = 0.25 if (destino, origen, "+") in CAUSAL["enlaces"] or (destino, origen, "-") in CAUSAL["enlaces"] else 0.0
        color = VERDE if signo == "+" else ROJO
        flecha(eje, inicio, fin, color=color, curva=curva)
        medio = ((inicio[0] + fin[0]) / 2, (inicio[1] + fin[1]) / 2)
        desplazamiento = 18 if curva else 8
        eje.text(medio[0] + desplazamiento, medio[1] + desplazamiento, signo, color=color, fontsize=16, fontweight="bold", ha="center", va="center")
    marcas = {"R1": (160, 325), "B1": (520, 325), "B2": (400, 325), "B3": (400, 190)}
    for etiqueta, nombre, _ in CAUSAL["bucles"]:
        x, y = marcas[etiqueta]
        eje.text(x, y, etiqueta, ha="center", va="center", fontsize=11, fontweight="bold", color=AZUL, bbox={"boxstyle": "circle", "fc": "white", "ec": AZUL})
    leyenda = "\n".join(f"{e}: {'Refuerzo' if e.startswith('R') else 'Balanceo'} - {n}" for e, n, _ in CAUSAL["bucles"])
    eje.text(80, 560, leyenda, fontsize=9, va="top", color=AZUL)
    eje.set_xlim(40, 760)
    eje.set_ylim(570, 40)
    figura.tight_layout()
    figura.savefig(SALIDA / "diagrama_causal.png", dpi=150)
    plt.close(figura)


def figura_flujos_niveles():
    figura, eje = lienzo(14, 8, "Diagrama de flujos y niveles")
    ubicacion = {n: (d["x"], d["y"]) for n, d in {**NIVELES, **AUXILIARES, **CONSTANTES}.items()}
    for nombre, n in NIVELES.items():
        caja(eje, n["x"], n["y"], nombre, ancho=110, alto=40, color="#e8f0fb", borde=AZUL, tam=9)
    for nombre, f in FLUJOS.items():
        desde = ubicacion.get(f["desde"], f.get("nube"))
        hacia = ubicacion.get(f["hacia"], f.get("nube"))
        inicio = recorte(desde, (f["x"], f["y"]), 55, 20) if f["desde"] else desde
        fin = recorte(hacia, (f["x"], f["y"]), 55, 20) if f["hacia"] else hacia
        flecha(eje, inicio, (f["x"], f["y"]), color=AZUL, ancho=3, estilo="-")
        flecha(eje, (f["x"], f["y"]), fin, color=AZUL, ancho=3)
        eje.plot(f["x"], f["y"], marker="D", color=AZUL)
        eje.text(f["x"], f["y"] + 22, nombre, ha="center", fontsize=8.5, color=AZUL)
        if f.get("nube"):
            eje.text(*f["nube"], "nube", ha="center", va="center", fontsize=8, color=GRIS, bbox={"boxstyle": "round", "fc": "#f4f6f8", "ec": GRIS})
    for nombre, a in {**AUXILIARES, **CONSTANTES}.items():
        eje.text(a["x"], a["y"], envolver(nombre, 16), ha="center", va="center", fontsize=8, color=VERDE if nombre in AUXILIARES else GRIS)
    ubicacion.update({n: (f["x"], f["y"]) for n, f in FLUJOS.items()})
    for nombre, definicion in list(FLUJOS.items()) + list(AUXILIARES.items()):
        destino = ubicacion[nombre]
        for dependencia in nombres_en(definicion["ecuacion"], list(ubicacion)):
            origen = ubicacion[dependencia]
            inicio, fin = recorte(origen, destino, 45, 14), recorte(destino, origen, 12, 12)
            flecha(eje, inicio, fin, color="#9aa5b1", ancho=0.8)
    eje.set_xlim(60, 980)
    eje.set_ylim(590, 0)
    figura.tight_layout()
    figura.savefig(SALIDA / "diagrama_flujos_niveles.png", dpi=150)
    plt.close(figura)


def rombo(eje, x, y, texto, ancho=170, alto=80):
    eje.add_patch(Polygon([(x, y - alto / 2), (x + ancho / 2, y), (x, y + alto / 2), (x - ancho / 2, y)], fc="#fff7e6", ec="#b7791f", lw=1.5))
    eje.text(x, y, envolver(texto, 18), ha="center", va="center", fontsize=8.5)


def figura_flujo_proceso():
    figura, eje = lienzo(13, 7.5, "Diagrama de flujo del proceso de atención en el puesto de salud")
    pasos = {
        "inicio": (110, 120, "Llega el paciente al puesto"),
        "registro": (330, 120, "Registro en el sistema y asignación de turno"),
        "prioridad": (570, 120, None),
        "libre": (820, 120, None),
        "fila": (820, 300, "Espera en la fila del servicio"),
        "consulta": (570, 300, "Consulta con el profesional"),
        "otro": (330, 300, None),
        "cierre": (110, 300, "Registro del tiempo de atención y salida"),
        "abandono": (820, 470, "El paciente se retira sin atención"),
    }
    for clave, (x, y, texto) in pasos.items():
        if texto:
            caja(eje, x, y, texto, ancho=150, alto=56, color="#eef6f2", borde=VERDE)
    rombo(eje, 570, 120, "¿Es paciente prioritario?")
    rombo(eje, 820, 120, "¿Hay profesional libre?")
    rombo(eje, 330, 300, "¿Necesita otro servicio?")
    flecha(eje, (185, 120), (255, 120))
    flecha(eje, (405, 120), (485, 120))
    # Rama Sí: el prioritario se ubica al frente de la fila y luego se atiende
    flecha(eje, (570, 80), (570, 66), color=VERDE)
    caja(eje, 570, 38, "Se ubica al frente de la fila", ancho=170, alto=44, color="#eef6f2", borde=VERDE)
    flecha(eje, (655, 38), (820, 80), color=VERDE)
    eje.text(700, 24, "Sí", fontsize=9, color=VERDE)
    # Rama No: el resto se ubica al final de la fila
    flecha(eje, (570, 160), (570, 183), color=ROJO)
    eje.text(580, 172, "No", fontsize=9, color=ROJO)
    caja(eje, 570, 205, "Se ubica al final de la fila", ancho=170, alto=44, color="#eef6f2", borde=VERDE)
    flecha(eje, (655, 205), (745, 300), color=ROJO)
    flecha(eje, (820, 160), (820, 272))
    eje.text(830, 215, "No", fontsize=9, color=ROJO)
    flecha(eje, (820, 328), (820, 440), color=ROJO)
    eje.text(830, 385, "Espera excesiva", fontsize=8, color=ROJO)
    flecha(eje, (745, 300), (645, 300))
    flecha(eje, (495, 300), (415, 300))
    flecha(eje, (245, 300), (185, 300))
    eje.text(215, 285, "No", fontsize=9, color=VERDE)
    flecha(eje, (330, 260), (330, 175), curva=0.0)
    eje.text(342, 215, "Sí: nuevo turno", fontsize=8, color=VERDE)
    flecha(eje, (790, 155), (600, 272), color=VERDE, curva=0.2)
    eje.text(640, 200, "Sí: atiende de inmediato", fontsize=8, color=VERDE)
    eje.set_xlim(20, 920)
    eje.set_ylim(510, 0)
    figura.tight_layout()
    figura.savefig(SALIDA / "diagrama_flujo_proceso.png", dpi=150)
    plt.close(figura)


def figura_arbol_problemas():
    figura, eje = lienzo(13, 8.5, "Árbol de problemas: bajo aprovechamiento tecnológico en el puesto de salud rural")
    efectos = [
        "Esperas largas e impredecibles",
        "Abandono de la consulta",
        "Saturación y subuso alternados de profesionales",
        "Pérdida de confianza comunitaria",
        "Decisiones sin evidencia cuantitativa",
    ]
    causas = [
        "Sin registro digital de llegadas y atenciones",
        "Conectividad limitada en la vereda",
        "Baja alfabetización digital de usuarios y personal",
        "Turnos asignados sin reglas de prioridad",
        "Sin indicadores ni simulación para decidir",
    ]
    centro = (500, 300)
    caja(eje, *centro, "Bajo aprovechamiento de tecnologías electrónicas en la gestión de turnos del puesto de salud rural", ancho=330, alto=90, color="#fdecea", borde=ROJO, tam=10, ancho_texto=40)
    for i, texto in enumerate(efectos):
        x = 110 + i * 195
        caja(eje, x, 110, texto, ancho=170, alto=70, color="#e8f0fb", borde=AZUL, ancho_texto=22)
        flecha(eje, (500, 252), (x, 150), color=AZUL)
    for i, texto in enumerate(causas):
        x = 110 + i * 195
        caja(eje, x, 490, texto, ancho=170, alto=70, color="#eef6f2", borde=VERDE, ancho_texto=22)
        flecha(eje, (x, 452), (500, 348), color=VERDE)
    eje.text(20, 60, "EFECTOS", fontsize=10, fontweight="bold", color=AZUL)
    eje.text(20, 545, "CAUSAS", fontsize=10, fontweight="bold", color=VERDE)
    eje.set_xlim(0, 1000)
    eje.set_ylim(570, 30)
    figura.tight_layout()
    figura.savefig(SALIDA / "arbol_problemas.png", dpi=150)
    plt.close(figura)


def generar():
    SALIDA.mkdir(exist_ok=True)
    figura_causal()
    figura_flujos_niveles()
    figura_flujo_proceso()
    figura_arbol_problemas()


if __name__ == "__main__":
    generar()
