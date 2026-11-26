import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import Sesion
from app.negocio import reportes

DESTINO = Path(__file__).resolve().parent / "datos" / "citas_historicas.csv"


def exportar():
    with Sesion() as db:
        filas = reportes.citas_atendidas(db)
    DESTINO.write_text(reportes.a_csv(filas), encoding="utf-8")
    print(f"{len(filas)} citas atendidas exportadas a {DESTINO}")


if __name__ == "__main__":
    exportar()
