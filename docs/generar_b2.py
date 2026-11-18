from pathlib import Path

from docx.enum.text import WD_BREAK

from generar_informes import DESTINO, FIGURAS_DOCS, documento, figura, lista, tabla

REFERENCIAS = [
    "Adacher, L., Flamini, M., & Naldi, M. (2024). Simulation of a schedule-based mass vaccination clinic. Journal of Simulation, 18(5), 903-919. https://doi.org/10.1080/17477778.2023.2260348",
    "Gáfaro-Rojas, A. I., Mallor-Giménez, F., & Azcárate-Camio, C. (2014). Modelado de la atención en consulta externa en un hospital público: una herramienta de gestión. Gerencia y Políticas de Salud, 13(26). https://doi.org/10.11144/Javeriana.rgsp13-26.mace",
    "Hanly, M., Churches, T., Fitzgerald, O., Caterson, I., MacIntyre, C. R., & Jorm, L. (2022). Modelling vaccination capacity at mass vaccination hubs and general practice clinics: A simulation study. BMC Health Services Research, 22, Article 1059. https://doi.org/10.1186/s12913-022-08447-8",
    "Hernández Chinchilla, D., Camacho Oliveros, M. Á., & Duarte Forero, E. L. (2017). Análisis del flujo de pacientes en el servicio de urgencias del Hospital Universitario la Samaritana a través de simulación discreta. Avances Investigación en Ingeniería, 14(1), 109-122. https://doi.org/10.18041/1794-4953/avances.1.1289",
    "Lenin, R. B., Lowery, C. L., Hitt, W. C., Manning, N. A., Lowery, P., & Eswaran, H. (2015). Optimizing appointment template and number of staff of an OB/GYN clinic: Micro and macro simulation analyses. BMC Health Services Research, 15, Article 387. https://doi.org/10.1186/s12913-015-1007-9",
    "Medina, P., & Arrieta, K. (2013). Simulación de eventos discretos para optimizar recursos restrictivos del servicio de urgencias de un hospital. Cartagena, Colombia. Teknos Revista Científica, 13(1), 55-66. https://doi.org/10.25044/25392190.425",
    "Velásquez-Restrepo, P. A., Rodríguez-Quintero, A. K., & Jaén-Posada, J. S. (2011). Metodologías cuantitativas para la optimización del servicio de urgencias: Una revisión de la literatura. Gerencia y Políticas de Salud, 10(21). https://doi.org/10.11144/Javeriana.rgsp10-21.mcpo",
    "Zhang, X. (2018). Application of discrete event simulation in health care: A systematic review. BMC Health Services Research, 18, Article 687. https://doi.org/10.1186/s12913-018-3456-4",
]

RESENAS = [
    {
        "titulo": "Lenin et al. (2015), clínica de ginecología y obstetricia (en inglés)",
        "sintesis": "Los autores construyeron un modelo de eventos discretos de una clínica ambulatoria, ajustaron distribuciones de los tiempos de servicio con los datos del registro de pacientes y validaron el modelo comparando las esperas simuladas con las reales. "
        "Con el modelo validado probaron escenarios y encontraron que citas cada 16 minutos en la mañana y cada 19 en la tarde, más un auxiliar médico, reducían en 39,84 % la espera promedio por proveedor y en 30,31 % la espera total, sin afectar la utilización del personal.",
        "aportes": "Demuestra un procedimiento completo (datos, ajuste, validación, escenarios) que cambia decisiones de agenda y personal sin intervenir la clínica real; es el mismo procedimiento que sigue este proyecto.",
        "vacios": "Se limita a una clínica especializada de un hospital universitario y a decisiones de agenda y personal. No aborda la captura digital de los datos, la conectividad ni a poblaciones rurales.",
    },
    {
        "titulo": "Hanly et al. (2022), vacunación contra la COVID-19 (en inglés)",
        "sintesis": "Modelan con redes de colas estocásticas centros de vacunación masiva y consultorios generales, y estiman esperas y capacidad diaria según agenda, tiempos de servicio y personal. "
        "Con los supuestos adoptados, un centro grande llega a unas 1400 dosis por jornada de ocho horas y un consultorio grande a casi 300; las pruebas de estrés mostraron que los sitios con más personal resisten mejor la presión y que los centros masivos son más robustos que los consultorios. Ofrecen además una aplicación interactiva.",
        "aportes": "Muestra que un modelo de colas simple y liviano sirve para dimensionar servicios y que las pruebas de estrés (más demanda, menos personal) revelan la fragilidad de los sitios pequeños. La aplicación interactiva facilita que los gestores exploren sus propios supuestos.",
        "vacios": "Los tiempos de servicio son supuestos de los autores y no mediciones de un sitio real, lo que limita la validación. Tampoco incorpora la tecnología de registro ni las barreras de acceso de la población.",
    },
    {
        "titulo": "Medina y Arrieta (2013), urgencias en Cartagena (en español)",
        "sintesis": "Simulan las urgencias de un hospital de Cartagena, identifican las causas de la congestión y evalúan escenarios de mejora con medidas de teoría de colas. "
        "El recurso limitante fue el triage, con 99 % de ocupación, y la espera de los pacientes llegaba a 82 minutos; se sugiere añadir otro servidor en el triage para reducir las esperas y el número de pacientes que se retiran sin atención.",
        "aportes": "Es un caso colombiano que identifica el cuello de botella con datos y lo traduce en una decisión concreta de capacidad, y que considera los pacientes que abandonan, un efecto que este proyecto solo modela en dinámica de sistemas.",
        "vacios": "Se refiere a un servicio de urgencias de un hospital urbano y a un solo recurso crítico. No analiza costos de la alternativa ni el contexto rural, y el resumen no describe cómo se registran los datos.",
    },
]


