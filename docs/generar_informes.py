import json
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import RGBColor, Inches, Pt

RAIZ = Path(__file__).resolve().parent.parent
SALIDAS = RAIZ / "simulacion" / "salidas"
FIGURAS_DOCS = RAIZ / "docs" / "figuras"
FIGURAS_DIAGRAMAS = RAIZ / "diagramas" / "png"
DESTINO = RAIZ / "docs" / "informes"

NOMBRES_ESCENARIOS = {
    "base": "Base",
    "cola_unica": "Fila única",
    "cola_unica_prioridad": "Fila única con prioridad",
    "medico_adicional": "Médico adicional",
    "demanda_mas_25": "Demanda +25 %",
    "demanda_mas_25_recomendado": "Demanda +25 % con fila única y prioridad",
}


def cargar(nombre):
    return json.loads((SALIDAS / nombre).read_text(encoding="utf-8"))


def documento(titulo, subtitulo):
    doc = Document()
    estilo = doc.styles["Normal"]
    estilo.font.name = "Times New Roman"
    estilo.font.size = Pt(12)
    for nombre in ("Title", "Heading 1", "Heading 2", "Heading 3"):
        doc.styles[nombre].font.color.rgb = RGBColor(0, 0, 0)
    doc.add_heading(titulo, 0)
    parrafo = doc.add_paragraph(subtitulo)
    parrafo.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return doc


def tabla(doc, encabezados, filas, pie=None):
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Light Grid Accent 1"
    for i, texto in enumerate(encabezados):
        t.rows[0].cells[i].text = str(texto)
    for fila in filas:
        celdas = t.add_row().cells
        for i, valor in enumerate(fila):
            celdas[i].text = str(valor)
    if pie:
        doc.add_paragraph(pie).runs[0].italic = True
    doc.add_paragraph()


def figura(doc, ruta, ancho=6.0, pie=None):
    doc.add_picture(str(ruta), width=Inches(ancho))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if pie:
        p = doc.add_paragraph(pie)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].italic = True


def lista(doc, elementos):
    for elemento in elementos:
        doc.add_paragraph(elemento, style="List Bullet")


def ic(m):
    return f"{m['media']:.2f} [{m['ic_inf']:.2f}; {m['ic_sup']:.2f}]"


def pesos(valor):
    return f"${valor:,.0f}".replace(",", ".")


