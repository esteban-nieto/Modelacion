"""Toma capturas de la interfaz en ejecución para la exposición (docs/exposicion/capturas/).

Requiere la aplicación levantada (docker compose o uvicorn) y Playwright con Chromium:
    pip install playwright && python -m playwright install chromium

Uso: python scripts/capturas_frontend.py [URL_BASE]   (por defecto https://localhost:8443)
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "docs" / "exposicion" / "capturas"
BASE = sys.argv[1] if len(sys.argv) > 1 else "https://localhost:8443"
CORREO, CLAVE = "administrador@saludrural.co", "Admin12345"


def entrar(pagina):
    pagina.goto(BASE)
    pagina.fill("input[name=correo]", CORREO)
    pagina.fill("input[name=clave]", CLAVE)
    pagina.click("button[type=submit]")
    pagina.wait_for_selector("#menu button")


def seccion(pagina, titulo):
    pagina.click(f"#menu button:has-text('{titulo}')")
    pagina.wait_for_timeout(1200)


def ejecutar():
    SALIDA.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        contexto = navegador.new_context(ignore_https_errors=True, viewport={"width": 1280, "height": 800})
        pagina = contexto.new_page()

        pagina.goto(BASE)
        pagina.wait_for_selector("#form-login")
        pagina.screenshot(path=str(SALIDA / "01_login.png"))

        entrar(pagina)
        seccion(pagina, "Tablero")
        pagina.wait_for_timeout(800)
        pagina.screenshot(path=str(SALIDA / "02_tablero.png"), full_page=True)

        seccion(pagina, "Cola de atención")
        pagina.screenshot(path=str(SALIDA / "03_cola_atencion.png"))

        seccion(pagina, "Reportes")
        pagina.screenshot(path=str(SALIDA / "04_reportes.png"))

        seccion(pagina, "Auditoría")
        pagina.screenshot(path=str(SALIDA / "05_auditoria.png"))

        # Vista de consulta: el rol consulta no ve acciones de escritura.
        pagina.click("#salir")
        pagina.wait_for_selector("#form-login")
        pagina.fill("input[name=correo]", "consulta@saludrural.co")
        pagina.fill("input[name=clave]", "Consulta12345")
        pagina.click("button[type=submit]")
        pagina.wait_for_selector("#menu button")
        seccion(pagina, "Citas")
        pagina.screenshot(path=str(SALIDA / "06_rol_consulta_citas.png"))

        # Menú en celular.
        movil = contexto.new_page()
        movil.set_viewport_size({"width": 375, "height": 812})
        movil.goto(BASE)
        movil.wait_for_selector("#form-login")
        movil.fill("input[name=correo]", CORREO)
        movil.fill("input[name=clave]", CLAVE)
        movil.click("button[type=submit]")
        movil.wait_for_selector("#vista-app", state="visible")
        movil.wait_for_timeout(1200)
        movil.screenshot(path=str(SALIDA / "07_movil_tablero.png"))
        movil.click("#abrir-menu")
        movil.wait_for_timeout(400)
        movil.screenshot(path=str(SALIDA / "08_movil_menu_abierto.png"))

        navegador.close()
    print("capturas en", SALIDA)


if __name__ == "__main__":
    ejecutar()