def b2():
    doc = documento("Módulo B2: Escenarios en perspectiva", "Análisis comparativo de casos locales y globales donde la simulación se usó para decidir")
    doc.add_heading("1. Mapa comparativo", 1)
    doc.add_paragraph("La infografía resume tres casos locales y tres globales y sus relaciones críticas. También se entrega como archivo independiente en `docs/figuras/infografia_b2.pdf`.")
    figura(doc, FIGURAS_DOCS / "infografia_b2.png", 5.6, "Figura 1. Mapa comparativo de casos")
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    doc.add_heading("2. Análisis crítico", 1)
    doc.add_heading("2.1 Qué muestran los casos", 2)
    doc.add_paragraph(
        "Los seis casos coinciden en lo esencial: un servicio de salud con demanda variable y recursos limitados se modela como un sistema de colas, se validan sus resultados con datos y se comparan escenarios antes de modificar la operación. "
        "En Cartagena el triage de urgencias trabajaba al 99 % de ocupación con esperas de 82 minutos (Medina y Arrieta, 2013); en Arkansas un cambio en la plantilla de citas y un auxiliar más redujeron cerca de 40 % la espera por proveedor (Lenin et al., 2015); "
        "y en la vacunación contra la COVID-19 las pruebas de estrés mostraron qué sitios resisten un aumento de demanda o una falta de personal (Hanly et al., 2022). En todos, la simulación permitió descartar o elegir una medida sin costo de ensayo en la operación real."
    )
    doc.add_paragraph(
        "Entre los casos hay diferencias de enfoque que conviene relacionar. Los casos colombianos de Medina y Arrieta (2013) y de Hernández Chinchilla et al. (2017) se centran en urgencias de hospitales urbanos, donde el problema es la congestión y la estancia; "
        "Gáfaro-Rojas et al. (2014) modelan la consulta externa de un hospital público a partir del proceso de llegadas, de modo que se acercan más a la lógica de un puesto de salud. Los casos globales, en cambio, trabajan sobre la agenda de citas (Lenin et al., 2015; Adacher et al., 2024) "
        "y sobre la capacidad de sitios de vacunación (Hanly et al., 2022). Este proyecto combina ambas lógicas: modela las llegadas como en el caso colombiano de consulta externa y decide sobre reglas de fila y prioridad, como los casos de agenda."
    )
    doc.add_heading("2.2 Escenarios tecnológicos, sociales y culturales", 2)
    lista(
        doc,
        [
            "Tecnológico. Todos los casos dependen de datos de llegadas y tiempos de servicio. Lenin et al. (2015) los obtuvieron del registro de seguimiento de pacientes de la clínica. En un puesto rural el primer paso es crear ese registro: por eso el CRUD del proyecto captura la llegada, el inicio y el fin de cada atención y los exporta para la simulación. La conectividad limitada es un riesgo que ninguno de los casos revisados resuelve y que obliga a diseñar el sistema para funcionar con interrupciones.",
            "Social. Reducir la espera media no basta si se desatiende a quienes más lo necesitan. La prioridad que recomienda este proyecto beneficia a los pacientes prioritarios, pero debe vigilarse que no deteriore la espera de los demás. El caso de Cartagena recuerda que las esperas largas hacen que los pacientes se retiren sin atención, con riesgo para su salud (Medina y Arrieta, 2013).",
            "Cultural. La aceptación de una regla nueva depende de la confianza de la comunidad y del personal. Una fila única por servicio cambia la costumbre de esperar con un profesional conocido; por eso se modeló la confianza comunitaria en el diagrama causal. Los casos revisados no estudian esta dimensión, y una validación futura debería incluir la opinión de usuarios y de los profesionales.",
        ],
    )
    doc.add_heading("2.3 Vínculo con los retos regionales y translocales", 2)
    doc.add_paragraph(
        "El problema de contexto del campo de aprendizaje es el bajo aprovechamiento de tecnologías electrónicas en soluciones comunitarias de salud, ambiente y conectividad. Los casos muestran que la simulación es una forma de aprovechar datos que ya existen para decidir mejor, pero también revelan un hueco: "
        "una revisión de 211 estudios de simulación de eventos discretos en salud encontró que la mayoría (más del 68 % de las aplicaciones de operación de servicios) se concentra en problemas de unidades individuales, con pocos modelos de servicios integrados (Zhang, 2018). "
        "Otra revisión, centrada en urgencias, observó que los estudios no plantean un cambio de esquema del sistema ni exploran la reducción de la demanda (Velásquez-Restrepo et al., 2011). Ninguno de los casos revisados modela un puesto de salud rural, que es donde se cruzan los retos locales (distancia, conectividad, pocos profesionales) "
        "y translocales (aprender de experiencias de otros contextos sin trasladarlas de forma mecánica)."
    )
    doc.add_heading("2.4 Límites y precauciones", 2)
    lista(
        doc,
        [
            "Las cifras de cada caso corresponden a su contexto; trasladarlas a un puesto rural exige revalidar el modelo con datos propios.",
            "Los casos globales de vacunación parten de supuestos de tiempos de servicio y no de mediciones, de modo que su valor es metodológico.",
            "Los casos colombianos reseñados se basan en los resúmenes de los artículos; el equipo debe leer los textos completos antes de la sustentación.",
        ],
    )

    doc.add_heading("3. Lectura crítica de artículos arbitrados", 1)
    doc.add_paragraph("Se reseñan tres artículos revisados por pares sobre tecnologías aplicadas a la salud, dos de ellos en inglés.")
    for r in RESENAS:
        doc.add_heading(r["titulo"], 2)
        doc.add_paragraph().add_run("Síntesis. ").bold = True
        doc.paragraphs[-1].add_run(r["sintesis"])
        doc.add_paragraph().add_run("Aportes. ").bold = True
        doc.paragraphs[-1].add_run(r["aportes"])
        doc.add_paragraph().add_run("Vacíos. ").bold = True
        doc.paragraphs[-1].add_run(r["vacios"])
    tabla(
        doc,
        ["Artículo", "Aporte principal", "Vacío que deja", "Cómo se usa en este proyecto"],
        [
            ["Lenin et al. (2015)", "Validación y escenarios de agenda y personal", "Un solo servicio especializado", "Estructura del experimento y de la validación"],
            ["Hanly et al. (2022)", "Pruebas de estrés y herramienta interactiva", "Tiempos de servicio supuestos", "Análisis de sensibilidad y tablero comparativo"],
            ["Medina y Arrieta (2013)", "Identificación del recurso limitante", "Contexto urbano y sin costos", "Análisis de ocupación y cuellos de botella"],
        ],
    )

    doc.add_heading("4. Conclusiones", 1)
    lista(
        doc,
        [
            "La simulación se usa para decidir recursos y reglas antes de aplicarlos, y el proyecto sigue ese mismo camino con datos exportados del CRUD.",
            "El aporte propio es llevar el enfoque a un puesto de salud rural, un contexto que los casos revisados no cubren.",
            "Quedan abiertas las dimensiones de conectividad y de aceptación cultural, que requieren trabajo de campo.",
        ],
    )
    doc.add_heading("Nota sobre las fuentes", 1)
    doc.add_paragraph(
        "Las fuentes se localizaron con un asistente de IA (Claude) y sus datos bibliográficos (autores, año, revista, volumen y DOI) se verificaron en las páginas de las revistas, en PubMed Central y en Crossref. "
        "Los resúmenes se leyeron en esas páginas, pero el texto completo de los artículos debe leerlo el integrante antes de la sustentación para poder explicarlos."
    )
    doc.add_heading("Referencias", 1)
    for referencia in REFERENCIAS:
        doc.add_paragraph(referencia)
    return doc


if __name__ == "__main__":
    DESTINO.mkdir(exist_ok=True)
    b2().save(DESTINO / "Modulo_B2_Escenarios_en_Perspectiva.docx")
