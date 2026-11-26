const sesion = {
  token: sessionStorage.getItem("token"),
  rol: sessionStorage.getItem("rol"),
  nombre: sessionStorage.getItem("nombre"),
};

const catalogos = { sedes: [], servicios: [], profesionales: [], roles: [] };

const $ = (selector) => document.querySelector(selector);

function crear(etiqueta, atributos = {}, ...hijos) {
  const nodo = document.createElement(etiqueta);
  for (const [clave, valor] of Object.entries(atributos)) {
    if (valor === false || valor === null || valor === undefined) continue;
    if (clave === "texto") nodo.textContent = valor;
    else if (clave.startsWith("on")) nodo.addEventListener(clave.slice(2), valor);
    else nodo.setAttribute(clave, valor === true ? "" : valor);
  }
  nodo.append(...hijos.flat().filter((h) => h !== null && h !== undefined));
  return nodo;
}

function mensajeDeError(cuerpo) {
  if (!cuerpo || !cuerpo.detail) return "No se pudo completar la operación";
  if (typeof cuerpo.detail === "string") return cuerpo.detail;
  return cuerpo.detail
    .map((e) => {
      const campo = e.loc.slice(1).join(".");
      const mensaje = e.msg.replace("Value error, ", "");
      return campo ? `${campo}: ${mensaje}` : mensaje;
    })
    .join(" | ");
}

async function api(ruta, { metodo = "GET", cuerpo, crudo = false } = {}) {
  const cabeceras = { Authorization: `Bearer ${sesion.token}` };
  if (cuerpo) cabeceras["Content-Type"] = "application/json";
  const respuesta = await fetch(ruta, { method: metodo, headers: cabeceras, body: cuerpo ? JSON.stringify(cuerpo) : undefined });
  if (respuesta.status === 401 && ruta !== "/api/auth/login") {
    cerrarSesion();
    throw new Error("La sesión expiró, ingrese de nuevo");
  }
  if (!respuesta.ok) throw new Error(mensajeDeError(await respuesta.json().catch(() => null)));
  if (crudo) return respuesta;
  return respuesta.status === 204 ? null : respuesta.json();
}

function avisar(texto) {
  $("#mensaje").textContent = texto;
}

function nombreDe(lista, id) {
  const encontrado = lista.find((e) => e.id === id);
  return encontrado ? encontrado.nombre : id;
}

function formatoFecha(texto) {
  return texto ? texto.replace("T", " ").slice(0, 16) : "";
}

const puedeEscribir = () => ["administrador", "operador"].includes(sesion.rol);
const esAdmin = () => sesion.rol === "administrador";

