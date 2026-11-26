from docx.enum.text import WD_BREAK

from generar_informes import DESTINO, FIGURAS_DOCS, documento, figura, lista, tabla

# Solo fuentes cuyos datos bibliográficos se comprobaron en búsqueda (editorial, DOI o PubMed).
# Lo que no se pudo comprobar NO se incluye: ver la sección "Pendientes" del documento.
REFERENCIAS = [
    "Aguiar, C., Rentería, S., Catumba-Ruiz, J. C., & Barrera, D. (2022). Use of discrete event simulation and genetic algorithms to estimate the necessary resources to respond in a timely manner in the Medical Emergency System in Bogotá. Medwave, 22(3), e002100. https://doi.org/10.5867/medwave.2022.03.002100",
    "Medina Monterrosa, Y., & Arrieta-Canchila, K. (2013). Simulación de eventos discretos para optimizar recursos restrictivos del servicio de urgencias de un hospital. Revista Científica Teknos, 13(1), 55-66.",
    "Sánchez Castillo, V., Gómez Cano, C. A., & Gonzalez-Argote, J. (2023). Telemedicine and mHealth applications for health monitoring in rural communities in Colombia: A systematic review. EAI Endorsed Transactions on Pervasive Health and Technology, 9(1). https://doi.org/10.4108/eetpht.9.3400",
    "Xie, J., Zhuang, W., Ang, M., Chou, M. C., Luo, L., & Yao, D. D. (2021). Analytics for hospital resource planning: Two case studies. Production and Operations Management. https://doi.org/10.1111/poms.13158",
    "Dosi, C., Iori, M., Kramer, A., & Vignoli, M. (2023). Successful implementation of discrete event simulation: Integrating design thinking and simulation approach in an emergency department. Production Planning & Control, 34(13), 1233-1247. https://doi.org/10.1080/09537287.2021.1996651",
    "Comis, M., et al. (2021). Patients, primary care, and policy: Agent-based simulation modeling for health care decision support. Health Care Management Science, 24(4). https://doi.org/10.1007/s10729-021-09556-2",
]

# Casos de simulación para decidir. Solo se incluyen los verificados con fuente primaria.
CASOS_LOCALES = [
    ("Cartagena, Colombia (2013)", "Urgencias de un hospital; simulación de eventos discretos para asignar recursos restrictivos.", "Medina y Arrieta (2013)"),
    ("Bogotá, Colombia (2022)", "Sistema de emergencias médicas; simulación con algoritmos genéticos para estimar ambulancias necesarias.", "Aguiar et al. (2022)"),
]
CASOS_GLOBALES = [
    ("Singapur y Chengdu, China (2021)", "Planeación de camas y de recursos de diagnóstico en dos hospitales grandes, con datos reales y simulación para validar.", "Xie et al. (2021)"),
    ("Italia (2023)", "Urgencias de un hospital del norte de Italia: la simulación validada por los gestores eligió un escenario que el servicio implementó.", "Dosi et al. (2023)"),
    ("Alemania (2021)", "Sistema de atención primaria regional modelado con datos empíricos para evaluar políticas de decisión (agentes).", "Comis et al. (2021)"),
]

RESENAS = [
    {
        "titulo": "Sánchez Castillo et al. (2023): telemedicina y mHealth en comunidades rurales de Colombia (en inglés)",
        "sintesis": "Revisión sistemática de aplicaciones de telemedicina y mHealth para el monitoreo de la salud en comunidades rurales colombianas. Se incluyeron solo estudios publicados en revistas arbitradas.",
        "aportes": "Ubica la tecnología electrónica en el problema de salud rural que aborda este proyecto y muestra que el monitoreo a distancia se estudia en Colombia.",
        "vacios": "El resumen consultado no describe los resultados de cada estudio; el equipo debe leer el texto completo para reseñar hallazgos y limitaciones concretas.",
    },
    {
        "titulo": "Aguiar et al. (2022): simulación para recursos de emergencias en Bogotá (en inglés en el título, texto en español)",
        "sintesis": "Modelo híbrido de simulación de eventos discretos y algoritmos genéticos para estimar la cantidad y el tipo de ambulancias necesarias en Bogotá. Los datos provienen de registros administrativos de despachos entre 2014 y 2017.",
        "aportes": "Muestra cómo registros administrativos existentes sirven como entrada de un modelo de simulación para decidir recursos, el mismo flujo que este proyecto plantea con el CRUD.",
        "vacios": "Se centra en emergencias prehospitalarias, no en un puesto de salud. Los datos de cada estudio no son de un sitio rural.",
    },
]


