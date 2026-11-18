import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

DESTINO = Path(__file__).resolve().parent / "figuras"
VERDE, AZUL, ROJO, GRIS = "#0b6e4f", "#1d4e89", "#b42318", "#3d4852"

LOCALES = [
    ("Cartagena, 2013", "Medina y Arrieta", "Urgencias de un hospital", "Eventos discretos y teoría de colas",
     "El triage operaba al 99 % de ocupación y la espera era de 82 min; se propone un servidor adicional."),
    ("Bogotá, 2017", "Hernández, Camacho y Duarte", "Urgencias del Hospital La Samaritana", "Simulación discreta y segmentación de pacientes",
     "Escenarios y estrategias para reducir la estancia, según días de estadía y patología."),
    ("Hospital público colombiano, 2014", "Gáfaro-Rojas, Mallor-Giménez y Azcárate-Camio", "Consulta externa", "Modelo de simulación de llegadas",
     "Modelo de llegadas reutilizable en contextos similares para planear la gestión."),
]
GLOBALES = [
    ("Arkansas, EE. UU., 2015", "Lenin et al.", "Clínica de ginecología y obstetricia", "Eventos discretos validados con datos reales",
     "Citas cada 16 y 19 min y un auxiliar más: espera por proveedor 39,8 % menor."),
    ("Vacunación COVID-19, 2022", "Hanly et al.", "Centros masivos y consultorios", "Redes de colas estocásticas",
     "500 a 1400 dosis diarias en centros y 100 a 300 en consultorios; más personal da más robustez."),
    ("Clínica de vacunación, 2023", "Adacher, Flamini y Naldi", "Clínica con citas programadas", "Simulador de capacidad y personal",
     "Diseña la capacidad y el personal antes de operar, en vez de dotarlos sin análisis."),
]
RELACIONES = [
    "Todos usan simulación para decidir recursos (personal, citas, servidores) antes de gastar, igual que este proyecto con la fila única y la prioridad.",
    "Los casos locales se concentran en urgencias y hospitales urbanos; ninguno de los reseñados modela un puesto de salud rural, que es el hueco que cubre este trabajo.",
    "Los casos globales validan con datos propios (Lenin) o entregan una herramienta abierta (Hanly): una práctica que este proyecto replica con la exportación del CRUD.",
    "Una revisión de 211 estudios halló que más del 68 % de las aplicaciones atienden unidades individuales (Zhang, 2018): faltan modelos de servicios integrados.",
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
