"""Genera las evidencias visuales de la exposición (docs/exposicion/evidencias/).

Capturas de la aplicación en ejecución (Playwright), Swagger, GitHub y Docker; tablas y gráficas
a partir de los JSON y CSV del proyecto; y fragmentos de código de los archivos reales.

Requisitos: la aplicación en http://127.0.0.1:8000 (uvicorn), Playwright con Chromium y Docker
para la captura de docker compose ps. Uso: python scripts/evidencias_expo.py
"""

import json
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "docs" / "exposicion" / "evidencias"
BASE = "http://127.0.0.1:8000"
FUENTE = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 18)
ALTO = 26


def mono_imagen(lineas, destino, titulo=""):
    ancho = 1200
    filas = lineas + ([] if not titulo else [])
    alto = ALTO * (len(filas) + 2) + 24
    img = Image.new("RGB", (ancho, alto), "#1e1e1e")
    d = ImageDraw.Draw(img)
    if titulo:
        d.rectangle([0, 0, ancho, ALTO + 8], fill="#2d2d30")
        d.text((12, 6), titulo, font=FUENTE, fill="#9cdcfe")
    y = ALTO + 16
    for linea in filas:
        d.text((12, y), linea[:150], font=FUENTE, fill="#d4d4d4")
        y += ALTO
    img.save(destino)


def codigo(ruta, inicio, fin, destino):
    lineas = (RAIZ / ruta).read_text(encoding="utf-8").splitlines()[inicio - 1:fin]
    numeradas = [f"{n:>4}  {l}" for n, l in zip(range(inicio, fin + 1), lineas)]
    mono_imagen(numeradas, destino, titulo=f"{ruta}  (líneas {inicio}-{fin})")


def cabecera_csv(ruta, n, destino, titulo):
    lineas = (RAIZ / ruta).read_text(encoding="utf-8").splitlines()[:n]
    mono_imagen(lineas, destino, titulo=titulo)


def capturas_app():
    with sync_playwright() as p:
        nav = p.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 760})
        pg = ctx.new_page()

        def entrar(correo, clave):
            pg.goto(BASE)
            pg.evaluate("sessionStorage.clear()")
            pg.reload()
            pg.wait_for_selector("#form-login", state="visible")
            pg.fill("input[name=correo]", correo)
            pg.fill("input[name=clave]", clave)
            pg.click("button[type=submit]")
            pg.wait_for_selector("#menu button")
            pg.wait_for_timeout(600)

        def ir(seccion):
            pg.click(f"#menu button:has-text('{seccion}')")
            pg.wait_for_timeout(1000)

        entrar("administrador@saludrural.co", "Admin12345")
        ir("Pacientes")
        pg.screenshot(path=str(SALIDA / "20_crud_pacientes.png"))
        pg.fill("input[type=search]", "Ana Gómez")
        pg.keyboard.press("Enter")
        pg.wait_for_timeout(900)
        pg.screenshot(path=str(SALIDA / "21_busqueda_pacientes.png"))
        ir("Usuarios")
        pg.screenshot(path=str(SALIDA / "22_admin_usuarios.png"))

        pg.goto(f"{BASE}/docs")
        pg.wait_for_timeout(1500)
        pg.screenshot(path=str(SALIDA / "23_swagger.png"))

        entrar("operador@saludrural.co", "Operador12345")
        pg.screenshot(path=str(SALIDA / "25_menu_operador.png"))
        entrar("consulta@saludrural.co", "Consulta12345")
        ir("Pacientes")
        pg.screenshot(path=str(SALIDA / "24_consulta_pacientes.png"))

        gh = ctx.new_page()
        gh.goto("https://github.com/esteban-nieto/Modelacion/pull/1/checks")
        gh.wait_for_timeout(3000)
        gh.screenshot(path=str(SALIDA / "26_github_checks.png"))
        nav.close()


