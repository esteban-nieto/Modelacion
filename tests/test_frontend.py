import shutil
import subprocess
from pathlib import Path

import pytest

APP_JS = Path(__file__).resolve().parent.parent / "static" / "app.js"


def _node():
    """Busca Node en el PATH y, en Windows, en la ruta de instalación habitual."""
    encontrado = shutil.which("node")
    if encontrado:
        return encontrado
    for ruta in (r"C:\Program Files\nodejs\node.exe", "/usr/bin/node", "/usr/local/bin/node"):
        if Path(ruta).exists():
            return ruta
    return None


@pytest.mark.skipif(_node() is None, reason="requiere Node.js instalado")
def test_app_js_tiene_sintaxis_valida():
    resultado = subprocess.run([_node(), "--check", str(APP_JS)], capture_output=True, text=True)
    assert resultado.returncode == 0, resultado.stderr


def test_pagina_inicial_enlaza_menu_movil_y_script(cliente):
    html = cliente.get("/").text
    assert 'id="abrir-menu"' in html
    assert '/static/app.js' in html


def test_archivos_estaticos_no_se_cachean(cliente):
    respuesta = cliente.get("/static/app.js")
    assert respuesta.headers.get("Cache-Control") == "no-cache"
