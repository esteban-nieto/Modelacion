"""Arma docs/entregables_finales/ con los 10 entregables finales de la guía (sección 9).

Copia los archivos reales del proyecto a una subcarpeta por entregable y genera un índice con
el estado de cada uno. Lo que no existe (video, declaración de IA, autoevaluación) queda marcado
como pendiente y se deja una plantilla o guía de qué falta.

Uso: python scripts/armar_entregables.py
"""

import shutil
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "docs" / "entregables_finales"

ENTREGABLES = [
    ("01_repositorio_git", "Repositorio Git con código, historial, README, scripts, Docker, pruebas y pipeline de CI",
     [".github/workflows/ci.yml", "Dockerfile", "docker-compose.yml", "README.md", "pytest.ini", "requirements.txt", "requirements-dev.txt"],
     "Entregado",
     "El repositorio está en https://github.com/esteban-nieto/Modelacion, rama principal main."),
    ("02_sistema_desplegado", "Sistema desplegado y accesible (URL) o ejecutable con un solo comando documentado",
     ["docs/entregables_fuentes/Enlace_sistema_desplegado.docx"],
     "Entregado (desplegado en Railway)",
     "URL de la aplicación: https://modelacion-api-production.up.railway.app (documentación de la API en /docs). El enlace completo y los roles de acceso están en Enlace_sistema_desplegado.docx. Alternativa local: `docker compose --env-file .env up --build` (README)."),
    ("03_documentacion_componente_A", "Documentación del componente A (requisitos, ERD, arquitectura, UML, manuales)",
     ["docs/informes/Documentacion_Componente_A.docx", "docs/figuras/erd.png", "docs/figuras/arquitectura.png",
      "docs/figuras/casos_de_uso.png", "docs/figuras/secuencia_cita.png", "docs/figuras/secuencia_login.png", "docs/openapi.json", "docs/esquema.sql"],
     "Entregado (revisar manuales)",
     "Revisar que los manuales de usuario y técnico estén completos dentro del documento."),
    ("04_informe_tecnico_componente_B", "Informe técnico del componente B (8 a 12 páginas, APA 7.ª)",
     ["docs/informes/Informe_Tecnico_Componente_B.docx"],
     "Entregado (extensión y APA por verificar)",
     "No se ha contado la extensión (8 a 12 páginas sin anexos) ni revisado el formato APA 7."),
    ("05_modelo_simulacion", "Archivos del modelo de simulación (.mod u otro) con instrucciones para reproducir",
     ["simulacion/modelo.py", "simulacion/escenarios.py", "simulacion/exportar_datos.py", "simulacion/ajuste_distribuciones.py",
      "simulacion/monte_carlo.py", "simulacion/financiero.py", "simulacion/calentamiento.py", "simulacion/datos/citas_historicas.csv",
      "diagramas/turnos_flujos_niveles.mdl", "diagramas/turnos_causal.mdl", "diagramas/calibrar_vensim.py", "diagramas/correr_vensim.py"],
     "Entregado",
     "Modelo en SimPy (código Python) y modelos Vensim (.mdl). Pasos de reproducción en el README, sección 'Reproducir la simulación'."),
    ("06_infografia_escenarios", "Infografía de la comparación de escenarios (1 página)",
     ["docs/figuras/infografia_b2.pdf", "docs/figuras/infografia_b2.png"],
     "Entregado",
     "Generada con la tabla final de casos de B2 (docs/generar_infografia_b2.py)."),
    ("07_bitacora_y_cronograma", "Bitácora de equipo y cronograma",
     ["docs/informes/Bitacora_y_Cronograma.docx", "docs/figuras/gantt.png"],
     "Entregado (revisar aporte individual)",
     "La bitácora debe mostrar el aporte individual identificable de cada integrante."),
    ("08_videos_individuales", "Video individual de postura crítica (máximo 5 minutos) por cada integrante",
     ["docs/exposicion/Guion_Video_B5.md"],
     "Pendiente (no grabado)",
     "Cada integrante debe grabar su video. Se deja el guion; el video no se puede generar desde aquí."),
    ("09_presentacion_sustentacion", "Presentación de la sustentación",
     ["docs/exposicion/Exposicion_Modelacion.pptx"],
     "Entregado (diseño por revisar)",
     "Revisar el renderizado de todas las diapositivas en PowerPoint antes de la sustentación."),
    ("10_declaracion_IA_y_coevaluacion", "Declaración de uso de herramientas de IA y autoevaluación/coevaluación",
     [], "Pendiente (borrador)",
     "Ver el borrador en la subcarpeta 10_declaracion_IA_y_coevaluacion. El equipo debe revisarlo, completarlo y firmarlo."),
]