const recursos = {
  citas: {
    titulo: "Citas",
    columnas: [
      { campo: "id", etiqueta: "ID", orden: true },
      { campo: "llegada", etiqueta: "Llegada", orden: true, ver: (f) => formatoFecha(f.llegada) },
      { campo: "paciente_id", etiqueta: "Paciente" },
      { campo: "servicio_id", etiqueta: "Servicio", ver: (f) => nombreDe(catalogos.servicios, f.servicio_id) },
      { campo: "profesional_id", etiqueta: "Profesional", ver: (f) => nombreDe(catalogos.profesionales, f.profesional_id) },
      { campo: "estado", etiqueta: "Estado", orden: true },
      { campo: "prioridad", etiqueta: "Prioridad", orden: true },
    ],
    campos: [
      { nombre: "documento_paciente", etiqueta: "Documento del paciente", tipo: "text", requerido: true, patron: "\\d{5,15}" },
      { nombre: "sede_id", etiqueta: "Sede", tipo: "select", fuente: "sedes", requerido: true },
      { nombre: "servicio_id", etiqueta: "Servicio", tipo: "select", fuente: "servicios", requerido: true },
      { nombre: "profesional_id", etiqueta: "Profesional", tipo: "select", fuente: "profesionales", requerido: true },
      { nombre: "llegada", etiqueta: "Llegada", tipo: "datetime-local", requerido: true },
      { nombre: "inicio_atencion", etiqueta: "Inicio de atención", tipo: "datetime-local" },
      { nombre: "fin_atencion", etiqueta: "Fin de atención", tipo: "datetime-local" },
      { nombre: "estado", etiqueta: "Estado", tipo: "select", opciones: ["programada", "atendida", "cancelada", "no_asistio"], requerido: true },
      { nombre: "prioridad", etiqueta: "Prioridad", tipo: "select", opciones: ["normal", "prioritaria"], requerido: true },
    ],
    valoresIniciales: { estado: "programada", prioridad: "normal" },
  },
  pacientes: {
    titulo: "Pacientes",
    columnas: [
      { campo: "id", etiqueta: "ID", orden: true },
      { campo: "documento", etiqueta: "Documento", orden: true },
      { campo: "nombre", etiqueta: "Nombre", orden: true },
      { campo: "telefono", etiqueta: "Teléfono" },
    ],
    campos: [
      { nombre: "documento", etiqueta: "Documento", tipo: "text", requerido: true, patron: "\\d{5,15}" },
      { nombre: "nombre", etiqueta: "Nombre completo", tipo: "text", requerido: true, min: 3, max: 100 },
      { nombre: "telefono", etiqueta: "Teléfono", tipo: "text", requerido: true, patron: "\\d{7,15}" },
      { nombre: "fecha_nacimiento", etiqueta: "Fecha de nacimiento", tipo: "date", requerido: true },
    ],
  },
  profesionales: {
    titulo: "Profesionales",
    columnas: [
      { campo: "id", etiqueta: "ID", orden: true },
      { campo: "nombre", etiqueta: "Nombre", orden: true },
      { campo: "sede_id", etiqueta: "Sede", ver: (f) => nombreDe(catalogos.sedes, f.sede_id) },
      { campo: "servicios", etiqueta: "Servicios", ver: (f) => f.servicios.map((s) => s.nombre).join(", ") },
    ],
    campos: [
      { nombre: "nombre", etiqueta: "Nombre", tipo: "text", requerido: true, min: 3, max: 100 },
      { nombre: "sede_id", etiqueta: "Sede", tipo: "select", fuente: "sedes", requerido: true },
      { nombre: "servicios_ids", etiqueta: "Servicios que presta", tipo: "multiple", fuente: "servicios" },
    ],
  },
  servicios: {
    titulo: "Servicios",
    columnas: [
      { campo: "id", etiqueta: "ID", orden: true },
      { campo: "nombre", etiqueta: "Nombre", orden: true },
      { campo: "duracion_media_min", etiqueta: "Duración media (min)", orden: true },
    ],
    campos: [
      { nombre: "nombre", etiqueta: "Nombre", tipo: "text", requerido: true, min: 3, max: 100 },
      { nombre: "duracion_media_min", etiqueta: "Duración media (min)", tipo: "number", requerido: true, min: 1, max: 240 },
    ],
  },
  sedes: {
    titulo: "Sedes",
    columnas: [
      { campo: "id", etiqueta: "ID", orden: true },
      { campo: "nombre", etiqueta: "Nombre", orden: true },
      { campo: "vereda", etiqueta: "Vereda", orden: true },
    ],
    campos: [
      { nombre: "nombre", etiqueta: "Nombre", tipo: "text", requerido: true, min: 3, max: 100 },
      { nombre: "vereda", etiqueta: "Vereda", tipo: "text", requerido: true, min: 3, max: 100 },
    ],
  },
  usuarios: {
    titulo: "Usuarios",
    soloAdmin: true,
    columnas: [
      { campo: "id", etiqueta: "ID", orden: true },
      { campo: "nombre", etiqueta: "Nombre", orden: true },
      { campo: "correo", etiqueta: "Correo", orden: true },
      { campo: "rol", etiqueta: "Rol", ver: (f) => f.rol.nombre },
    ],
    campos: [
      { nombre: "nombre", etiqueta: "Nombre", tipo: "text", requerido: true, min: 3, max: 100 },
      { nombre: "correo", etiqueta: "Correo", tipo: "email", requerido: true },
      { nombre: "clave", etiqueta: "Clave (dejar vacía para no cambiar)", tipo: "password", min: 8 },
      { nombre: "rol_id", etiqueta: "Rol", tipo: "select", fuente: "roles", requerido: true },
    ],
  },
  auditoria: {
    titulo: "Auditoría",
    soloAdmin: true,
    soloLectura: true,
    sinBusqueda: true,
    columnas: [
      { campo: "id", etiqueta: "ID" },
      { campo: "fecha", etiqueta: "Fecha", ver: (f) => formatoFecha(f.fecha) },
      { campo: "usuario_id", etiqueta: "Usuario" },
      { campo: "entidad", etiqueta: "Entidad" },
      { campo: "registro_id", etiqueta: "Registro" },
      { campo: "accion", etiqueta: "Acción" },
    ],
    ruta: "/api/auditoria",
  },
};

