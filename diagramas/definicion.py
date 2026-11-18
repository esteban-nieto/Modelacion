CONTROLES = {"FINAL TIME": 12, "INITIAL TIME": 0, "TIME STEP": 0.0625}

NIVELES = {
    "Cola de espera": {"x": 400, "y": 300, "inicial": 0, "unidades": "pacientes", "nota": "Pacientes esperando turno"},
    "En atencion": {"x": 650, "y": 300, "inicial": 0, "unidades": "pacientes", "nota": "Pacientes siendo atendidos"},
    "Atendidos": {"x": 900, "y": 300, "inicial": 0, "unidades": "pacientes", "nota": "Pacientes atendidos en la jornada"},
    "Abandonos acumulados": {"x": 400, "y": 540, "inicial": 0, "unidades": "pacientes", "nota": "Pacientes que se retiran sin atencion"},
    "Confianza comunitaria": {"x": 400, "y": 100, "inicial": 0.75, "unidades": "Dmnl", "nota": "Confianza de la comunidad en el puesto de salud"},
}

FLUJOS = {
    "Llegadas": {
        "x": 300, "y": 300, "desde": None, "hacia": "Cola de espera", "nube": (200, 300),
        "ecuacion": "IF THEN ELSE(Time<Duracion de jornada, Tasa base de llegadas*Factor de demanda*Efecto de la confianza, 0)",
        "unidades": "pacientes/Hora", "nota": "Llegada de pacientes durante la jornada",
    },
    "Inicio de atencion": {
        "x": 525, "y": 300, "desde": "Cola de espera", "hacia": "En atencion",
        "ecuacion": "MIN(Cola de espera/TIME STEP, Profesionales libres/TIME STEP)",
        "unidades": "pacientes/Hora", "nota": "Pacientes que pasan a consulta",
    },
    "Fin de atencion": {
        "x": 775, "y": 300, "desde": "En atencion", "hacia": "Atendidos",
        "ecuacion": "En atencion/Duracion de atencion",
        "unidades": "pacientes/Hora", "nota": "Pacientes que terminan su consulta",
    },
    "Abandonos": {
        "x": 400, "y": 420, "desde": "Cola de espera", "hacia": "Abandonos acumulados",
        "ecuacion": "Cola de espera*Fraccion de abandono",
        "unidades": "pacientes/Hora", "nota": "Pacientes que se retiran por la espera",
    },
    "Ganancia de confianza": {
        "x": 300, "y": 100, "desde": None, "hacia": "Confianza comunitaria", "nube": (200, 100),
        "ecuacion": "Fin de atencion*Efecto por atencion",
        "unidades": "1/Hora", "nota": "La atencion oportuna aumenta la confianza",
    },
    "Perdida de confianza": {
        "x": 500, "y": 100, "desde": "Confianza comunitaria", "hacia": None, "nube": (600, 100),
        "ecuacion": "Abandonos*Efecto por abandono+MAX(Tiempo de espera estimado-Tolerancia de espera, 0)*Efecto por espera larga",
        "unidades": "1/Hora", "nota": "Abandonos y esperas largas reducen la confianza",
    },
}

AUXILIARES = {
    "Efecto de la confianza": {"x": 300, "y": 200, "ecuacion": "0.4+0.8*MAX(0, MIN(1, Confianza comunitaria))", "unidades": "Dmnl", "nota": "Factor de demanda segun la confianza"},
    "Profesionales libres": {"x": 650, "y": 420, "ecuacion": "MAX(Profesionales-En atencion, 0)", "unidades": "profesionales", "nota": "Profesionales sin paciente"},
    "Capacidad de atencion": {"x": 760, "y": 480, "ecuacion": "Profesionales/Duracion de atencion", "unidades": "pacientes/Hora", "nota": "Pacientes que el puesto puede atender por hora"},
    "Tiempo de espera estimado": {"x": 560, "y": 540, "ecuacion": "Cola de espera/Capacidad de atencion", "unidades": "Hora", "nota": "Espera esperada para quien llega"},
    "Fraccion de abandono": {"x": 520, "y": 440, "ecuacion": "MIN(0.5, Sensibilidad al abandono*Tiempo de espera estimado)", "unidades": "1/Hora", "nota": "Proporcion de la cola que se retira por hora"},
}

