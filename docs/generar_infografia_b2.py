import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

DESTINO = Path(__file__).resolve().parent / "figuras"
VERDE, AZUL, ROJO, GRIS = "#0b6e4f", "#1d4e89", "#b42318", "#3d4852"

LOCALES = [
    ("Cartagena, 2013", "Medina y Arrieta", "Urgencias de un hospital", "Simulación de eventos discretos",
     "Identifica el recurso restrictivo de urgencias y propone optimizar los recursos de atención."),
    ("Bogotá, 2017", "Hernández Chinchilla et al.", "Urgencias del Hospital La Samaritana", "Simulación discreta del flujo de pacientes",
     "Analiza el flujo de pacientes y plantea escenarios para mejorar la atención."),
    ("Bogotá, 2022", "Aguiar et al.", "Sistema de emergencias médicas", "Simulación más algoritmos genéticos",
     "Estima cuántas ambulancias se necesitan para responder a tiempo."),
]
GLOBALES = [
    ("Singapur y Chengdu, 2021", "Xie et al.", "Dos hospitales grandes", "Análisis con datos reales y simulación",
     "Planeación de camas y recursos de diagnóstico con datos de dos hospitales."),
    ("Italia, 2023", "Dosi et al.", "Urgencias de un hospital", "Simulación validada por los gestores",
     "Un escenario validado por los gestores fue implementado por el servicio."),
    ("Alemania, 2021", "Comis et al.", "Atención primaria regional", "Modelo de agentes con datos empíricos",
     "Evalúa políticas de atención primaria con un modelo de agentes."),
]
RELACIONES = [
    "Los seis casos usan la simulación para decidir recursos (camas, personal, ambulancias, citas) antes de aplicar una medida.",
    "Los casos locales se concentran en urgencias y emergencias en ciudades; ninguno modela un puesto de salud rural, que es el hueco que cubre este proyecto.",
    "Los casos globales validan con datos reales o llevan la decisión hasta la implementación: una práctica que este proyecto replica con la exportación del CRUD.",
]


def tarjeta(eje, x, y, ancho, alto, datos, color):
    lugar, autores, servicio, metodo, hallazgo = datos
    eje.add_patch(FancyBboxPatch((x, y), ancho, alto, boxstyle="round,pad=0.4,rounding_size=1.2", fc="white", ec=color, lw=1.6))
    eje.text(x + 1.5, y + alto - 2.2, lugar, fontsize=8.6, fontweight="bold", color=color, va="center")
    eje.text(x + 1.5, y + alto - 5.2, autores, fontsize=6.8, color=GRIS, va="center", style="italic")
    cuerpo = f"Servicio: {servicio}\nMétodo: {metodo}\nHallazgo: {hallazgo}"
    envuelto = "\n".join("\n".join(textwrap.wrap(linea, 58)) for linea in cuerpo.split("\n"))
    eje.text(x + 1.5, y + alto - 8, envuelto, fontsize=7.6, va="top", color="#1f2933", linespacing=1.4)


def generar():
    DESTINO.mkdir(exist_ok=True)
    figura = plt.figure(figsize=(8.5, 11))
    eje = figura.add_axes([0, 0, 1, 1])
    eje.set_xlim(0, 100)
    eje.set_ylim(0, 129.4)
    eje.axis("off")
    eje.add_patch(FancyBboxPatch((0, 117), 100, 12.4, boxstyle="square,pad=0", fc=VERDE, ec=VERDE))
    eje.text(50, 124.6, "Simulación para decidir en salud: casos locales y globales", color="white", fontsize=14.5, fontweight="bold", ha="center")
    eje.text(50, 120.4, "Mapa comparativo para la gestión de turnos en un puesto de salud rural", color="white", fontsize=9.5, ha="center")
    eje.text(25, 113.6, "CASOS LOCALES (COLOMBIA)", fontsize=10.5, fontweight="bold", color=AZUL, ha="center")
    eje.text(75, 113.6, "CASOS GLOBALES", fontsize=10.5, fontweight="bold", color=ROJO, ha="center")
    alto, paso = 24, 28
    for i, (local, mundial) in enumerate(zip(LOCALES, GLOBALES)):
        y = 85 - i * paso
        tarjeta(eje, 2, y, 46, alto, local, AZUL)
        tarjeta(eje, 52, y, 46, alto, mundial, ROJO)
    eje.add_patch(FancyBboxPatch((2, 4), 96, 22.5, boxstyle="round,pad=0.4,rounding_size=1.2", fc="#eef6f2", ec=VERDE, lw=1.6))
    eje.text(4, 24, "Relaciones críticas y lecciones para el proyecto", fontsize=9.6, fontweight="bold", color=VERDE, va="center")
    texto = "\n".join("• " + "\n   ".join(textwrap.wrap(r, 118)) for r in RELACIONES)
    eje.text(4, 21.4, texto, fontsize=7.3, va="top", linespacing=1.5, color="#1f2933")
    eje.text(50, 1.6, "Fuentes: artículos arbitrados listados en el documento del módulo B2 (APA 7). Elaboración propia.", fontsize=6.2, ha="center", color=GRIS)
    figura.savefig(DESTINO / "infografia_b2.png", dpi=200)
    figura.savefig(DESTINO / "infografia_b2.pdf")
    plt.close(figura)


if __name__ == "__main__":
    generar()