def informe_b():
    resultados, financiero, monte = cargar("resultados.json"), cargar("financiero.json"), cargar("monte_carlo.json")
    parametros = cargar("parametros.json")
    ajuste = pd.read_csv(SALIDAS / "ajuste_distribuciones.csv")
    elegidas = ajuste[ajuste["elegida"]]
    esc = resultados["escenarios"]
    recomendado = resultados["recomendado"]
    validacion = resultados["validacion"]
    doc = documento("Informe técnico del componente B", "Modelación, simulación y análisis de decisiones para la gestión de turnos en un puesto de salud rural")

    doc.add_heading("1. Introducción", 1)
    doc.add_paragraph(
        "El proceso elegido es la asignación de turnos y la atención de pacientes en un puesto de salud rural de la vereda Fagua (Chía). "
        "Tiene los elementos que justifican una simulación: llegadas aleatorias, recursos limitados (cuatro profesionales), tiempos de servicio variables y colas. "
        "El mismo proceso lo gestiona el sistema CRUD, que registra cada cita con su hora de llegada, inicio y fin de atención."
    )
    doc.add_paragraph(
        "La simulación se ha usado para decidir recursos de urgencias y de emergencias en Colombia y en otros países "
        "(Medina Monterrosa y Arrieta-Canchila, 2013; Aguiar et al., 2022; Hernández Chinchilla et al., 2017; Xie et al., 2021; Dosi et al., 2023). "
        "En el contexto rural colombiano, las aplicaciones electrónicas de telemedicina y mHealth se estudian para el monitoreo de la salud (Sánchez Castillo et al., 2023)."
    )
    doc.add_paragraph(
        "Los datos del puesto de salud usados en este informe son sintéticos: se generaron con una semilla fija a partir de distribuciones conocidas para 60 jornadas hábiles, "
        "porque no se dispone de registros reales anonimizados. El procedimiento es el mismo que se seguiría con datos reales: exportar el histórico desde el CRUD, ajustar distribuciones, simular y decidir. "
        "Las conclusiones numéricas describen el modelo y no deben presentarse como mediciones de un puesto real."
    )

    doc.add_heading("2. Modelación del sistema (B1)", 1)
    doc.add_heading("2.1 Descripción y frontera", 2)
    doc.add_paragraph(
        "El sistema comprende desde que el paciente llega al puesto hasta que termina su consulta o se retira. Opera de 7:00 a 16:00 (540 minutos) con tres servicios: medicina general (dos médicos), "
        "enfermería y vacunación (un profesional) y odontología (un profesional). Quedan fuera de la frontera el traslado del paciente, la dispensación de medicamentos, las remisiones a otros centros y el agendamiento previo."
    )
    tabla(
        doc,
        ["Elemento", "Descripción"],
        [
            ["Entidades", "Pacientes (temporales); profesionales y servicios (permanentes)"],
            ["Atributos", "Prioridad (normal o prioritaria), servicio solicitado, hora de llegada, duración de la consulta"],
            ["Variables de estado", "Pacientes en cola por servicio, profesionales ocupados, tiempo de espera acumulado"],
            ["Eventos", "Llegada de un paciente, inicio de atención, fin de atención, cierre de la jornada"],
            ["Actividades", "Consulta con el profesional (duración aleatoria)"],
            ["Colas", "Una fila por profesional, atendida en orden de llegada"],
            ["Reglas", "Cada paciente queda en la fila de un profesional del servicio solicitado; sin prioridad"],
        ],
    )
    doc.add_heading("2.2 Diagramas estructurados", 2)
    figura(doc, FIGURAS_DIAGRAMAS / "diagrama_flujo_proceso.png", 3.5, "Figura 1. Diagrama de flujo del proceso")
    figura(doc, FIGURAS_DIAGRAMAS / "diagrama_causal.png", 3.5, "Figura 2. Diagrama causal con bucles de refuerzo (R) y balanceo (B)")
    doc.add_paragraph(
        "El bucle R1 refuerza la demanda: más pacientes atendidos aumentan la confianza de la comunidad y, con ella, las llegadas. "
        "Los bucles B1, B2 y B3 la limitan: una cola larga eleva el tiempo de espera, que provoca abandonos y reduce la confianza, y a la vez una cola mayor aumenta la atención. "
        "La capacidad de los profesionales actúa sobre el tiempo de espera y es la palanca principal de decisión."
    )
    figura(doc, FIGURAS_DIAGRAMAS / "diagrama_flujos_niveles.png", 3.5, "Figura 3. Diagrama de flujos y niveles (Vensim, archivo turnos_flujos_niveles.mdl)")
    vensim = pd.read_csv(RAIZ / "diagramas" / "resultados_vensim.csv")
    doc.add_paragraph(
        "El modelo de flujos y niveles agrega los tres servicios en una sola cola, por lo que describe la tendencia del sistema y no sus tiempos de espera por servicio. "
        "Ejecutado con una jornada de 9 horas, produce los resultados siguientes."
    )
    tabla(
        doc,
        ["Escenario", "Atendidos", "Abandonos", "Cola máxima", "Espera máx. (min)", "Confianza final"],
        [[r.escenario, r.atendidos, r.abandonos, r.cola_maxima, r.espera_maxima_min, r.confianza_final] for r in vensim.itertuples()],
    )
    figura(doc, FIGURAS_DIAGRAMAS / "arbol_problemas.png", 3.5, "Figura 4. Árbol de problemas")
    doc.add_heading("2.3 Supuestos, simplificaciones y limitaciones", 2)
    lista(
        doc,
        [
            "Las llegadas de cada servicio son independientes y estacionarias durante la jornada; no se modelan picos por hora.",
            "Los pacientes no abandonan en el modelo de simulación: el abandono solo se considera en el modelo de dinámica de sistemas.",
            "Los profesionales no tienen descansos ni ausencias, salvo en el ejercicio de Monte Carlo.",
            "Cada paciente solicita un único servicio por visita.",
            "La jornada empieza con el puesto vacío y se atiende a todos los pacientes que llegaron antes del cierre.",
            "Los datos son sintéticos; la validación demuestra la coherencia interna del procedimiento, no la fidelidad a un puesto real.",
        ],
    )

    doc.add_heading("3. Análisis de datos de entrada", 1)
    doc.add_paragraph(
        f"Se exportaron desde el CRUD {int(parametros['Medicina general']['llegadas']['observaciones'] + parametros['Enfermería y vacunación']['llegadas']['observaciones'] + parametros['Odontología']['llegadas']['observaciones'])} "
        "tiempos entre llegadas y las duraciones de consulta de las citas atendidas. Para cada variable se ajustaron las distribuciones exponencial, gamma, lognormal, Weibull y normal por máxima verosimilitud. "
        "Cada ajuste se contrastó con Kolmogorov-Smirnov y chi-cuadrado (10 clases equiprobables, nivel 5 %), y entre las no rechazadas se eligió la de menor AIC."
    )
    tabla(
        doc,
        ["Servicio", "Variable", "Distribución", "n", "KS (p)", "Chi² (p)"],
        [[r.servicio, r.variable, r.distribucion, r.n, f"{r.ks_p:.3f}", f"{r.chi2_p:.3f}"] for r in elegidas.itertuples()],
    )
    doc.add_paragraph(
        "El valor p de KS con parámetros estimados es aproximado. La tasa de llegadas incluye el último intervalo censurado por el cierre de la jornada."
    )

    doc.add_heading("4. Diseño del modelo de simulación", 1)
    doc.add_paragraph(
        "El modelo de eventos discretos se construyó en SimPy: cada servicio es una fila, los pacientes son las entidades, los profesionales son los recursos y la jornada dura 540 minutos."
    )

    doc.add_heading("5. Verificación y validación", 1)
    lista(
        doc,
        [
            "Verificación: pruebas de consistencia (más recursos reducen la espera; más demanda la aumenta; la prioridad favorece a los prioritarios).",
            "Casos extremos: con capacidad ampliada la espera tiende a cero y con demanda +40 % crece de forma marcada (véase sensibilidad).",
            "Validación: comparación de la espera media diaria real (60 jornadas) con la simulada (400 jornadas).",
        ],
    )
    tabla(
        doc,
        ["Medida", "Real", "Simulado"],
        [["Espera media diaria (min)", validacion["espera_diaria_real_media"], validacion["espera_diaria_simulada_media"]]],
    )
    doc.add_paragraph(
        f"Con la prueba t de Welch (p = {str(validacion['welch_t_p']).replace('.', ',')}), la de Kolmogorov-Smirnov de dos muestras (p = {str(validacion['ks_dos_muestras_p']).replace('.', ',')}) y la de Mann-Whitney (p = {str(validacion['mann_whitney_p']).replace('.', ',')}) "
        f"no se rechaza la igualdad. {validacion['conclusion']}."
    )

    doc.add_heading("6. Diseño de experimentos y escenarios", 1)
    cfg = resultados["configuracion"]
    doc.add_paragraph(
        f"Cada réplica simula {cfg['jornadas_por_replica']} jornadas independientes y se realizaron {cfg['replicas']} réplicas por escenario, con intervalos de confianza del 95 % basados en la t de Student. "
        "Como cada jornada comienza con el puesto vacío y termina cuando se atiende al último paciente, el sistema es de horizonte finito y no existe régimen transitorio entre jornadas: el periodo de calentamiento es cero. "
        "Las réplicas usan semillas comunes entre escenarios para que las diferencias se calculen por pares."
    )
    tabla(
        doc,
        ["Escenario", "Descripción"],
        [[NOMBRES_ESCENARIOS[n], e["descripcion"]] for n, e in esc.items()],
    )

    doc.add_heading("7. Resultados", 1)
    tabla(
        doc,
        ["Escenario", "Espera media (min)", "Espera prioritarios (min)", "Ocupación (%)"],
        [
            [NOMBRES_ESCENARIOS[n], ic(e["metricas"]["espera_media_min"]), ic(e["metricas"]["espera_prioritarios_min"]), ic(e["metricas"]["ocupacion_pct"])]
            for n, e in esc.items()
        ],
        "Media [IC 95 %]",
    )
    figura(doc, SALIDAS / "espera_escenarios.png", 3.5, "Figura 5. Espera media por escenario")
    tabla(
        doc,
        ["Escenario frente al base", "Diferencia en espera media (min)", "Diferencia en espera prioritarios (min)"],
        [
            [NOMBRES_ESCENARIOS[n], ic(e["diferencia_vs_base"]["espera_media_min"]), ic(e["diferencia_vs_base"]["espera_prioritarios_min"])]
            for n, e in esc.items()
            if n != "base"
        ],
        "Diferencia de medias pareada [IC 95 %]; un intervalo que no contiene el cero indica diferencia significativa.",
    )
    cuellos = resultados["cuellos_de_botella_ocupacion_pct"]
    doc.add_paragraph(
        "Cuellos de botella: la ocupación de los servicios en el escenario base es " + ", ".join(f"{s} {v:.1f} %" for s, v in cuellos.items()) +
        ". El servicio más cargado concentra la espera y es el candidato a reforzar."
    )
    doc.add_heading("7.1 Análisis de sensibilidad", 2)
    sensibilidad = pd.DataFrame(resultados["sensibilidad"])
    tabla(
        doc,
        ["Escenario", "Demanda", "Duración de consulta", "Espera media (min)", "Ocupación (%)"],
        [[NOMBRES_ESCENARIOS.get(r.escenario, r.escenario), f"x{r.factor_demanda}", f"x{r.factor_servicio}", f"{r.espera_media_min:.2f}", f"{r.ocupacion_pct:.1f}"] for r in sensibilidad.itertuples()],
    )
    doc.add_heading("7.2 Decisión recomendada", 2)
    doc.add_paragraph(
        f"Se recomienda el escenario «{NOMBRES_ESCENARIOS[recomendado]}». Reduce la espera media en {abs(esc[recomendado]['diferencia_vs_base']['espera_media_min']['media']):.1f} minutos "
        f"y la de los pacientes prioritarios en {abs(esc[recomendado]['diferencia_vs_base']['espera_prioritarios_min']['media']):.1f} minutos, sin contratar personal. "
        "El criterio de elección fue minimizar 0,7 veces la espera media más 0,3 veces la espera de prioritarios entre las alternativas sin costo adicional de personal. "
        "La contratación de un médico adicional logra una reducción de espera comparable al reorganizar las filas, pero con un costo anual mucho mayor (sección 9)."
    )

    doc.add_heading("8. Método de Monte Carlo", 1)
    doc.add_paragraph(
        f"Se simularon {monte['iteraciones']:,} jornadas".replace(",", ".") +
        " con incertidumbre en la demanda (multiplicador lognormal con sigma 0,15), en la duración de las consultas (factor triangular 0,9; 1,0; 1,3) y en la presencia de los profesionales "
        "(5 % de probabilidad de ausencia por profesional y día). Cuando un servicio queda sin profesionales sus pacientes no se atienden."
    )
    actual, propuesta = monte["sistema_actual"], monte["fila_unica"]
    tabla(
        doc,
        ["Indicador", "Sistema actual", "Fila única"],
        [
            ["Media de la espera diaria (min)", actual["media"], propuesta["media"]],
            ["Percentil 50", actual["p50"], propuesta["p50"]],
            ["Percentil 90", actual["p90"], propuesta["p90"]],
            ["Percentil 95", actual["p95"], propuesta["p95"]],
            ["Percentil 99", actual["p99"], propuesta["p99"]],
            ["Probabilidad de superar 30 min", f"{100 * actual['probabilidad_superar_umbral']:.1f} %", f"{100 * propuesta['probabilidad_superar_umbral']:.1f} %"],
            ["Pacientes sin atender por día", actual["pacientes_sin_atender_por_dia"], propuesta["pacientes_sin_atender_por_dia"]],
        ],
    )
    figura(doc, SALIDAS / "monte_carlo_histograma.png", 3.5, "Figura 6. Distribución de la espera media diaria")
    doc.add_paragraph(
        f"Interpretación: en el 90 % de las jornadas del sistema actual la espera media no supera {actual['p90']} minutos, frente a {propuesta['p90']} con fila única. "
        "La cola larga de la distribución (percentil 99) se asocia, según el diseño del ejercicio, con las jornadas en que falta un profesional (no se aisló su efecto por separado), por lo que la fila única no elimina el riesgo de las jornadas críticas; "
        "para esas jornadas se necesita un plan de reemplazo."
    )

    doc.add_heading("9. Modelo financiero", 1)
    doc.add_paragraph("El análisis financiero usa los conceptos de flujo de caja, valor presente neto y sensibilidad de Pérez Peña (2019).")
    sup, fu, med = financiero["supuestos"], financiero["fila_unica_con_prioridad"], financiero["medico_adicional"]
    doc.add_paragraph(
        "El beneficio se valora como el tiempo de espera que los pacientes dejan de perder. Los valores monetarios son supuestos del equipo, no cifras verificadas, y deben reemplazarse por datos reales antes de decidir."
    )
    tabla(
        doc,
        ["Supuesto", "Valor"],
        [
            ["Jornadas por año", sup["jornadas_por_anio"]],
            ["Citas por día", sup["citas_por_dia"]],
            ["Minutos de espera ahorrados por cita", round(sup["minutos_ahorrados_por_cita"], 2)],
            ["Valor del minuto del paciente", pesos(sup["valor_minuto_paciente"])],
            ["Inversión inicial (desarrollo y capacitación)", pesos(sup["inversion_inicial"])],
            ["Costo anual de operación", pesos(sup["costo_operacion_anual"])],
            ["Tasa de descuento", f"{100 * sup['tasa_descuento']:.0f} %"],
            ["Horizonte", "5 años"],
        ],
    )
    tabla(
        doc,
        ["Indicador", "Fila única con prioridad", "Médico adicional"],
        [
            ["Beneficio anual", pesos(fu["beneficio_anual"]), pesos(med["beneficio_anual"])],
            ["Valor presente neto", pesos(fu["vpn"]), pesos(med["vpn"])],
            ["Tasa interna de retorno", f"{100 * fu['tir']:.1f} %" if fu["tir"] else "No existe", f"{100 * med['tir']:.1f} %" if med["tir"] else "No existe"],
            ["Relación beneficio/costo", fu["relacion_beneficio_costo"], med["relacion_beneficio_costo"]],
            ["Recuperación (años)", fu["recuperacion_anios"], med["recuperacion_anios"] or "No se recupera"],
            ["Cobertura de la operación (beneficio/costo anual)", fu["sostenibilidad_cobertura_operacion"], med["sostenibilidad_cobertura_operacion"]],
        ],
    )
    doc.add_paragraph("Flujo de caja de la fila única con prioridad (año 0 a 5): " + ", ".join(pesos(v) for v in fu["flujo_de_caja"]) + ".")
    tabla(
        doc,
        ["Variable incierta", "Valor bajo", "Valor alto", "VPN bajo", "VPN alto"],
        [[s["variable"], round(s["valor_bajo"], 3), round(s["valor_alto"], 3), pesos(s["vpn_bajo"]), pesos(s["vpn_alto"])] for s in financiero["sensibilidad_vpn"]],
        "Análisis de sensibilidad univariado del VPN.",
    )
    mc = financiero["monte_carlo_vpn"]
    figura(doc, SALIDAS / "financiero_vpn.png", 3.5, "Figura 7. Distribución del VPN con 10 000 iteraciones")
    doc.add_paragraph(
        f"Con incertidumbre simultánea en las variables, el VPN medio es {pesos(mc['media'])}, con un intervalo entre percentiles 5 y 95 de {pesos(mc['p5'])} a {pesos(mc['p95'])}, "
        f"y probabilidad de VPN positivo de {100 * mc['probabilidad_vpn_positivo']:.1f} %. La variable que más mueve el resultado es el valor asignado al tiempo del paciente, "
        "de modo que la conclusión es robusta frente a los costos pero depende de ese supuesto."
    )

    doc.add_heading("10. Integración con el sistema CRUD", 1)
    tabla(
        doc,
        ["Eslabón", "Evidencia"],
        [
            ["Problema", "Esperas largas y desiguales en el puesto de salud (árbol de problemas)"],
            ["Datos", "Exportación `citas_historicas.csv` desde el endpoint `/api/exportar/citas.csv` y el script de exportación"],
            ["Modelo", "Ajuste de distribuciones y modelo SimPy validado"],
            ["Escenarios", f"Seis escenarios con 30 réplicas e IC del 95 %; recomendado: {NOMBRES_ESCENARIOS[recomendado]}"],
            ["Decisión", "Fila única por servicio con prioridad a pacientes prioritarios"],
            ["Cambio 1", "Cola de atención ordenada por prioridad y llegada (`/api/citas/cola`) y profesional sugerido con menor carga (`/api/citas/profesional-sugerido`)"],
            ["Cambio 2", "Alertas de capacidad cuando la espera media por servicio supera el umbral (`/api/alertas/capacidad`)"],
            ["Tablero", "El tablero compara los indicadores reales con los proyectados por la simulación (`/api/tablero`)"],
        ],
    )

    doc.add_heading("11. Reflexión ética (B5)", 1)
    doc.add_paragraph(
        "Las decisiones que se derivan de una simulación afectan a personas, por lo que el ingeniero responde por la calidad del modelo y por el uso que se hace de sus resultados "
        "(Bilbao Alberdi, 2010). Se analizan cinco aspectos."
    )
    doc.add_heading("Sesgos en los datos", 2)
    doc.add_paragraph(
        "El histórico solo contiene a quienes llegaron y fueron atendidos. Los pacientes que no pudieron llegar por distancia, conectividad o falta de transporte no aparecen, "
        "de modo que la demanda real puede ser mayor y distinta. Los ajustes se hicieron con citas atendidas, lo que subestima la carga; cualquier decisión de capacidad debe contrastarse con la demanda no registrada."
    )
    doc.add_heading("Privacidad de los datos de salud", 2)
    doc.add_paragraph(
        "Los registros de pacientes son datos personales sensibles. El sistema limita su lectura por rol, registra quién consulta y modifica cada registro y exporta para la simulación únicamente "
        "tiempos y servicios, sin nombres ni documentos. Antes de usar datos reales se requiere autorización de tratamiento y anonimización, y conservar la exportación bajo control de acceso."
    )
    doc.add_heading("Equidad en la asignación", 2)
    doc.add_paragraph(
        "La prioridad reduce de forma importante la espera de los pacientes prioritarios, pero deja igual la de los demás. Debe definirse con criterios clínicos transparentes quién es prioritario, "
        "y vigilar que el tiempo de espera de los demás no se degrade en los días de alta demanda ni que la regla discrimine por edad, vereda o condición social."
    )
    doc.add_heading("Uso del modelo fuera de su dominio de validez", 2)
    doc.add_paragraph(
        "El modelo se validó para un puesto con tres servicios y una demanda cercana a 76 citas diarias. No debe extrapolarse a otro puesto, a brotes epidemiológicos, a campañas de vacunación "
        "ni a demandas muy superiores a las probadas en la sensibilidad (+40 %). Los resultados financieros dependen de supuestos que el equipo no verificó."
    )
    doc.add_heading("Responsabilidad del ingeniero", 2)
    doc.add_paragraph(
        "La responsabilidad incluye declarar los supuestos, comunicar la incertidumbre mediante intervalos y no presentar la simulación como una predicción exacta. "
        "La decisión final corresponde a las personas responsables del puesto de salud, y el sistema debe permitir revertir la regla de prioridad si produce efectos no deseados."
    )

    doc.add_heading("12. Declaración de uso de herramientas de IA", 1)
    doc.add_paragraph(
        "Se usó el asistente Claude (Anthropic) para escribir código, scripts, modelos y borradores. El equipo verificó el resultado con las pruebas automáticas, "
        "la revisión de resultados estadísticos y la prueba de la interfaz. Cada integrante debe poder explicar cualquier parte de lo entregado."
    )

    doc.add_heading("13. Conclusiones", 1)
    lista(
        doc,
        [
            f"Una fila única por servicio con prioridad reduce la espera media de {esc['base']['metricas']['espera_media_min']['media']:.1f} a {esc[recomendado]['metricas']['espera_media_min']['media']:.1f} minutos sin costo de personal.",
            "El modelo reproduce el comportamiento de los datos (p > 0,05), con la salvedad de que los datos son sintéticos.",
            "Las ausencias de profesionales generan las jornadas críticas y requieren un plan de contingencia.",
            "Contratar un médico adicional no es financieramente sostenible con los supuestos adoptados.",
        ],
    )
    doc.add_heading("Pendientes del módulo B2", 1)
    doc.add_paragraph(
        "El mapa comparativo con al menos tres casos locales y tres globales, el análisis crítico y la reseña de dos artículos arbitrados (uno en inglés) requieren fuentes verificadas por el equipo "
        "y no se redactaron en este documento para no incluir referencias sin comprobar."
    )
    doc.add_heading("Referencias", 1)
    for referencia in (
        "Aguiar, C., Rentería, S., Catumba-Ruiz, J. C., & Barrera, D. (2022). Use of discrete event simulation and genetic algorithms to estimate the necessary resources to respond in a timely manner in the Medical Emergency System in Bogotá. Medwave, 22(3), e002100. https://doi.org/10.5867/medwave.2022.03.002100",
        "Bilbao Alberdi, G. (2010). Ética para ingenieros.",
        "Dosi, C., Iori, M., Kramer, A., & Vignoli, M. (2023). Successful implementation of discrete event simulation: Integrating design thinking and simulation approach in an emergency department. Production Planning & Control, 34(13), 1233–1247. https://doi.org/10.1080/09537287.2021.1996651",
        "Hernández Chinchilla, D., Camacho Oliveros, M. Á., & Duarte Forero, E. L. (2017). Análisis del flujo de pacientes en el servicio de urgencias del Hospital Universitario La Samaritana a través de simulación discreta. Avances Investigación en Ingeniería, 14. https://doi.org/10.18041/1794-4953/avances.1.1289",
        "Medina Monterrosa, Y., & Arrieta-Canchila, K. (2013). Simulación de eventos discretos para optimizar recursos restrictivos del servicio de urgencias de un hospital. Revista Científica Teknos, 13(1), 55–66.",
        "Pérez Peña, R. (2019). Modelación financiera: conceptos y aplicaciones.",
        "Sánchez Castillo, V., Gómez Cano, C. A., & Gonzalez-Argote, J. (2023). Telemedicine and mHealth applications for health monitoring in rural communities in Colombia: A systematic review. EAI Endorsed Transactions on Pervasive Health and Technology, 9(1). https://doi.org/10.4108/eetpht.9.3400",
        "Team SimPy. (s. f.). SimPy: Discrete event simulation for Python (versión 4.1.2) [Software]. https://simpy.readthedocs.io",
        "Ventana Systems. (s. f.). Vensim PLE (versión 11.0) [Software]. https://vensim.com",
        "Xie, J., Zhuang, W., Ang, M., Chou, M. C., Luo, L., & Yao, D. D. (2021). Analytics for hospital resource planning: Two case studies. Production and Operations Management. https://doi.org/10.1111/poms.13158",
    ):
        pr = doc.add_paragraph(referencia)
        pr.paragraph_format.left_indent = Inches(0.5)
        pr.paragraph_format.first_line_indent = Inches(-0.5)
    return doc


