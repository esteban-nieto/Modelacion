"""Genera docs/resultados/index.html: una página estática con los resultados del proyecto.

Lee los JSON que producen los scripts (no escribe cifras a mano), los embebe en la página y
los dibuja con JavaScript. Abre el archivo con doble clic; no necesita servidor.

Uso: python scripts/generar_resultados_html.py
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDAS = RAIZ / "simulacion" / "salidas"
DESTINO = RAIZ / "docs" / "resultados" / "index.html"

FUENTES = {
    "resultados": SALIDAS / "resultados.json",
    "monte_carlo": SALIDAS / "monte_carlo.json",
    "financiero": SALIDAS / "financiero.json",
    "calentamiento": SALIDAS / "calentamiento.json",
    "usabilidad": RAIZ / "docs" / "usabilidad_simulada.json",
}

PLANTILLA = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Resultados: gestión de turnos en un puesto de salud rural</title>
<style>
  :root { --verde: #0b6e4f; --gris: #5b6770; --fondo: #f6f8f7; --linea: #d8e0dc; }
  body { font-family: system-ui, sans-serif; margin: 0; background: var(--fondo); color: #1d2630; }
  header { background: var(--verde); color: white; padding: 24px 32px; }
  header h1 { margin: 0 0 6px; font-size: 24px; }
  header p { margin: 0; opacity: .9; }
  main { max-width: 1100px; margin: 0 auto; padding: 24px; }
  section { background: white; border: 1px solid var(--linea); border-radius: 8px; padding: 20px 24px; margin-bottom: 20px; }
  h2 { margin: 0 0 4px; font-size: 19px; color: var(--verde); }
  .nota { color: var(--gris); font-size: 14px; margin: 0 0 14px; }
  .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 8px; }
  .kpi { border: 1px solid var(--linea); border-radius: 6px; padding: 12px; }
  .kpi b { display: block; font-size: 22px; color: var(--verde); }
  .kpi span { font-size: 13px; color: var(--gris); }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  th, td { text-align: left; padding: 7px 8px; border-bottom: 1px solid var(--linea); vertical-align: top; }
  th { color: var(--gris); font-weight: 600; }
  .barra { display: flex; align-items: center; gap: 10px; margin: 6px 0; font-size: 14px; }
  .barra .nombre { width: 210px; }
  .barra .pista { flex: 1; background: #eef3f1; border-radius: 4px; height: 18px; position: relative; }
  .barra .relleno { background: var(--verde); height: 100%; border-radius: 4px; }
  .barra .valor { width: 150px; text-align: right; color: var(--gris); }
  .ok { color: var(--verde); font-weight: 600; }
  .mal { color: #a33b20; font-weight: 600; }
  img { max-width: 100%; border: 1px solid var(--linea); border-radius: 6px; margin-top: 8px; }
  .etiqueta { display: inline-block; background: #fff4d6; color: #7a5a00; border-radius: 4px; padding: 2px 8px; font-size: 13px; }
</style>
</head>
<body>
<header>
  <h1>Gestión de turnos en un puesto de salud rural</h1>
  <p>Resultados de la simulación, el análisis financiero y la revisión de usabilidad.</p>
</header>
<main>

<section>
  <h2>1. Indicadores principales</h2>
  <p class="nota">Cifras leídas de <code>simulacion/salidas/</code>. Cada escenario se corrió con 30 réplicas.</p>
  <div class="kpis" id="kpis"></div>
</section>

<section>
  <h2>2. Validación contra el CRUD</h2>
  <p class="nota">Compara la espera diaria real (datos del CRUD) con la simulada, 400 jornadas simuladas.</p>
  <div id="validacion"></div>
</section>

<section>
  <h2>3. Escenarios: espera media con intervalo del 95 %</h2>
  <p class="nota">Barras: espera media en minutos. Un escenario es mejor cuanto menor es la barra.</p>
  <div id="escenarios"></div>
  <img src="../../simulacion/salidas/espera_escenarios.png" alt="Espera media por escenario con IC del 95 %">
</section>

<section>
  <h2>4. Sensibilidad y cuellos de botella</h2>
  <div id="sensibilidad"></div>
  <div id="cuellos"></div>
</section>

<section>
  <h2>5. Calentamiento: espera por hora de llegada</h2>
  <p class="nota">La espera sube durante la jornada porque el puesto abre vacío. No se descarta ninguna hora; ver la justificación en el informe.</p>
  <div id="calentamiento"></div>
</section>

<section>
  <h2>6. Monte Carlo (10 000 iteraciones)</h2>
  <div id="montecarlo"></div>
  <img src="../../simulacion/salidas/monte_carlo_histograma.png" alt="Histograma Monte Carlo">
</section>

<section>
  <h2>7. Modelo financiero</h2>
  <div id="financiero"></div>
  <img src="../../simulacion/salidas/financiero_vpn.png" alt="Distribución del VPN">
</section>

<section>
  <h2>8. Revisión de usabilidad <span class="etiqueta">SIMULADA</span></h2>
  <p class="nota">Recorrido automatizado por perfiles de rol contra la API real. No reemplaza pruebas con personas reales.</p>
  <div id="usabilidad"></div>
</section>

</main>
<script>
const DATOS = __DATOS__;

function el(tag, texto, clase) {
  const nodo = document.createElement(tag);
  if (texto !== undefined && texto !== null) nodo.textContent = texto;
  if (clase) nodo.className = clase;
  return nodo;
}

function kpi(valor, etiqueta) {
  const nodo = el("div", undefined, "kpi");
  nodo.appendChild(el("b", valor));
  nodo.appendChild(el("span", etiqueta));
  return nodo;
}

function tabla(cabeceras, filas) {
  const t = el("table");
  const thead = el("tr");
  cabeceras.forEach((c) => thead.appendChild(el("th", c)));
  t.appendChild(thead);
  filas.forEach((fila) => {
    const tr = el("tr");
    fila.forEach((c) => {
      const td = el("td");
      if (c && typeof c === "object" && "texto" in c) {
        td.textContent = c.texto;
        td.className = c.clase;
      } else {
        td.textContent = c;
      }
      tr.appendChild(td);
    });
    t.appendChild(tr);
  });
  return t;
}

function barras(items, maximo, formato) {
  const contenedor = el("div");
  items.forEach((it) => {
    const fila = el("div", undefined, "barra");
    fila.appendChild(el("div", it.nombre, "nombre"));
    const pista = el("div", undefined, "pista");
    const relleno = el("div", undefined, "relleno");
    relleno.style.width = Math.max(0, Math.min(100, (100 * it.valor) / maximo)) + "%";
    pista.appendChild(relleno);
    fila.appendChild(pista);
    fila.appendChild(el("div", formato(it), "valor"));
    contenedor.appendChild(fila);
  });
  return contenedor;
}

const r = DATOS.resultados;
const base = r.escenarios.base.metricas;
const recomendado = r.escenarios[r.recomendado];
const reduccion = 100 * (1 - recomendado.metricas.espera_media_min.media / base.espera_media_min.media);

const kpis = document.getElementById("kpis");
kpis.appendChild(kpi(base.espera_media_min.media.toFixed(1) + " min", "Espera media, sistema actual"));
kpis.appendChild(kpi(recomendado.metricas.espera_media_min.media.toFixed(1) + " min", "Espera media, escenario recomendado"));
kpis.appendChild(kpi(reduccion.toFixed(0) + " %", "Reducción frente al actual"));
kpis.appendChild(kpi(r.recomendado, "Escenario recomendado"));

const v = r.validacion;
document.getElementById("validacion").appendChild(tabla(
  ["Medida", "Valor"],
  [
    ["Días reales del CRUD", v.dias_reales],
    ["Espera diaria real (media)", v.espera_diaria_real_media.toFixed(2) + " min"],
    ["Espera diaria simulada (media)", v.espera_diaria_simulada_media.toFixed(2) + " min"],
    ["Prueba t de Welch (p)", v.welch_t_p.toFixed(4)],
    ["Kolmogorov-Smirnov dos muestras (p)", v.ks_dos_muestras_p.toFixed(4)],
    ["Mann-Whitney (p)", v.mann_whitney_p.toFixed(4)],
    [{ texto: "Conclusión", clase: "ok" }, v.conclusion],
  ]
));

document.getElementById("escenarios").appendChild(barras(
  Object.entries(r.escenarios).map(([nombre, e]) => ({
    nombre: nombre + (nombre === r.recomendado ? " (recomendado)" : ""),
    valor: e.metricas.espera_media_min.media,
    ic: [e.metricas.espera_media_min.ic_inf, e.metricas.espera_media_min.ic_sup],
  })),
  Math.max(...Object.values(r.escenarios).map((e) => e.metricas.espera_media_min.media)) * 1.1,
  (it) => it.valor.toFixed(1) + " min [" + it.ic[0].toFixed(1) + " – " + it.ic[1].toFixed(1) + "]"
));

const sens = r.sensibilidad.map((f) => [f.escenario, f.factor_demanda, f.factor_servicio, f.espera_media_min.toFixed(2), f.ocupacion_pct.toFixed(1) + " %"]);
document.getElementById("sensibilidad").appendChild(el("p", "Sensibilidad: el escenario recomendado frente a cambios de demanda y de tiempo de servicio.", "nota"));
document.getElementById("sensibilidad").appendChild(tabla(["Caso", "Factor demanda", "Factor servicio", "Espera media (min)", "Ocupación"], sens));
document.getElementById("cuellos").appendChild(el("p", "Ocupación por servicio en el sistema actual (cuello de botella = mayor ocupación):", "nota"));
document.getElementById("cuellos").appendChild(barras(
  Object.entries(r.cuellos_de_botella_ocupacion_pct).map(([nombre, valor]) => ({ nombre, valor })),
  100,
  (it) => it.valor.toFixed(1) + " %"
));

const cal = DATOS.calentamiento;
document.getElementById("calentamiento").appendChild(barras(
  Object.entries(cal.medias_por_hora_min).map(([hora, valor]) => ({ nombre: hora, valor })),
  Math.max(...Object.values(cal.medias_por_hora_min)) * 1.1,
  (it) => it.valor.toFixed(1) + " min"
));

const mc = DATOS.monte_carlo;
const filasMC = ["sistema_actual", "fila_unica"].filter((k) => mc[k]).map((k) => [
  k === "sistema_actual" ? "Sistema actual" : "Fila única",
  mc[k].p5, mc[k].p50, mc[k].p95, mc[k].p99,
]);
document.getElementById("montecarlo").appendChild(el("p", "Iteraciones: " + mc.iteraciones.toLocaleString("es-CO") + ". Percentiles de la espera media diaria (min).", "nota"));
document.getElementById("montecarlo").appendChild(tabla(["Escenario", "p5", "p50", "p95", "p99"], filasMC));

const fin = DATOS.financiero;
const filasSens = (fin.sensibilidad_vpn || []).map((f) => [f.variable, f.valor_bajo, f.valor_alto, f.vpn_bajo.toLocaleString("es-CO"), f.vpn_alto.toLocaleString("es-CO")]);
document.getElementById("financiero").appendChild(el("p", "VPN a 5 años de la fila única con prioridad (pesos colombianos). Sensibilidad frente a variables inciertas.", "nota"));
document.getElementById("financiero").appendChild(tabla(["Variable", "Valor bajo", "Valor alto", "VPN bajo", "VPN alto"], filasSens));

const filasUsab = [];
DATOS.usabilidad.usuarios.forEach((u) => {
  u.tareas.forEach((t) => {
    const clase = t.resultado === "completada" ? "ok" : (t.resultado === "bloqueado por rol" ? "" : "mal");
    filasUsab.push([u.perfil.id + " (" + u.perfil.rol + ")", t.tarea, { texto: t.resultado, clase }, t.codigo]);
  });
});
document.getElementById("usabilidad").appendChild(tabla(["Perfil", "Tarea", "Resultado", "Código HTTP"], filasUsab));
</script>
</body>
</html>
"""


def cargar():
    datos = {}
    for clave, ruta in FUENTES.items():
        datos[clave] = json.loads(ruta.read_text(encoding="utf-8"))
    return datos


def ejecutar():
    datos = cargar()
    # Escapar "</" para que los datos no cierren la etiqueta <script> prematuramente.
    embebido = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(PLANTILLA.replace("__DATOS__", embebido), encoding="utf-8")
    print("Escrito:", DESTINO)


if __name__ == "__main__":
    ejecutar()
