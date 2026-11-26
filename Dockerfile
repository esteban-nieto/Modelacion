FROM python:3.12-slim

WORKDIR /srv
ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY app ./app
COPY static ./static
COPY scripts ./scripts
COPY simulacion ./simulacion
COPY tests ./tests
COPY pytest.ini ./

EXPOSE 8000
CMD ["sh", "-c", "python scripts/sembrar_datos.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