def documento_a():
    doc = documento("Documentación del componente A", "Sistema CRUD para la gestión de turnos en un puesto de salud rural")
    doc.add_heading("1. Especificación de requisitos", 1)
    tabla(
        doc,
        ["Historia de usuario", "Criterios de aceptación"],
        [
            ["Como administrador quiero gestionar usuarios y roles para controlar el acceso", "Solo el administrador crea, edita y elimina usuarios; la clave exige 8 caracteres con letras y números; no se muestra el hash"],
            ["Como operador quiero registrar pacientes y citas para organizar la atención", "Los datos se validan en cliente y servidor; el documento es único; la cita exige un profesional de la sede que preste el servicio"],
            ["Como operador quiero ver la cola de atención para saber a quién llamar", "La cola muestra primero a los prioritarios y luego por hora de llegada"],
            ["Como operador quiero saber qué profesional tiene menos carga para asignar la cita", "El sistema devuelve el profesional del servicio con menos citas programadas"],
            ["Como usuario de consulta quiero ver reportes para conocer el desempeño", "Hay tres reportes con filtro de fechas y descarga en CSV"],
            ["Como administrador quiero auditar los cambios para saber quién modificó qué", "Cada creación, actualización y eliminación guarda usuario, entidad, acción y fecha"],
            ["Como analista quiero exportar el histórico para alimentar la simulación", "El CSV incluye servicio, profesional, llegada, inicio, fin, espera y atención"],
            ["Como jefe del puesto quiero un tablero que compare lo real con lo simulado", "El tablero muestra indicadores reales, proyectados y alertas de capacidad"],
        ],
    )
    doc.add_heading("2. Requisitos no funcionales", 1)
    lista(
        doc,
        [
            "Seguridad: hash scrypt con sal, JWT, consultas parametrizadas, cabeceras de seguridad, secretos por variables de entorno y HTTPS con Caddy.",
            "Calidad: pruebas unitarias y de integración con cobertura superior al 60 % en la capa de negocio, ejecutadas en cada push mediante GitHub Actions.",
            "Despliegue: `docker compose` con PostgreSQL, API y proxy.",
            "Usabilidad: diseño responsivo, etiquetas en los campos y mensajes de error claros.",
        ],
    )
    doc.add_heading("3. Modelo de datos", 1)
    doc.add_paragraph(
        "El modelo está en tercera forma normal: cada atributo depende de la clave de su tabla y no hay dependencias transitivas. La relación muchos a muchos entre profesionales y servicios se resuelve con la tabla `profesional_servicio`. "
        "El borrado es lógico (columna `eliminado`) en usuarios, sedes, servicios, profesionales, pacientes y citas. El script de creación está en `docs/esquema.sql` y los datos de prueba se generan con `scripts/sembrar_datos.py` (700 pacientes y más de 4 000 citas)."
    )
    figura(doc, FIGURAS_DOCS / "erd.png", 6.3, "Figura 1. Diagrama entidad-relación")
    doc.add_heading("4. Arquitectura", 1)
    doc.add_paragraph(
        "La aplicación sigue una arquitectura por capas: los routers reciben y validan solicitudes (presentación), el paquete `negocio` aplica las reglas y calcula los reportes, y `recursos`, `consultas` y `models` acceden a los datos. "
        "Se eligió FastAPI por la validación declarativa con Pydantic y la generación automática de OpenAPI; SQLAlchemy permite usar SQLite en pruebas y PostgreSQL en producción con el mismo código. "
        "La interfaz es HTML y JavaScript sin dependencias, lo que reduce la superficie de ataque y facilita su revisión."
    )
    figura(doc, FIGURAS_DOCS / "arquitectura.png", 6.3, "Figura 2. Arquitectura")
    doc.add_heading("5. Diagramas UML", 1)
    figura(doc, FIGURAS_DOCS / "casos_de_uso.png", 6.0, "Figura 3. Casos de uso")
    figura(doc, FIGURAS_DOCS / "secuencia_login.png", 6.0, "Figura 4. Secuencia de inicio de sesión y consulta")
    figura(doc, FIGURAS_DOCS / "secuencia_cita.png", 6.0, "Figura 5. Secuencia de registro de una cita")
    doc.add_heading("6. API REST", 1)
    doc.add_paragraph("La especificación OpenAPI se exporta a `docs/openapi.json` y la interfaz interactiva está disponible en `/docs`. Los recursos principales son:")
    tabla(
        doc,
        ["Ruta", "Métodos", "Roles"],
        [
            ["/api/auth/login", "POST", "Público"],
            ["/api/pacientes, /api/citas, /api/profesionales, /api/servicios, /api/sedes", "GET, POST, PUT, DELETE", "Lectura: todos; escritura: administrador y operador; eliminación: administrador"],
            ["/api/usuarios", "GET, POST, PUT, DELETE", "Administrador"],
            ["/api/reportes/{tiempos|ocupacion|volumen}", "GET (JSON o CSV)", "Todos"],
            ["/api/exportar/citas.csv", "GET", "Administrador y operador"],
            ["/api/citas/cola, /api/citas/profesional-sugerido", "GET", "Todos / escritura"],
            ["/api/alertas/capacidad, /api/tablero", "GET", "Todos"],
            ["/api/auditoria", "GET", "Administrador"],
        ],
    )
    doc.add_heading("7. Manual de usuario", 1)
    lista(
        doc,
        [
            "Ingreso: escriba su correo y clave y pulse «Ingresar». La sesión se cierra con «Salir».",
            "Listados: use el cuadro de búsqueda, haga clic en un encabezado para ordenar y use «Anterior» y «Siguiente» para paginar.",
            "Crear y editar: pulse «Nuevo» o «Editar», complete el formulario y pulse «Guardar». Los errores se muestran en el mismo formulario.",
            "Citas: indique el documento del paciente, la sede, el servicio, el profesional y la hora de llegada. Marque como atendida e ingrese inicio y fin cuando termine la consulta.",
            "Cola: elija la sede para ver el orden de atención.",
            "Reportes: elija el reporte, filtre por fechas y pulse «Consultar» o «Descargar CSV».",
            "Tablero: compara la espera y la ocupación reales con las simuladas y muestra las alertas de capacidad.",
            "Eliminar (solo administrador): el registro queda marcado como eliminado y deja de mostrarse.",
        ],
    )
    doc.add_heading("8. Manual técnico", 1)
    doc.add_paragraph("Las instrucciones de instalación, ejecución con Docker, pruebas y reproducción de la simulación están en el archivo README.md del repositorio.")
    tabla(
        doc,
        ["Variable de entorno", "Uso"],
        [
            ["SECRET_KEY", "Firma de los tokens JWT (obligatoria)"],
            ["DATABASE_URL", "Cadena de conexión SQLAlchemy"],
            ["TOKEN_MINUTOS", "Duración del token"],
            ["UMBRAL_ESPERA_MIN", "Umbral de las alertas de capacidad"],
            ["RESULTADOS_SIMULACION", "Ruta del JSON con los resultados de la simulación"],
            ["POSTGRES_PASSWORD", "Clave de la base de datos en docker-compose"],
        ],
    )
    doc.add_heading("9. Pruebas", 1)
    doc.add_paragraph(
        "Las pruebas de integración recorren la API con cada rol (autenticación, permisos, CRUD, borrado lógico, validaciones, conflictos, paginación, auditoría, reportes y tablero) y las unitarias verifican el hash, los tokens y los cálculos de negocio. "
        "El pipeline de GitHub Actions las ejecuta en cada push y exige una cobertura mínima del 60 %."
    )
    doc.add_heading("10. Pendiente: revisión de usabilidad", 1)
    doc.add_paragraph("El enunciado exige una revisión con al menos cinco usuarios reales o simulados. Esa revisión debe realizarla el equipo y registrarse en la siguiente tabla.")
    tabla(doc, ["Usuario", "Tarea probada", "Hallazgo", "Ajuste realizado"], [["", "", "", ""] for _ in range(5)])
    return doc