const vistas = {
  tablero: { titulo: "Tablero", dibujar: dibujarTablero },
  cola: { titulo: "Cola de atención", dibujar: dibujarCola },
  reportes: { titulo: "Reportes", dibujar: dibujarReportes },
};

function opcionesDe(campo) {
  if (campo.opciones) return campo.opciones.map((o) => ({ valor: o, texto: o }));
  return catalogos[campo.fuente].map((e) => ({ valor: e.id, texto: e.nombre }));
}

async function cargarCatalogos() {
  const [sedes, servicios, profesionales] = await Promise.all(
    ["sedes", "servicios", "profesionales"].map((r) => api(`/api/${r}?tamano=100`))
  );
  catalogos.sedes = sedes.items;
  catalogos.servicios = servicios.items;
  catalogos.profesionales = profesionales.items;
  if (esAdmin()) catalogos.roles = await api("/api/auth/roles");
}

function construirCampo(campo, valor) {
  const atributos = { name: campo.nombre, required: campo.requerido, id: `campo-${campo.nombre}` };
  if (campo.tipo === "multiple") {
    const marcados = new Set(valor || []);
    const casillas = opcionesDe(campo).map((o) =>
      crear("label", {}, crear("input", { type: "checkbox", name: campo.nombre, value: o.valor, checked: marcados.has(o.valor) }), o.texto)
    );
    return crear("fieldset", {}, crear("legend", { texto: campo.etiqueta }), crear("div", { class: "opciones" }, casillas));
  }
  let entrada;
  if (campo.tipo === "select") {
    entrada = crear("select", atributos, opcionesDe(campo).map((o) => crear("option", { value: o.valor, texto: o.texto })));
    if (valor !== undefined) entrada.value = valor;
  } else {
    entrada = crear("input", {
      ...atributos,
      type: campo.tipo,
      pattern: campo.patron,
      minlength: campo.tipo === "text" || campo.tipo === "password" ? campo.min : null,
      maxlength: campo.max && campo.tipo === "text" ? campo.max : null,
      min: campo.tipo === "number" ? campo.min : null,
      max: campo.tipo === "number" ? campo.max : null,
      autocomplete: campo.tipo === "password" ? "new-password" : "off",
    });
    entrada.value = valor ?? "";
  }
  return crear("label", {}, campo.etiqueta, entrada);
}

function valoresParaFormulario(config, registro) {
  if (!registro) return config.valoresIniciales || {};
  const valores = { ...registro };
  if (registro.servicios) valores.servicios_ids = registro.servicios.map((s) => s.id);
  if (registro.rol) valores.rol_id = registro.rol.id;
  for (const campo of config.campos) {
    if (campo.tipo === "datetime-local" && valores[campo.nombre]) valores[campo.nombre] = valores[campo.nombre].slice(0, 16);
    if (campo.tipo === "date" && valores[campo.nombre]) valores[campo.nombre] = valores[campo.nombre].slice(0, 10);
  }
  return valores;
}

async function leerFormulario(config, formulario) {
  const datos = {};
  for (const campo of config.campos) {
    if (campo.tipo === "multiple") {
      datos[campo.nombre] = [...formulario.querySelectorAll(`[name="${campo.nombre}"]:checked`)].map((c) => Number(c.value));
      continue;
    }
    const bruto = formulario.elements[campo.nombre].value.trim();
    if (campo.tipo === "number" || (campo.tipo === "select" && campo.fuente)) datos[campo.nombre] = Number(bruto);
    else if (campo.tipo === "datetime-local") datos[campo.nombre] = bruto ? `${bruto}:00` : null;
    else if (campo.tipo === "date") datos[campo.nombre] = `${bruto}T00:00:00`;
    else if (campo.tipo === "password") datos[campo.nombre] = bruto || null;
    else datos[campo.nombre] = bruto;
  }
  if (config.titulo === "Citas") await resolverPaciente(datos);
  return datos;
}

async function resolverPaciente(datos) {
  const resultado = await api(`/api/pacientes?busqueda=${encodeURIComponent(datos.documento_paciente)}&tamano=1`);
  const paciente = resultado.items.find((p) => p.documento === datos.documento_paciente);
  if (!paciente) throw new Error("No existe un paciente con ese documento");
  datos.paciente_id = paciente.id;
  delete datos.documento_paciente;
}

