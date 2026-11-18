from pathlib import Path

import pysd
import pytest

MODELO = Path(__file__).resolve().parent.parent / "diagramas" / "turnos_flujos_niveles.mdl"


@pytest.fixture(scope="module")
def modelo():
    return pysd.read_vensim(str(MODELO))


def test_conservacion_de_pacientes(modelo):
    trayectoria = modelo.run(return_columns=["Cola de espera", "En atencion", "Atendidos", "Abandonos acumulados", "Llegadas"])
    paso = 0.0625
    llegados = trayectoria["Llegadas"].sum() * paso
    total = trayectoria.iloc[-1][["Cola de espera", "En atencion", "Atendidos", "Abandonos acumulados"]].sum()
    assert total == pytest.approx(llegados, rel=0.02)


def test_mas_demanda_genera_mas_cola(modelo):
    base = modelo.run(params={"Factor de demanda": 1.0}, return_columns=["Cola de espera"])["Cola de espera"].max()
    alta = modelo.run(params={"Factor de demanda": 1.5}, return_columns=["Cola de espera"])["Cola de espera"].max()
    assert alta > base