def documento_bitacora():
    doc = documento("Bitácora y cronograma del equipo", "Planeación del proyecto integrador (módulo B6)")
    doc.add_heading("1. Objetivos", 1)
    lista(
        doc,
        [
            "Construir un CRUD completo y seguro para la gestión de turnos de un puesto de salud rural.",
            "Modelar y simular el proceso con datos del CRUD y recomendar una decisión con evidencia estadística.",
            "Traducir la decisión en cambios del sistema y en un tablero comparativo.",
        ],
    )
    doc.add_heading("2. Roles", 1)
    tabla(
        doc,
        ["Integrante", "Roles", "Responsabilidades"],
        [["Gaddiel Esteban Nieto Rojas", "Líder, desarrollo, simulación y documentación", "Todas las tareas del proyecto: sistema CRUD, modelo de simulación, modelos de Vensim, informes, pruebas, despliegue y sustentación"]],
    )
    doc.add_heading("3. Cronograma", 1)
    figura(doc, FIGURAS_DOCS / "gantt.png", 6.5, "Figura 1. Diagrama de Gantt")
    tabla(
        doc,
        ["Hito", "Semana", "Entregable"],
        [
            ["PC1", 2, "Propuesta aprobada, árbol de problemas y alcance"],
            ["PC2", 4, "Requisitos, modelo entidad-relación, arquitectura y plan"],
            ["PC3", 7, "CRUD núcleo funcionando, mapa comparativo y análisis crítico"],
            ["PC4", 9, "Modelo base validado y reportes del CRUD"],
            ["PC5", 11, "Informe técnico B3 y B4, versión candidata y video de B5"],
            ["Entrega final", 12, "Sistema, informes, simulación y sustentación"],
        ],
    )
    doc.add_heading("4. Riesgos", 1)
    tabla(
        doc,
        ["Riesgo", "Probabilidad", "Impacto", "Mitigación"],
        [
            ["No disponer de datos reales del puesto de salud", "Alta", "Alto", "Usar datos sintéticos declarados y dejar el procedimiento listo para datos reales"],
            ["Modelo de simulación sin validar", "Media", "Alto", "Pruebas estadísticas contra el histórico y verificación cruzada con otra implementación"],
            ["Fallas en el despliegue el día de la sustentación", "Media", "Alto", "Docker reproducible, ensayo completo y copia local"],
            ["Desigualdad en las contribuciones del equipo", "Media", "Medio", "Commits frecuentes por integrante y bitácora semanal"],
            ["Exposición de datos de salud", "Baja", "Alto", "Roles, auditoría, exportación sin identificadores y secretos por variables de entorno"],
        ],
    )
    doc.add_heading("5. Bitácora semanal", 1)
    doc.add_paragraph("Las semanas siguen las fases del cronograma. Ajuste las fechas reales de cada registro si el profesor las pide. Todas las tareas las realizó el único integrante, Gaddiel Esteban Nieto Rojas.")
    tabla(
        doc,
        ["Semana", "Qué se hizo", "Dificultades", "Decisiones"],
        [
            ["1", "Lectura del enunciado, elección del proceso (turnos en un puesto de salud rural de Chía) y árbol de problemas", "No se dispone de datos reales del puesto", "Usar datos sintéticos con semilla fija y declararlo en los informes"],
            ["2", "Propuesta y alcance (PC1), diagrama de flujo del proceso y descripción del sistema", "Delimitar la frontera del sistema", "Tres servicios, cuatro profesionales y jornada de 7:00 a 16:00"],
            ["3", "Requisitos, historias de usuario y modelo entidad-relación en tercera forma normal", "Resolver la relación entre profesionales y servicios", "Tabla intermedia `profesional_servicio` (muchos a muchos) y borrado lógico"],
            ["4", "Arquitectura por capas, plan y bitácora, repositorio y pipeline de CI (PC2)", "Vensim modela dinámica de sistemas y no eventos discretos", "Vensim para el módulo B1 y SimPy para la simulación del módulo B3"],
            ["5", "Modelo de datos, seguridad (scrypt y JWT), auditoría y autenticación con tres roles", "El validador de correos rechazó el dominio `.local` de los usuarios de prueba", "Usar el dominio `saludrural.co`"],
            ["6", "CRUD genérico con permisos por rol, búsqueda, orden, filtros y paginación en el servidor, y pruebas", "Un documento duplicado producía un error 500 al insertar", "Capturar el conflicto al insertar y responder 409"],
            ["7", "Interfaz web con validaciones en cliente, Docker, Caddy con HTTPS y mapa comparativo (PC3)", "La política CSP estricta bloquea scripts y estilos en línea", "Mantener todo el JavaScript y los estilos en archivos propios"],
            ["8", "Datos de prueba (700 pacientes y 4 467 citas), reportes y exportación a CSV", "Medir la espera por servicio sin depender del motor de base de datos", "Calcular los reportes en la capa de negocio"],
            ["9", "Ajuste de distribuciones (KS y chi-cuadrado), modelo SimPy y validación (PC4)", "La validación rechazaba el modelo por sobreestimar la tasa de llegadas", "Corregir la tasa incluyendo el intervalo censurado del cierre de jornada"],
            ["10", "Escenarios con 30 réplicas e intervalos de confianza, sensibilidad y Monte Carlo", "El Monte Carlo y el modelo detallado diferían por la incertidumbre añadida", "Fijar la incertidumbre en cero en la prueba cruzada"],
            ["11", "Modelo financiero, cola priorizada, alertas, tablero y modelos de Vensim (PC5)", "El instalador de Vensim PLE no admite modo silencioso", "Instalarlo con interfaz y validar los modelos en el programa"],
            ["12", "Informes, módulo B2, encuesta de usabilidad en Google Forms, prueba del despliegue con Docker y ensayo de la sustentación", "Ninguna dificultad nueva", "Entregar con la declaración de uso de IA"],
        ],
    )
    return doc


def generar():
    DESTINO.mkdir(exist_ok=True)
    informe_b().save(DESTINO / "Informe_Tecnico_Componente_B.docx")
    documento_a().save(DESTINO / "Documentacion_Componente_A.docx")
    documento_bitacora().save(DESTINO / "Bitacora_y_Cronograma.docx")


if __name__ == "__main__":
    generar()