async function abrirFormulario(nombre, config, registro, alGuardar) {
  const dialogo = $("#dialogo");
  const valores = valoresParaFormulario(config, registro);
  if (registro && nombre === "citas") {
    const paciente = await api(`/api/pacientes/${registro.paciente_id}`);
    valores.documento_paciente = paciente.documento;
  }
  $("#titulo-dialogo").textContent = `${registro ? "Editar" : "Nueva"} ${config.titulo.toLowerCase()}`;
  $("#campos-dialogo").replaceChildren(...config.campos.map((c) => construirCampo(c, valores[c.nombre])));
  $("#error-dialogo").textContent = "";
  const formulario = $("#form-dialogo");
  formulario.onsubmit = async (evento) => {
    evento.preventDefault();
    try {
      const datos = await leerFormulario(config, formulario);
      const ruta = registro ? `/api/${nombre}/${registro.id}` : `/api/${nombre}`;
      await api(ruta, { metodo: registro ? "PUT" : "POST", cuerpo: datos });
      dialogo.close();
      if (nombre === "profesionales" || nombre === "sedes" || nombre === "servicios") await cargarCatalogos();
      avisar("Registro guardado");
      alGuardar();
    } catch (error) {
      $("#error-dialogo").textContent = error.message;
    }
  };
  dialogo.showModal();
}

function dibujarLista(nombre) {
  const config = recursos[nombre];
  const ruta = config.ruta || `/api/${nombre}`;
  const consulta = { pagina: 1, tamano: 10, busqueda: "", orden: "id", direccion: "asc" };
  const contenedor = crear("div");

  async function cargar() {
    const parametros = new URLSearchParams({ pagina: consulta.pagina, tamano: consulta.tamano });
    if (!config.soloLectura) {
      parametros.set("orden", consulta.orden);
      parametros.set("direccion", consulta.direccion);
    }
    if (consulta.busqueda) parametros.set("busqueda", consulta.busqueda);
    try {
      pintar(await api(`${ruta}?${parametros}`));
    } catch (error) {
      avisar(error.message);
    }
  }

  function pintar(pagina) {
    const encabezados = config.columnas.map((c) => {
      const marca = c.orden && consulta.orden === c.campo ?(consulta.direccion === "asc" ? " ▲" : " ▼") : "";
      return crear("th", {
        class: c.orden ? "ordenable" : null,
        texto: c.etiqueta + marca,
        onclick: c.orden
          ? () => {
              consulta.direccion = consulta.orden === c.campo && consulta.direccion === "asc" ? "desc" : "asc";
              consulta.orden = c.campo;
              cargar();
            }
          : null,
      });
    });
    if (!config.soloLectura) encabezados.push(crear("th", { texto: "Acciones" }));
    const filas = pagina.items.map((registro) => {
      const celdas = config.columnas.map((c) => crear("td", { texto: String(c.ver ? c.ver(registro) : registro[c.campo] ?? "") }));
      if (!config.soloLectura) celdas.push(crear("td", {}, acciones(registro)));
      return crear("tr", {}, celdas);
    });
    contenedor.querySelector(".resultado").replaceChildren(
      crear("div", { class: "tabla-contenedor" }, crear("table", {}, crear("thead", {}, crear("tr", {}, encabezados)), crear("tbody", {}, filas))),
      crear(
        "div",
        { class: "paginacion" },
        crear("button", { class: "secundario", texto: "Anterior", disabled: pagina.pagina <= 1, onclick: () => { consulta.pagina -= 1; cargar(); } }),
        crear("span", { texto: `Página ${pagina.pagina} de ${Math.max(pagina.paginas, 1)} (${pagina.total} registros)` }),
        crear("button", { class: "secundario", texto: "Siguiente", disabled: pagina.pagina >= pagina.paginas, onclick: () => { consulta.pagina += 1; cargar(); } })
      )
    );
  }

  function acciones(registro) {
    const botones = [];
    if (puedeEscribir()) botones.push(crear("button", { class: "secundario", texto: "Editar", onclick: () => abrirFormulario(nombre, config, registro, cargar) }));
    if (esAdmin()) botones.push(crear("button", { class: "peligro", texto: "Eliminar", onclick: () => eliminar(registro) }));
    return crear("div", { class: "celda-acciones" }, botones);
  }

  async function eliminar(registro) {
    if (!window.confirm("¿Eliminar este registro? Quedará marcado como eliminado.")) return;
    try {
      await api(`/api/${nombre}/${registro.id}`, { metodo: "DELETE" });
      avisar("Registro eliminado");
      cargar();
    } catch (error) {
      avisar(error.message);
    }
  }

  const herramientas = crear("div", { class: "herramientas" });
  if (!config.sinBusqueda) {
    herramientas.append(
      crear("input", {
        type: "search",
        placeholder: "Buscar",
        "aria-label": "Buscar",
        oninput: (e) => {
          consulta.busqueda = e.target.value;
          consulta.pagina = 1;
          cargar();
        },
      })
    );
  }
  if (puedeEscribir() && !config.soloLectura && !(config.soloAdmin && !esAdmin())) {
    herramientas.append(crear("button", { texto: "Nuevo", onclick: () => abrirFormulario(nombre, config, null, cargar) }));
  }
  contenedor.append(crear("h2", { texto: config.titulo }), herramientas, crear("div", { class: "resultado" }));
  cargar();
  return contenedor;
}

