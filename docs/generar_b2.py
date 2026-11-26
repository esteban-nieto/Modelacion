from docx.enum.text import WD_BREAK

from generar_informes import DESTINO, FIGURAS_DOCS, documento, figura, lista, tabla

# Solo fuentes cuyos datos bibliográficos se comprobaron en búsqueda (editorial, DOI o PubMed).
# Lo que no se pudo comprobar NO se incluye: ver la sección "Pendientes" del documento.
REFERENCIAS = [
    "Hernández Chinchilla, D., Camacho Oliveros, M. Á., & Duarte Forero, E. L. (2017). Análisis del flujo de pacientes en el servicio de urgencias del Hospital Universitario La Samaritana a través de simulación discreta. Avances Investigación en Ingeniería, 14. https://doi.org/10.18041/1794-4953/avances.1.1289",
    "Aguiar, C., Rentería, S., Catumba-Ruiz, J. C., & Barrera, D. (2022). Use of discrete event simulation and genetic algorithms to estimate the necessary resources to respond in a timely manner in the Medical Emergency System in Bogotá. Medwave, 22(3), e002100. https://doi.org/10.5867/medwave.2022.03.002100",
    "Medina Monterrosa, Y., & Arrieta-Canchila, K. (2013). Simulación de eventos discretos para optimizar recursos restrictivos del servicio de urgencias de un hospital. Revista Científica Teknos, 13(1), 55-66.",
    "Sánchez Castillo, V., Gómez Cano, C. A., & Gonzalez-Argote, J. (2023). Telemedicine and mHealth applications for health monitoring in rural communities in Colombia: A systematic review. EAI Endorsed Transactions on Pervasive Health and Technology, 9(1). https://doi.org/10.4108/eetpht.9.3400",
    "Xie, J., Zhuang, W., Ang, M., Chou, M. C., Luo, L., & Yao, D. D. (2021). Analytics for hospital resource planning: Two case studies. Production and Operations Management. https://doi.org/10.1111/poms.13158",
    "Dosi, C., Iori, M., Kramer, A., & Vignoli, M. (2023). Successful implementation of discrete event simulation: Integrating design thinking and simulation approach in an emergency department. Production Planning & Control, 34(13), 1233-1247. https://doi.org/10.1080/09537287.2021.1996651",
    "Comis, M., et al. (2021). Patients, primary care, and policy: Agent-based simulation modeling for health care decision support. Health Care Management Science, 24(4). https://doi.org/10.1007/s10729-021-09556-2",
    "Revisión sistemática de sensores de bajo costo para el monitoreo de la calidad del aire en América Latina (2026). ES Engineering and Science, 15(1). https://doi.org/10.18607/ES20261521055",
]

# Casos de simulación para decidir. Solo se incluyen los verificados con fuente primaria.
CASOS_LOCALES = [
    ("Cartagena, Colombia (2013)", "Urgencias de un hospital; simulación de eventos discretos para asignar recursos restrictivos.", "Medina y Arrieta (2013)"),
    ("Bogotá, Colombia (2022)", "Sistema de emergencias médicas; simulación con algoritmos genéticos para estimar ambulancias necesarias.", "Aguiar et al. (2022)"),
    ("Bogotá, Colombia (2017)", "Urgencias del Hospital Universitario La Samaritana; simulación discreta del flujo de pacientes, con escenarios para reducir demoras y estadía.", "Hernández Chinchilla et al. (2017)"),
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
        "titulo": "Revisión sistemática de sensores de bajo costo en América Latina (2026): tecnología electrónica para el ambiente (en portugués, texto con resumen en inglés)",
        "sintesis": "Revisión sistemática con protocolo PRISMA de 87 artículos de Scopus y Web of Science sobre sensores de bajo costo para monitorear la calidad del aire en América Latina.",
        "aportes": "Muestra que el monitoreo ambiental con sensores electrónicos baratos se estudia en la región y que la cobertura oficial de monitoreo suele ser insuficiente, lo que justifica datos de bajo costo en comunidades.",
        "vacios": "Se centra en calidad del aire y no en salud rural ni en conectividad. El resumen consultado no detalla las conclusiones; el equipo debe leer el texto completo.",
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
        "revisados por pares con al menos uno en inglés. Hoy hay tres casos locales, tres globales y dos artículos revisados por pares "
        "sobre tecnologías electrónicas (uno en inglés). Las secciones de abajo marcan lo que queda por revisar."
    )

    doc.add_heading("1. Mapa comparativo", 1)
    tabla(
        doc,
        ["Ámbito", "Caso", "Qué se decidió con simulación", "Fuente"],
        [[ "Local", c[0], c[1], c[2]] for c in CASOS_LOCALES] + [["Global", c[0], c[1], c[2]] for c in CASOS_GLOBALES],
    )
    doc.add_paragraph(
        "La infografía de 1 página (`docs/figuras/infografia_b2.png`) se regenera con esta tabla antes de entregar el módulo."
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
            "Lectura del texto completo de las fuentes citadas, para poder explicarlas en la sustentación.",
            "Regenerar la infografía con la tabla de casos final.",
        ],
    )
    doc.add_heading("Referencias", 1)
    for referencia in REFERENCIAS:
        doc.add_paragraph(referencia)
    return doc


if __name__ == "__main__":
    DESTINO.mkdir(exist_ok=True)
    b2().save(DESTINO / "Modulo_B2_Escenarios_en_Perspectiva.docx")
