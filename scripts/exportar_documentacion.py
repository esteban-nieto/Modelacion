import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "documentacion")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

from app.database import Base
from app.main import app

DOCS = Path(__file__).resolve().parent.parent / "docs"


def esquema_sql():
    sentencias = []
    for tabla in Base.metadata.sorted_tables:
        sentencias.append(str(CreateTable(tabla).compile(dialect=postgresql.dialect())).strip() + ";")
        sentencias.extend(str(CreateIndex(i).compile(dialect=postgresql.dialect())).strip() + ";" for i in tabla.indexes)
    return "\n\n".join(sentencias) + "\n"


if __name__ == "__main__":
    DOCS.mkdir(exist_ok=True)
    (DOCS / "esquema.sql").write_text(esquema_sql(), encoding="utf-8")
    (DOCS / "openapi.json").write_text(json.dumps(app.openapi(), indent=2, ensure_ascii=False), encoding="utf-8")
    print("Documentacion exportada en docs/")