function dibujarTablero() {
  const contenedor = crear("div", {}, crear("h2", { texto: "Tablero: indicadores reales y simulados" }));
  api("/api/tablero")
    .then((datos) => {
      const { reales, proyectados, alertas } = datos;
      const intervalo = (m) => (m ? `${m.media} (IC 95%: ${m.ic_inf} a ${m.ic_sup})` : "Sin simulación");
      const filas = [
        ["Espera media (min)", reales.espera_media_min, proyectados && intervalo(proyectados.base.espera_media_min), proyectados && intervalo(proyectados.recomendado.espera_media_min)],
        ["Ocupación media (%)", reales.ocupacion_media_pct, proyectados && intervalo(proyectados.base.ocupacion_pct), proyectados && intervalo(proyectados.recomendado.ocupacion_pct)],
      ];
      contenedor.append(
        crear("div", { class: "rejilla" }, [
          tarjetaIndicador("Citas atendidas", reales.citas_atendidas),
          tarjetaIndicador("Espera media real (min)", reales.espera_media_min),
          tarjetaIndicador("Atención media real (min)", reales.atencion_media_min),
          tarjetaIndicador("Ocupación media real (%)", reales.ocupacion_media_pct),
        ]),
        crear("h3", { texto: "Real frente a simulación" }),
        tablaSimple(
          ["Indicador", "Real", "Simulación base", proyectados ? `Recomendado: ${proyectados.recomendado.nombre}` : "Recomendado"],
          filas.map((f) => f.map((v) => v ?? "Sin simulación"))
        ),
        crear("h3", { texto: "Alertas de capacidad" }),
        alertas.length
          ? alertas.map((a) => crear("div", { class: "alerta", texto: `${a.servicio}: espera media de ${a.espera_media_min} min supera el umbral de ${a.umbral_min} min` }))
          : crear("p", { texto: "Sin alertas: las esperas están dentro del umbral." })
      );
    })
    .catch((error) => avisar(error.message));
  return contenedor;
}

function tarjetaIndicador(etiqueta, valor) {
  return crear("div", { class: "panel" }, crear("div", { class: "indicador", texto: String(valor) }), crear("div", { class: "etiqueta", texto: etiqueta }));
}

function tablaSimple(encabezados, filas) {
  return crear(
    "div",
    { class: "tabla-contenedor" },
    crear(
      "table",
      {},
      crear("thead", {}, crear("tr", {}, encabezados.map((e) => crear("th", { texto: e })))),
      crear("tbody", {}, filas.map((f) => crear("tr", {}, f.map((v) => crear("td", { texto: String(v) })))))
    )
  );
}

function dibujarCola() {
  const selector = crear("select", { "aria-label": "Sede" }, catalogos.sedes.map((s) => crear("option", { value: s.id, texto: s.nombre })));
  const resultado = crear("div");
  async function cargar() {
    try {
      const citas = await api(`/api/citas/cola?sede_id=${selector.value}`);
      resultado.replaceChildren(
        citas.length
          ? tablaSimple(
              ["Turno", "Prioridad", "Llegada", "Servicio", "Profesional"],
              citas.map((c, i) => [i + 1, c.prioridad, formatoFecha(c.llegada), nombreDe(catalogos.servicios, c.servicio_id), nombreDe(catalogos.profesionales, c.profesional_id)])
            )
          : crear("p", { texto: "No hay citas programadas en espera." })
      );
    } catch (error) {
      avisar(error.message);
    }
  }
  selector.addEventListener("change", cargar);
  cargar();
  return crear("div", {}, crear("h2", { texto: "Cola de atención (prioritarias primero)" }), crear("div", { class: "herramientas" }, selector), resultado);
}