def tabla_roles(destino):
    filas = [
        ["Consultar catálogos, pacientes, citas, reportes y tablero", "Sí", "Sí", "Sí"],
        ["Crear y editar pacientes, citas, sedes, servicios y profesionales", "Sí", "Sí", "No"],
        ["Exportar citas para simulación y sugerir profesional", "Sí", "Sí", "No"],
        ["Eliminar (borrado lógico) cualquier registro", "Sí", "No", "No"],
        ["Crear, editar y consultar usuarios", "Sí", "No", "No"],
        ["Consultar la auditoría", "Sí", "No", "No"],
    ]
    fig, eje = plt.subplots(figsize=(12, 4.2))
    eje.axis("off")
    tb = eje.table(cellText=filas, colLabels=["Permiso", "Administrador", "Operador", "Consulta"], loc="center", cellLoc="left", colWidths=[0.58, 0.14, 0.14, 0.14])
    tb.auto_set_font_size(False)
    tb.set_fontsize(11)
    tb.scale(1, 1.8)
    for (r, c), celda in tb.get_celld().items():
        if r == 0:
            celda.set_facecolor("#007a3d")
            celda.set_text_props(color="white", weight="bold")
        elif c > 0:
            celda.set_text_props(ha="center")
    fig.savefig(destino, dpi=150, bbox_inches="tight")
    plt.close(fig)


def tabla_vv(destino):
    r = json.loads((RAIZ / "simulacion/salidas/resultados.json").read_text(encoding="utf-8"))["validacion"]
    filas = [
        ["Días reales del CRUD", str(r["dias_reales"])],
        ["Espera diaria real (media)", f"{r['espera_diaria_real_media']} min"],
        ["Espera diaria simulada (media)", f"{r['espera_diaria_simulada_media']} min"],
        ["Prueba t de Welch (p)", f"{r['welch_t_p']:.4f}"],
        ["Kolmogorov-Smirnov dos muestras (p)", f"{r['ks_dos_muestras_p']:.4f}"],
        ["Mann-Whitney (p)", f"{r['mann_whitney_p']:.4f}"],
    ]
    fig, eje = plt.subplots(figsize=(9, 3.6))
    eje.axis("off")
    tb = eje.table(cellText=filas, colLabels=["Medida", "Valor"], loc="center", cellLoc="left", colWidths=[0.7, 0.3])
    tb.auto_set_font_size(False)
    tb.set_fontsize(11)
    tb.scale(1, 1.7)
    for (rr, c), celda in tb.get_celld().items():
        if rr == 0:
            celda.set_facecolor("#007a3d")
            celda.set_text_props(color="white", weight="bold")
    fig.savefig(destino, dpi=150, bbox_inches="tight")
    plt.close(fig)


def grafica_calentamiento(destino):
    c = json.loads((RAIZ / "simulacion/salidas/calentamiento.json").read_text(encoding="utf-8"))["medias_por_hora_min"]
    fig, eje = plt.subplots(figsize=(9, 3.8))
    eje.bar(list(c.keys()), list(c.values()), color="#0b6e4f")
    eje.set_ylabel("Espera media (min)")
    eje.set_xlabel("Hora de llegada")
    eje.set_title("Espera por hora: el transitorio es parte de la jornada real")
    eje.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(destino, dpi=150)
    plt.close(fig)


def grafica_cuellos(destino):
    c = json.loads((RAIZ / "simulacion/salidas/resultados.json").read_text(encoding="utf-8"))["cuellos_de_botella_ocupacion_pct"]
    fig, eje = plt.subplots(figsize=(9, 3.6))
    eje.barh(list(c.keys()), list(c.values()), color="#5b6770")
    eje.set_xlabel("Ocupación (%) en el sistema actual")
    eje.set_title("Cuellos de botella: ocupación por servicio")
    eje.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(destino, dpi=150)
    plt.close(fig)


