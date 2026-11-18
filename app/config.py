import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./turnos.db")
SECRET_KEY = os.environ.get("SECRET_KEY", "")
TOKEN_MINUTOS = int(os.environ.get("TOKEN_MINUTOS", "120"))
UMBRAL_ESPERA_MIN = float(os.environ.get("UMBRAL_ESPERA_MIN", "30"))
RESULTADOS_SIMULACION = os.environ.get("RESULTADOS_SIMULACION", "simulacion/salidas/resultados.json")