function dibujarReportes() {
  const tipo = crear("select", { "aria-label": "Reporte" }, [
    crear("option", { value: "tiempos", texto: "Tiempos de espera y atención por servicio" }),
    crear("option", { value: "ocupacion", texto: "Ocupación por profesional" }),
    crear("option", { value: "volumen", texto: "Volumen de citas por periodo" }),
  ]);
  const desde = crear("input", { type: "date", "aria-label": "Desde" });
  const hasta = crear("input", { type: "date", "aria-label": "Hasta" });
  const periodo = crear("select", { "aria-label": "Periodo" }, [crear("option", { value: "dia", texto: "Por día" }), crear("option", { value: "mes", texto: "Por mes" })]);
  const resultado = crear("div");

  const parametros = (formato) => {
    const p = new URLSearchParams({ formato, periodo: periodo.value });
    if (desde.value) p.set("desde", desde.value);
    if (hasta.value) p.set("hasta", `${hasta.value}T23:59:59`);
    return p;
  };

  async function consultar() {
    try {
      const filas = await api(`/api/reportes/${tipo.value}?${parametros("json")}`);
      resultado.replaceChildren(filas.length ? tablaSimple(Object.keys(filas[0]), filas.map((f) => Object.values(f))) : crear("p", { texto: "Sin datos para el filtro." }));
    } catch (error) {
      avisar(error.message);
    }
  }

  return crear(
    "div",
    {},
    crear("h2", { texto: "Reportes" }),
    crear(
      "div",
      { class: "herramientas" },
      tipo, desde, hasta, periodo,
      crear("button", { texto: "Consultar", onclick: consultar }),
      crear("button", { class: "secundario", texto: "Descargar CSV", onclick: () => descargar(`/api/reportes/${tipo.value}?${parametros("csv")}`, `${tipo.value}.csv`) }),
      puedeEscribir() ? crear("button", { class: "secundario", texto: "Exportar datos para simulación", onclick: () => descargar("/api/exportar/citas.csv", "citas_historicas.csv") }) : null
    ),
    resultado
  );
}

async function descargar(ruta, nombreArchivo) {
  try {
    const respuesta = await api(ruta, { crudo: true });
    const url = URL.createObjectURL(await respuesta.blob());
    crear("a", { href: url, download: nombreArchivo }).click();
    URL.revokeObjectURL(url);
  } catch (error) {
    avisar(error.message);
  }
}

function disponibles() {
  const lista = Object.entries(vistas).map(([clave, v]) => ({ clave, titulo: v.titulo }));
  for (const [clave, r] of Object.entries(recursos)) {
    if (!r.soloAdmin || esAdmin()) lista.push({ clave, titulo: r.titulo });
  }
  return lista;
}

function mostrar(clave) {
  avisar("");
  for (const boton of document.querySelectorAll("#menu button")) boton.classList.toggle("activo", boton.dataset.vista === clave);
  const contenido = vistas[clave] ? vistas[clave].dibujar() : dibujarLista(clave);
  $("#contenido").replaceChildren(contenido);
}

async function entrar() {
  $("#vista-login").hidden = true;
  $("#vista-app").hidden = false;
  $("#usuario").textContent = `${sesion.nombre} (${sesion.rol})`;
  await cargarCatalogos();
  $("#menu").replaceChildren(...disponibles().map((v) => crear("button", { type: "button", "data-vista": v.clave, texto: v.titulo, onclick: () => mostrar(v.clave) })));
  mostrar("tablero");
}

function cerrarSesion() {
  sessionStorage.clear();
  sesion.token = null;
  $("#vista-app").hidden = true;
  $("#vista-login").hidden = false;
}

$("#form-login").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const formulario = evento.target;
  $("#error-login").textContent = "";
  if (!formulario.checkValidity()) {
    $("#error-login").textContent = "Ingrese un correo válido y su clave";
    return;
  }
  try {
    const cuerpo = { correo: formulario.correo.value, clave: formulario.clave.value };
    const datos = await api("/api/auth/login", { metodo: "POST", cuerpo });
    Object.assign(sesion, { token: datos.token, rol: datos.rol, nombre: datos.nombre });
    sessionStorage.setItem("token", datos.token);
    sessionStorage.setItem("rol", datos.rol);
    sessionStorage.setItem("nombre", datos.nombre);
    formulario.reset();
    await entrar();
  } catch (error) {
    $("#error-login").textContent = error.message;
  }
});

$("#salir").addEventListener("click", cerrarSesion);
$("#cancelar-dialogo").addEventListener("click", () => $("#dialogo").close());

if (sesion.token) entrar().catch(cerrarSesion);
