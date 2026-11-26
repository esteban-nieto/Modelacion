"""Convierte un Markdown sencillo (títulos, listas, tablas, negritas) a Word (.docx)."""

import re
import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor

NEGRITA = re.compile(r"\*\*(.+?)\*\*")


def agregar_texto(parrafo, texto):
    pos = 0
    for m in NEGRITA.finditer(texto):
        if m.start() > pos:
            parrafo.add_run(texto[pos:m.start()])
        parrafo.add_run(m.group(1)).bold = True
        pos = m.end()
    if pos < len(texto):
        parrafo.add_run(texto[pos:])


def convertir(origen, destino):
    doc = Document()
    doc.styles["Normal"].font.size = Pt(11)
    for estilo in ("Title", "Heading 1", "Heading 2", "Heading 3"):
        doc.styles[estilo].font.color.rgb = RGBColor(0, 0, 0)
    lineas = Path(origen).read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lineas):
        linea = lineas[i].rstrip()
        if not linea.strip() or linea.strip() == "---":
            i += 1
            continue
        if linea.startswith("|"):
            filas = []
            while i < len(lineas) and lineas[i].startswith("|"):
                celdas = [c.strip() for c in lineas[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in celdas if c):
                    filas.append(celdas)
                i += 1
            tabla = doc.add_table(rows=len(filas), cols=len(filas[0]))
            tabla.style = "Table Grid"
            for r, fila in enumerate(filas):
                for c, valor in enumerate(fila):
                    celda = tabla.cell(r, c)
                    celda.text = ""
                    agregar_texto(celda.paragraphs[0], valor)
                    if r == 0:
                        for run in celda.paragraphs[0].runs:
                            run.bold = True
            doc.add_paragraph()
            continue
        m = re.match(r"(#{1,3})\s+(.*)", linea)
        if m:
            doc.add_heading(m.group(2), level=len(m.group(1)) - 1 if len(m.group(1)) > 1 else 0)
        elif re.match(r"\s*[-*]\s+", linea):
            agregar_texto(doc.add_paragraph(style="List Bullet"), re.sub(r"^\s*[-*]\s+", "", linea))
        elif re.match(r"\s*\d+\.\s+", linea):
            agregar_texto(doc.add_paragraph(style="List Number"), re.sub(r"^\s*\d+\.\s+", "", linea))
        else:
            agregar_texto(doc.add_paragraph(), linea)
        i += 1
    Path(destino).parent.mkdir(parents=True, exist_ok=True)
    doc.save(destino)


if __name__ == "__main__":
    for ruta in sys.argv[1:]:
        p = Path(ruta)
        convertir(p, p.with_suffix(".docx"))
        print("ok", p.with_suffix(".docx"))