BORRADOR_IA = """# Declaración de uso de herramientas de IA (BORRADOR)

Revisar, completar y firmar antes de entregar. Lo siguiente es lo que consta en el repositorio.

- **Herramienta:** Claude Code (Anthropic), asistente de programación con modelo de lenguaje.
- **Para qué se usó:** escribir y depurar código Python y JavaScript, generar scripts de simulación y de pruebas, redactar y regenerar documentos (B2, informes), buscar fuentes bibliográficas y generar figuras.
- **Despliegue:** configuración del despliegue en Railway (Dockerfile con el puerto PORT, normalización de la URL de PostgreSQL al driver psycopg2, variables de entorno y comandos de la CLI de Railway).
- **Depuración:** diagnóstico de errores de ejecución y de despliegue (por ejemplo, el fallo 502 por el driver de la base de datos y los errores de renderizado de la presentación y de los documentos). Cada corrección fue revisada y probada por el equipo.
- **Qué se verificó:** las pruebas automáticas (49 pruebas, cobertura 96,84 %), la ejecución de los modelos SimPy y Vensim, la validación de Vensim contra datos no usados en la calibración (error 0,31 %), la búsqueda de los datos bibliográficos en revistas y bases (PubMed, Crossref, páginas de las revistas), con los casos que no se pudieron comprobar excluidos del informe, y la revisión de los resultados en la aplicación en ejecución.
- **Qué no se verificó con IA:** el texto completo de las fuentes citadas (solo se revisaron metadatos y resúmenes); la revisión de usabilidad con usuarios reales (no se hizo); las respuestas del formulario (son simuladas, y así deben declararse).
- **Quién lo declara:** Gaddiel Esteban Nieto Rojas.
"""

PLANTILLA_COEVAL = """# Autoevaluación y coevaluación (PLANTILLA)

Completar por cada integrante. Escala de 1 a 5.

| Criterio | Autoevaluación | Coevaluación |
|---|---|---|
| Contribución al código (componente A) | | |
| Contribución a la simulación (componente B) | | |
| Participación en puntos de control | | |
| Calidad de la bitácora | | |
| Comunicación del equipo | | |

Comentario libre:
"""


def copiar(origen, carpeta):
    fuente = RAIZ / origen
    if not fuente.exists():
        return False
    destino = carpeta / Path(origen).name
    if fuente.is_dir():
        shutil.copytree(fuente, destino, dirs_exist_ok=True)
    else:
        shutil.copy2(fuente, destino)
    return True


def ejecutar():
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    DESTINO.mkdir(parents=True)
    indice = ["# Entregables finales (guía, sección 9)", "",
              "| # | Entregable | Estado | Archivos |", "|---|---|---|---|"]
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
    except Exception:  # noqa: BLE001
        commit = "desconocido"
    for carpeta_nombre, titulo, archivos, estado, nota in ENTREGABLES:
        carpeta = DESTINO / carpeta_nombre
        carpeta.mkdir()
        copiados = [a for a in archivos if copiar(a, carpeta)]
        if carpeta_nombre == "10_declaracion_IA_y_coevaluacion":
            (carpeta / "declaracion_IA_BORRADOR.md").write_text(BORRADOR_IA, encoding="utf-8")
            (carpeta / "autoevaluacion_coevaluacion_PLANTILLA.md").write_text(PLANTILLA_COEVAL, encoding="utf-8")
            copiados = ["declaracion_IA_BORRADOR.md", "autoevaluacion_coevaluacion_PLANTILLA.md"]
        (carpeta / "LEEME.md").write_text(f"# {titulo}\n\n**Estado:** {estado}\n\n{nota}\n\nArchivos incluidos:\n" + "\n".join(f"- {c}" for c in copiados) + "\n", encoding="utf-8")
        n = carpeta_nombre.split("_")[0]
        indice.append(f"| {n} | {titulo} | {estado} | {len(copiados)} |")
    indice += ["", f"Generado desde el repositorio (último commit confirmado: {commit}).", "",
               "## Notas por entregable"] + [f"- **{c.split('_')[0]}** {nota}" for c, _, _, _, nota in ENTREGABLES]
    (DESTINO / "LEEME.md").write_text("\n".join(indice) + "\n", encoding="utf-8")
    print("creado", DESTINO)


if __name__ == "__main__":
    ejecutar()