CONSTANTES = {
    "Tasa base de llegadas": {"x": 130, "y": 220, "valor": 8.4, "unidades": "pacientes/Hora", "nota": "Llegadas por hora con confianza media"},
    "Factor de demanda": {"x": 130, "y": 160, "valor": 1, "unidades": "Dmnl", "nota": "Multiplicador para probar escenarios de demanda"},
    "Duracion de jornada": {"x": 130, "y": 380, "valor": 9, "unidades": "Hora", "nota": "Horas en que se reciben pacientes"},
    "Profesionales": {"x": 650, "y": 180, "valor": 4, "unidades": "profesionales", "nota": "Profesionales de salud disponibles"},
    "Duracion de atencion": {"x": 860, "y": 420, "valor": 0.29, "unidades": "Hora", "nota": "Duracion media de una consulta"},
    "Efecto por atencion": {"x": 230, "y": 30, "valor": 0.002, "unidades": "Dmnl", "nota": "Confianza ganada por paciente atendido"},
    "Efecto por abandono": {"x": 560, "y": 30, "valor": 0.01, "unidades": "Dmnl", "nota": "Confianza perdida por abandono"},
    "Tolerancia de espera": {"x": 700, "y": 100, "valor": 0.5, "unidades": "Hora", "nota": "Espera aceptada por la comunidad"},
    "Efecto por espera larga": {"x": 640, "y": 200, "valor": 0.05, "unidades": "1/Hora", "nota": "Confianza perdida por esperas superiores a la tolerancia"},
    "Sensibilidad al abandono": {"x": 400, "y": 480, "valor": 0.1, "unidades": "1/Hora/Hora", "nota": "Que tan rapido abandonan los pacientes al esperar"},
}

CAUSAL = {
    "variables": {
        "Llegadas de pacientes": (160, 250),
        "Cola de espera": (400, 250),
        "Tiempo de espera": (640, 250),
        "Abandonos": (640, 400),
        "Inicio de atencion": (400, 400),
        "Pacientes atendidos": (160, 400),
        "Confianza comunitaria": (400, 100),
        "Profesionales disponibles": (400, 520),
    },
    "enlaces": [
        ("Llegadas de pacientes", "Cola de espera", "+"),
        ("Cola de espera", "Tiempo de espera", "+"),
        ("Tiempo de espera", "Abandonos", "+"),
        ("Abandonos", "Cola de espera", "-"),
        ("Cola de espera", "Inicio de atencion", "+"),
        ("Inicio de atencion", "Cola de espera", "-"),
        ("Inicio de atencion", "Pacientes atendidos", "+"),
        ("Pacientes atendidos", "Confianza comunitaria", "+"),
        ("Tiempo de espera", "Confianza comunitaria", "-"),
        ("Abandonos", "Confianza comunitaria", "-"),
        ("Confianza comunitaria", "Llegadas de pacientes", "+"),
        ("Profesionales disponibles", "Inicio de atencion", "+"),
        ("Profesionales disponibles", "Tiempo de espera", "-"),
    ],
    "bucles": [
        ("R1", "Confianza y demanda", ("Confianza comunitaria", "Llegadas de pacientes", "Cola de espera", "Inicio de atencion", "Pacientes atendidos")),
        ("B1", "Abandono por espera", ("Cola de espera", "Tiempo de espera", "Abandonos")),
        ("B2", "Atencion de la cola", ("Cola de espera", "Inicio de atencion")),
        ("B3", "Espera y confianza", ("Cola de espera", "Tiempo de espera", "Confianza comunitaria", "Llegadas de pacientes")),
    ],
}