def tabla_b2(destino):
    filas = [
        ["Local", "Cartagena (2013)", "Urgencias: recurso restrictivo", "Medina y Arrieta"],
        ["Local", "Bogotá (2022)", "Emergencias médicas: ambulancias", "Aguiar et al."],
        ["Local", "Bogotá (2017)", "Urgencias: flujo de pacientes", "Hernández Chinchilla et al."],
        ["Global", "Singapur y Chengdu (2021)", "Camas y recursos hospitalarios", "Xie et al."],
        ["Global", "Italia (2023)", "Urgencias: escenario implementado", "Dosi et al."],
        ["Global", "Alemania (2021)", "Atención primaria con agentes", "Comis et al."],
    ]
    fig, eje = plt.subplots(figsize=(12, 3.8))
    eje.axis("off")
    tb = eje.table(cellText=filas, colLabels=["Ámbito", "Caso", "Qué se decidió", "Fuente"], loc="center", cellLoc="left", colWidths=[0.1, 0.3, 0.4, 0.2])
    tb.auto_set_font_size(False)
    tb.set_fontsize(10.5)
    tb.scale(1, 1.7)
    for (rr, c), celda in tb.get_celld().items():
        if rr == 0:
            celda.set_facecolor("#007a3d")
            celda.set_text_props(color="white", weight="bold")
    fig.savefig(destino, dpi=150, bbox_inches="tight")
    plt.close(fig)


def error_422(destino):
    sys.path.insert(0, str(RAIZ))
    from fastapi.testclient import TestClient
    from app.main import app
    cliente = TestClient(app)
    tok = cliente.post("/api/auth/login", json={"correo": "administrador@saludrural.co", "clave": "Admin12345"}).json()["token"]
    r = cliente.post("/api/sedes", json={"vereda": "Fagua"}, headers={"Authorization": f"Bearer {tok}"})
    mono_imagen([f"POST /api/sedes  ->  HTTP {r.status_code}", r.text[:600]], destino, titulo="Respuesta de la API ante un dato faltante")


if __name__ == "__main__":
    SALIDA.mkdir(parents=True, exist_ok=True)
    capturas_app()
    try:
        out = subprocess.run(["docker", "compose", "ps"], cwd=RAIZ, capture_output=True, text=True, timeout=60).stdout
        mono_imagen(out.splitlines(), SALIDA / "30_docker_ps.png", titulo="$ docker compose ps")
    except Exception as e:  # noqa: BLE001
        print("docker no disponible:", e)
    tabla_roles(SALIDA / "35_roles_tabla.png")
    tabla_vv(SALIDA / "36_vv_tabla.png")
    grafica_calentamiento(SALIDA / "37_calentamiento.png")
    grafica_cuellos(SALIDA / "38_cuellos.png")
    tabla_b2(SALIDA / "39_b2_casos.png")
    error_422(SALIDA / "32_error_422.png")
    cabecera_csv("simulacion/datos/citas_historicas.csv", 9, SALIDA / "45_csv_citas.png", "simulacion/datos/citas_historicas.csv")
    cabecera_csv("simulacion/salidas/ajuste_distribuciones.csv", 7, SALIDA / "44_csv_ajuste.png", "simulacion/salidas/ajuste_distribuciones.csv")
    mono_imagen((RAIZ / "requirements.txt").read_text(encoding="utf-8").splitlines(), SALIDA / "34_requirements.png", titulo="requirements.txt")
    codigo("docs/esquema.sql", 1, 26, SALIDA / "40_esquema_sql.png")
    codigo("simulacion/exportar_datos.py", 7, 15, SALIDA / "42_exportar_codigo.png")
    codigo("simulacion/ajuste_distribuciones.py", 1, 30, SALIDA / "43_ajuste_codigo.png")
    codigo("app/negocio/turnos.py", 17, 46, SALIDA / "41_turnos_codigo.png")
    codigo("app/seguridad.py", 1, 22, SALIDA / "11_codigo_hash.png")
    codigo("app/consultas.py", 6, 19, SALIDA / "12_codigo_filtros.png")
    print("evidencias en", SALIDA)
