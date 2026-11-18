import numpy as np
import pandas as pd
import pytest

from simulacion import ajuste_distribuciones as ajuste
from simulacion import financiero, monte_carlo
from simulacion.modelo import Configuracion, cargar_parametros, esperas_diarias, replica


@pytest.fixture(scope="module")
def parametros():
    return cargar_parametros()


def test_fila_unica_con_un_servidor():
    assert monte_carlo.esperas_fila_unica([0, 1, 2], [5, 5, 5], 1) == [0, 4, 8]


def test_fila_unica_con_dos_servidores():
    assert monte_carlo.esperas_fila_unica([0, 1, 2], [5, 5, 5], 2) == [0, 0, 3]


def test_fila_por_profesional():
    esperas = monte_carlo.esperas_fila_por_profesional([0, 1, 2], [5, 5, 5], [0, 0, 1], 2)
    assert esperas == [0, 4, 0]


def test_replica_entrega_indicadores_coherentes(parametros):
    resultado = replica(parametros, Configuracion(), semilla=1, jornadas=3)
    assert resultado["espera_media_min"] >= 0
    assert 0 < resultado["ocupacion_pct"] < 100
    assert resultado["citas_por_dia"] > 0


def test_mas_recursos_reducen_la_espera(parametros):
    base = replica(parametros, Configuracion(), semilla=5, jornadas=15)
    ampliado = replica(parametros, Configuracion(profesionales_extra={"Medicina general": 3}), semilla=5, jornadas=15)
    assert ampliado["espera_Medicina general"] < base["espera_Medicina general"]


def test_prioridad_favorece_a_prioritarios(parametros):
    sin = replica(parametros, Configuracion(cola_unica=True), semilla=8, jornadas=30)
    con = replica(parametros, Configuracion(cola_unica=True, prioridad=True), semilla=8, jornadas=30)
    assert con["espera_prioritarios_min"] < sin["espera_prioritarios_min"]


def test_mayor_demanda_aumenta_la_espera(parametros):
    normal = replica(parametros, Configuracion(), semilla=3, jornadas=15)
    alta = replica(parametros, Configuracion(factor_demanda=1.4), semilla=3, jornadas=15)
    assert alta["espera_media_min"] > normal["espera_media_min"]


def test_simpy_y_recursion_rapida_coinciden(parametros, monkeypatch):
    monkeypatch.setattr(monte_carlo, "PROBABILIDAD_AUSENCIA", 0.0)
    monkeypatch.setattr(monte_carlo, "SIGMA_DEMANDA", 1e-9)
    monkeypatch.setattr(monte_carlo, "FACTOR_SERVICIO", (0.999999, 1.0, 1.000001))
    detallado = np.mean(esperas_diarias(parametros, Configuracion(cola_unica=True), 300, semilla=1))
    rapido, _ = monte_carlo.simular(parametros, fila_unica=True, iteraciones=300, semilla=2)
    assert abs(detallado - rapido.mean()) < 3


def test_ajuste_reconoce_distribucion_exponencial():
    muestra = np.random.default_rng(0).exponential(10, 2000)
    elegida = ajuste.elegir(ajuste.evaluar(muestra))
    assert elegida["ks_p"] > 0.05 and elegida["chi2_p"] > 0.05


def test_tiempos_entre_llegadas():
    grupo = pd.DataFrame({"llegada": pd.to_datetime(["2024-03-04 07:10", "2024-03-04 07:30"])})
    assert list(ajuste.tiempos_entre_llegadas(grupo)) == [10.0, 20.0]


def test_vpn_tir_y_recuperacion():
    flujo = [-100, 60, 60]
    assert financiero.valor_presente_neto(flujo, 0.10) == pytest.approx(4.132, abs=0.001)
    assert financiero.tasa_interna_retorno(flujo) == pytest.approx(0.1307, abs=0.001)
    assert financiero.periodo_de_recuperacion(flujo) == pytest.approx(1.667, abs=0.001)


def test_indicadores_financieros_positivos():
    resultado = financiero.indicadores(financiero.Supuestos())
    assert resultado["vpn"] > 0 and resultado["relacion_beneficio_costo"] > 1


def test_resumen_de_percentiles():
    resumen = monte_carlo.resumir(np.arange(1, 101, dtype=float), np.zeros(100))
    assert resumen["p50"] == pytest.approx(50.5) and resumen["probabilidad_superar_umbral"] == 0.7


def test_intervalo_de_confianza():
    from simulacion.escenarios import intervalo

    resultado = intervalo([10, 12, 14, 16, 18])
    assert resultado["media"] == 14 and resultado["ic_inf"] < 14 < resultado["ic_sup"]
