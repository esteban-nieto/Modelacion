import json
from dataclasses import dataclass, replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize

SALIDA = Path(__file__).resolve().parent / "salidas"
ITERACIONES = 10_000
SEMILLA = 77
HORIZONTE_ANIOS = 5


@dataclass(frozen=True)
class Supuestos:
    jornadas_por_anio: int = 250
    citas_por_dia: float = 76.0
    minutos_ahorrados_por_cita: float = 6.0
    valor_minuto_paciente: float = 95.0
    inversion_inicial: float = 14_000_000.0
    costo_operacion_anual: float = 3_000_000.0
    tasa_descuento: float = 0.12


def flujo_de_caja(supuestos):
    beneficio = (
        supuestos.minutos_ahorrados_por_cita * supuestos.citas_por_dia * supuestos.jornadas_por_anio * supuestos.valor_minuto_paciente
    )
    neto = beneficio - supuestos.costo_operacion_anual
    return [-supuestos.inversion_inicial] + [neto] * HORIZONTE_ANIOS, beneficio


def valor_presente_neto(flujo, tasa):
    return float(sum(valor / (1 + tasa) ** periodo for periodo, valor in enumerate(flujo)))


def tasa_interna_retorno(flujo):
    if flujo[1] <= 0:
        return None
    return float(optimize.brentq(lambda t: valor_presente_neto(flujo, t), -0.99, 10))


def periodo_de_recuperacion(flujo):
    acumulado = 0.0
    for periodo, valor in enumerate(flujo):
        siguiente = acumulado + valor
        if periodo > 0 and siguiente >= 0:
            return periodo - 1 + (-acumulado / valor)
        acumulado = siguiente
    return None


def indicadores(supuestos):
    flujo, beneficio = flujo_de_caja(supuestos)
    vpn = valor_presente_neto(flujo, supuestos.tasa_descuento)
    costos_presentes = supuestos.inversion_inicial + sum(
        supuestos.costo_operacion_anual / (1 + supuestos.tasa_descuento) ** t for t in range(1, HORIZONTE_ANIOS + 1)
    )
    beneficios_presentes = sum(beneficio / (1 + supuestos.tasa_descuento) ** t for t in range(1, HORIZONTE_ANIOS + 1))
    tir = tasa_interna_retorno(flujo)
    recuperacion = periodo_de_recuperacion(flujo)
    return {
        "flujo_de_caja": [round(v) for v in flujo],
        "beneficio_anual": round(beneficio),
        "vpn": round(vpn),
        "tir": round(tir, 4) if tir is not None else None,
        "relacion_beneficio_costo": round(beneficios_presentes / costos_presentes, 3),
        "recuperacion_anios": round(recuperacion, 2) if recuperacion is not None else None,
        "sostenibilidad_cobertura_operacion": round(beneficio / supuestos.costo_operacion_anual, 2),
    }


def sensibilidad(base, variables):
    filas = []
    for nombre, (bajo, alto) in variables.items():
        vpn_bajo = valor_presente_neto(flujo_de_caja(replace(base, **{nombre: bajo}))[0], base.tasa_descuento if nombre != "tasa_descuento" else bajo)
        vpn_alto = valor_presente_neto(flujo_de_caja(replace(base, **{nombre: alto}))[0], base.tasa_descuento if nombre != "tasa_descuento" else alto)
        filas.append({"variable": nombre, "valor_bajo": bajo, "valor_alto": alto, "vpn_bajo": round(vpn_bajo), "vpn_alto": round(vpn_alto)})
    return sorted(filas, key=lambda f: abs(f["vpn_alto"] - f["vpn_bajo"]), reverse=True)


def monte_carlo_vpn(base, rangos, iteraciones=ITERACIONES):
    rng = np.random.default_rng(SEMILLA)
    resultados = np.empty(iteraciones)
    for i in range(iteraciones):
        sorteo = {nombre: rng.triangular(bajo, modal, alto) for nombre, (bajo, modal, alto) in rangos.items()}
        supuestos = replace(base, **sorteo)
        resultados[i] = valor_presente_neto(flujo_de_caja(supuestos)[0], supuestos.tasa_descuento)
    return resultados


def graficar(vpn):
    figura, eje = plt.subplots(figsize=(9, 4.5))
    eje.hist(vpn / 1e6, bins=50, color="#0b6e4f")
    eje.axvline(0, color="black", linestyle="--")
    eje.set_xlabel("VPN a 5 años (millones de COP)")
    eje.set_ylabel("Frecuencia")
    eje.set_title("Distribución del VPN de la fila única con prioridad")
    figura.tight_layout()
    figura.savefig(SALIDA / "financiero_vpn.png", dpi=150)
    plt.close(figura)


def ejecutar():
    resultados = json.loads((SALIDA / "resultados.json").read_text(encoding="utf-8"))
    base_sim = resultados["escenarios"]["base"]["metricas"]
    recomendado = resultados["escenarios"][resultados["recomendado"]]
    ahorro = recomendado["diferencia_vs_base"]["espera_media_min"]
    ahorro_medio, ahorro_bajo, ahorro_alto = -ahorro["media"], -ahorro["ic_sup"], -ahorro["ic_inf"]
    base = Supuestos(citas_por_dia=round(base_sim["citas_por_dia"]["media"], 1), minutos_ahorrados_por_cita=ahorro_medio)

    medico = resultados["escenarios"]["medico_adicional"]
    ahorro_medico = -medico["diferencia_vs_base"]["espera_media_min"]["media"]
    alternativa = replace(base, minutos_ahorrados_por_cita=ahorro_medico, inversion_inicial=2_000_000.0, costo_operacion_anual=118_000_000.0)

    limites = {
        "minutos_ahorrados_por_cita": (ahorro_bajo, ahorro_alto),
        "valor_minuto_paciente": (65.0, 130.0),
        "citas_por_dia": (base.citas_por_dia * 0.8, base.citas_por_dia * 1.2),
        "tasa_descuento": (0.08, 0.16),
        "costo_operacion_anual": (2_000_000.0, 5_000_000.0),
    }
    rangos = {n: (b, getattr(base, n), a) for n, (b, a) in limites.items() if n != "tasa_descuento"}
    simulados = monte_carlo_vpn(base, rangos)
    salida = {
        "supuestos": base.__dict__,
        "fila_unica_con_prioridad": indicadores(base),
        "medico_adicional": {"supuestos": alternativa.__dict__, **indicadores(alternativa)},
        "sensibilidad_vpn": sensibilidad(base, limites),
        "monte_carlo_vpn": {
            "iteraciones": ITERACIONES,
            "media": round(float(simulados.mean())),
            "p5": round(float(np.percentile(simulados, 5))),
            "p50": round(float(np.percentile(simulados, 50))),
            "p95": round(float(np.percentile(simulados, 95))),
            "probabilidad_vpn_positivo": round(float((simulados > 0).mean()), 4),
        },
    }
    (SALIDA / "financiero.json").write_text(json.dumps(salida, indent=2, ensure_ascii=False), encoding="utf-8")
    graficar(simulados)
    print(json.dumps(salida, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    ejecutar()