def b2():
    doc = documento("Módulo B2: Escenarios en perspectiva", "Análisis comparativo de casos donde la simulación se usó para decidir")

    doc.add_heading("Estado del módulo", 1)
    doc.add_paragraph(
        "Este documento contiene solo lo verificado hasta ahora. La guía exige al menos tres casos locales y tres globales, y dos artículos "
        "revisados por pares con al menos uno en inglés. Hoy hay dos casos locales y tres globales verificados, y un artículo en inglés con DOI. "
        "Las secciones de abajo marcan lo que falta."
    )

    doc.add_heading("1. Mapa comparativo", 1)
    tabla(
        doc,
        ["Ámbito", "Caso", "Qué se decidió con simulación", "Fuente"],
        [[ "Local", c[0], c[1], c[2]] for c in CASOS_LOCALES] + [["Global", c[0], c[1], c[2]] for c in CASOS_GLOBALES],
    )
    doc.add_paragraph(
        "Pendiente: 1 caso local más. Candidato sin confirmar: Universidad Nacional, revista DYNA (2026, DOI 10.15446/dyna.v93n242.125778), simulación en FlexSim de centros de salud ante perturbaciones epidemiológicas; falta confirmar que el caso sea colombiano. La infografía de 1 página (`docs/figuras/infografia_b2.png`) todavía muestra "
        "casos de una versión anterior y debe regenerarse con esta tabla."
    )

    doc.add_heading("2. Análisis crítico", 1)
    doc.add_paragraph(
        "Los casos verificados comparten un patrón: un servicio con demanda variable y recursos limitados se modela como un sistema de colas, "
        "se alimenta con datos registrados y se usa para comparar alternativas antes de cambiar la operación. Los dos casos colombianos "
        "tratan de urgencias y de emergencias. Los globales cubren planeación hospitalaria (Singapur y Chengdu), urgencias (Italia) y atención primaria con agentes (Alemania). Ninguno trata de un puesto de salud rural."
    )
    lista(
        doc,
        [
            "Tecnológico: los tres casos dependen de datos de llegadas y tiempos de servicio. En un puesto rural el primer paso es ese registro, que el CRUD del proyecto captura y exporta.",
            "Social: la decisión sobre recursos debe vigilar a quienes esperan más, no solo el promedio. El caso de Bogotá parte de tiempos de respuesta que superan lo esperado, y eso afecta a los pacientes más graves.",
            "Cultural: la aceptación de una regla nueva depende de la comunidad y del personal. Los casos verificados no la estudian.",
        ],
    )
    doc.add_paragraph(
        "Relación con los retos regionales y translocales: la telemedicina rural en Colombia (Sánchez Castillo et al., 2023) muestra que la tecnología electrónica "
        "ya se estudia para salud rural, pero el vínculo con la simulación de recursos no aparece en las fuentes verificadas. Ese es el aporte que este proyecto debe demostrar."
    )
    lista(
        doc,
        [
            "Las cifras de cada caso son de su contexto; trasladarlas a un puesto rural exige revalidar el modelo con datos propios.",
            "Este análisis se basa en resúmenes y metadatos. El equipo debe leer los textos completos antes de la sustentación.",
        ],
    )

    doc.add_heading("3. Lectura crítica de artículos revisados por pares", 1)
    doc.add_paragraph("Se reseñan dos artículos revisados por pares, uno en inglés. Los resúmenes consultados no bastan para una reseña completa; las síntesis deben validarse con el texto completo.")
    for r in RESENAS:
        doc.add_heading(r["titulo"], 2)
        doc.add_paragraph().add_run("Síntesis. ").bold = True
        doc.paragraphs[-1].add_run(r["sintesis"])
        doc.add_paragraph().add_run("Aportes. ").bold = True
        doc.paragraphs[-1].add_run(r["aportes"])
        doc.add_paragraph().add_run("Vacíos. ").bold = True
        doc.paragraphs[-1].add_run(r["vacios"])

    doc.add_heading("4. Conclusiones (provisionales)", 1)
    lista(
        doc,
        [
            "La simulación se usa para decidir recursos antes de aplicarlos, y los casos verificados lo confirman en urgencias y en planeación hospitalaria.",
            "El aporte propio es llevar el enfoque a un puesto de salud rural. Ninguna fuente verificada lo hace todavía.",
        ],
    )

    doc.add_heading("Pendientes del módulo B2", 1)
    lista(
        doc,
        [
            "Un caso local más, con fuente primaria verificada (DOI o revista) y ubicación confirmada en Colombia.",
            "Un segundo artículo revisado por pares sobre tecnologías electrónicas en salud, ambiente o conectividad.",
            "Lectura del texto completo de los cuatro artículos citados.",
            "Regenerar la infografía con los casos finales.",
        ],
    )
    doc.add_heading("Referencias", 1)
    for referencia in REFERENCIAS:
        doc.add_paragraph(referencia)
    return doc


if __name__ == "__main__":
    DESTINO.mkdir(exist_ok=True)
    b2().save(DESTINO / "Modulo_B2_Escenarios_en_Perspectiva.docx")
