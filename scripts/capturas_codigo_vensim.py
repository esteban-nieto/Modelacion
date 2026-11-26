"""Genera imágenes de evidencia para la exposición (docs/exposicion/capturas/):

- Fragmentos de código renderizados a partir de los archivos reales (con número de línea).
- Trayectorias del modelo Vensim, obtenidas al ejecutar el mismo modelo con PySD.
- Resultado de las pruebas (texto de la última ejecución de pytest).

Uso: python scripts/capturas_codigo_vensim.py
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "docs" / "exposicion" / "capturas"
FUENTE = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 19)

FRAGMENTOS = {
    "10_codigo_borrado_logico.png": ("app/recursos.py", 108, 118),
    "11_codigo_hash_contrasenas.png": ("app/seguridad.py", 1, 22),
    "12_codigo_filtros_validados.png": ("app/consultas.py", 6, 19),
    "13_codigo_simulacion_paciente.png": ("simulacion/modelo.py", 66, 82),
    "14_codigo_calibracion_vensim.png": ("diagramas/calibrar_vensim.py", 28, 46),
    "15_codigo_validacion_vensim.png": ("diagramas/correr_vensim.py", 39, 52),
}


def imagen_codigo(ruta, inicio, fin, destino):
    lineas = (RAIZ / ruta).read_text(encoding="utf-8").splitlines()[inicio - 1:fin]
    numeradas = [f"{n:>4}  {linea}" for n, linea in zip(range(inicio, fin + 1), lineas)]
    encabezado = f"{ruta}"
    alto_linea = 27
    ancho = 1100
    alto = alto_linea * (len(numeradas) + 2) + 20
    img = Image.new("RGB", (ancho, alto), "#1e1e1e")
    dibujo = ImageDraw.Draw(img)
    dibujo.rectangle([0, 0, ancho, alto_linea + 6], fill="#2d2d30")
    dibujo.text((14, 6), encabezado, font=FUENTE, fill="#9cdcfe")
    y = alto_linea + 16
    for linea in numeradas:
        dibujo.text((14, y), linea, font=FUENTE, fill="#d4d4d4")
        y += alto_linea
    img.save(destino)


def trayectorias_vensim(destino):
    sys.path.insert(0, str(RAIZ / "diagramas"))
    import correr_vensim

    base = correr_vensim.correr({})
    saturacion = correr_vensim.correr({"Factor de demanda": 1.8})
    fig, ejes = plt.subplots(1, 2, figsize=(12, 4.6))
    for ax, titulo, df in ((ejes[0], "Escenario base", base), (ejes[1], "Demanda +80 % (saturación)", saturacion)):
        ax.plot(df.index, df["Cola de espera"], label="Cola de espera", color="#0b6e4f")
        ax.plot(df.index, df["En atencion"], label="En atención", color="#5b6770")
        ax.plot(df.index, df["Abandonos acumulados"], label="Abandonos acumulados", color="#a33b20")
        ax.set_title(titulo)
        ax.set_xlabel("Horas desde la apertura")
        ax.set_ylabel("Pacientes")
        ax.grid(alpha=0.3)
    ejes[0].legend(loc="upper left", fontsize=9)
    fig.suptitle("Modelo de dinámica de sistemas (Vensim, ejecutado con PySD)", fontsize=12)
    fig.tight_layout()
    fig.savefig(destino, dpi=150)
    plt.close(fig)


def texto_pruebas(destino):
    resumen = (RAIZ / "docs" / "exposicion" / "capturas" / "pytest_resumen.txt")
    lineas = resumen.read_text(encoding="utf-8").splitlines() if resumen.exists() else ["(sin resumen)"]
    alto_linea = 27
    img = Image.new("RGB", (1100, alto_linea * (len(lineas) + 2) + 20), "#0c0c0c")
    dibujo = ImageDraw.Draw(img)
    dibujo.text((14, 10), "$ python -m pytest --cov=app --cov-fail-under=60", font=FUENTE, fill="#cccccc")
    y = 10 + alto_linea + 8
    for linea in lineas:
        color = "#4ec9b0" if ("passed" in linea or "Required" in linea) else "#d4d4d4"
        dibujo.text((14, y), linea, font=FUENTE, fill=color)
        y += alto_linea
    img.save(destino)


if __name__ == "__main__":
    SALIDA.mkdir(parents=True, exist_ok=True)
    for nombre, (ruta, inicio, fin) in FRAGMENTOS.items():
        imagen_codigo(ruta, inicio, fin, SALIDA / nombre)
    trayectorias_vensim(SALIDA / "16_vensim_trayectorias.png")
    texto_pruebas(SALIDA / "17_pruebas_resultado.png")
    print("listo:", len(list(SALIDA.glob("*.png"))), "imágenes en", SALIDA)
