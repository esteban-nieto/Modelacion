from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch, Rectangle

SALIDA = Path(__file__).resolve().parent / "figuras"
VERDE, ROJO, GRIS, AZUL = "#0b6e4f", "#b42318", "#616e7c", "#1d4e89"


def lienzo(ancho, alto, titulo):
    figura, eje = plt.subplots(figsize=(ancho, alto))
    eje.axis("off")
    eje.set_title(titulo, fontsize=13, fontweight="bold")
    return figura, eje


def guardar(figura, nombre):
    figura.tight_layout()
    figura.savefig(SALIDA / nombre, dpi=150)
    plt.close(figura)


def flecha(eje, origen, destino, color=GRIS, estilo="-|>", curva=0.0, ancho=1.3, discontinua=False):
    eje.add_patch(
        FancyArrowPatch(origen, destino, arrowstyle=estilo, mutation_scale=12, color=color, lw=ancho, connectionstyle=f"arc3,rad={curva}", linestyle="--" if discontinua else "-")
    )


TABLAS = {
    "roles": {"pos": (60, 60), "campos": ["id PK", "nombre"]},
    "usuarios": {"pos": (60, 230), "campos": ["id PK", "nombre", "correo", "clave_hash", "rol_id FK", "eliminado"]},
    "auditoria": {"pos": (60, 470), "campos": ["id PK", "usuario_id FK", "entidad", "registro_id", "accion", "detalle", "fecha"]},
    "sedes": {"pos": (420, 60), "campos": ["id PK", "nombre", "vereda", "eliminado"]},
    "profesionales": {"pos": (420, 230), "campos": ["id PK", "nombre", "sede_id FK", "eliminado"]},
    "profesional_servicio": {"pos": (420, 410), "campos": ["profesional_id PK FK", "servicio_id PK FK"]},
    "servicios": {"pos": (780, 560), "campos": ["id PK", "nombre", "duracion_media_min", "eliminado"]},
    "pacientes": {"pos": (780, 60), "campos": ["id PK", "documento", "nombre", "telefono", "fecha_nacimiento", "eliminado"]},
    "citas": {"pos": (780, 230), "campos": ["id PK", "paciente_id FK", "profesional_id FK", "servicio_id FK", "sede_id FK", "llegada", "inicio_atencion", "fin_atencion", "estado", "prioridad", "eliminado"]},
}
RELACIONES = [
    ("roles", "usuarios"), ("usuarios", "auditoria"), ("sedes", "profesionales"), ("profesionales", "profesional_servicio"),
    ("servicios", "profesional_servicio"), ("pacientes", "citas"), ("profesionales", "citas"), ("servicios", "citas"), ("sedes", "citas"),
]
ANCHO_TABLA, ALTO_FILA, ALTO_TITULO = 220, 22, 28


def dimensiones(nombre):
    t = TABLAS[nombre]
    return t["pos"][0], t["pos"][1], ANCHO_TABLA, ALTO_TITULO + ALTO_FILA * len(t["campos"])


def centro(nombre):
    x, y, ancho, alto = dimensiones(nombre)
    return x + ancho / 2, y + alto / 2


def borde(nombre, hacia):
    x, y, ancho, alto = dimensiones(nombre)
    cx, cy = centro(nombre)
    dx, dy = hacia[0] - cx, hacia[1] - cy
    escala = min((ancho / 2) / abs(dx) if dx else 1e9, (alto / 2) / abs(dy) if dy else 1e9)
    return cx + dx * escala, cy + dy * escala


def figura_erd():
    figura, eje = lienzo(14, 9, "Modelo entidad-relación (3FN)")
    for a, b in RELACIONES:
        flecha(eje, borde(a, centro(b)), borde(b, centro(a)), estilo="-", color=GRIS)
        p, q = borde(a, centro(b)), borde(b, centro(a))
        eje.text(p[0] + (q[0] - p[0]) * 0.12, p[1] + (q[1] - p[1]) * 0.12, "1", fontsize=9, color=AZUL, ha="center")
        eje.text(p[0] + (q[0] - p[0]) * 0.88, p[1] + (q[1] - p[1]) * 0.88, "N", fontsize=9, color=ROJO, ha="center")
    for nombre, t in TABLAS.items():
        x, y, ancho, alto = dimensiones(nombre)
        eje.add_patch(Rectangle((x, y), ancho, alto, fc="white", ec=VERDE, lw=1.5))
        eje.add_patch(Rectangle((x, y), ancho, ALTO_TITULO, fc=VERDE, ec=VERDE))
        eje.text(x + ancho / 2, y + ALTO_TITULO / 2, nombre, color="white", ha="center", va="center", fontweight="bold", fontsize=10)
        for i, campo in enumerate(t["campos"]):
            eje.text(x + 8, y + ALTO_TITULO + ALTO_FILA * (i + 0.5), campo, va="center", fontsize=8.5)
    eje.set_xlim(20, 1040)
    eje.set_ylim(700, 20)
    guardar(figura, "erd.png")


def caja(eje, x, y, ancho, alto, texto, color="#eef6f2", borde_color=VERDE, tam=9):
    eje.add_patch(FancyBboxPatch((x, y), ancho, alto, boxstyle="round,pad=3", fc=color, ec=borde_color, lw=1.5))
    eje.text(x + ancho / 2, y + alto / 2, texto, ha="center", va="center", fontsize=tam)


def figura_arquitectura():
    figura, eje = lienzo(13, 8, "Arquitectura por capas y despliegue")
    caja(eje, 40, 40, 200, 70, "Navegador\nHTML + CSS + JS", "#e8f0fb", AZUL)
    caja(eje, 300, 40, 180, 70, "Proxy Caddy\nHTTPS", "#fff7e6", "#b7791f")
    eje.add_patch(Rectangle((540, 20), 420, 390, fc="#f8faf9", ec=GRIS, ls="--"))
    eje.text(750, 40, "Contenedor API (FastAPI)", ha="center", fontweight="bold", fontsize=10)
    caja(eje, 580, 70, 340, 80, "Presentación: routers REST\nauth, catálogos, operación (OpenAPI)")
    caja(eje, 580, 180, 340, 80, "Lógica de negocio\nreportes, cola de turnos, tablero, alertas")
    caja(eje, 580, 290, 340, 80, "Acceso a datos\nSQLAlchemy, consultas, auditoría")
    caja(eje, 580, 450, 340, 70, "PostgreSQL\n(SQLite en pruebas)", "#e8f0fb", AZUL)
    caja(eje, 40, 330, 400, 90, "Simulación (SimPy)\najuste de distribuciones, escenarios,\nMonte Carlo y modelo financiero", "#fdecea", ROJO)
    caja(eje, 40, 450, 400, 70, "citas_historicas.csv  →  resultados.json", "#fdecea", ROJO)
    flecha(eje, (240, 75), (300, 75))
    flecha(eje, (480, 75), (580, 110))
    for y in (150, 260):
        flecha(eje, (750, y), (750, y + 30))
    flecha(eje, (750, 370), (750, 450))
    flecha(eje, (580, 480), (440, 480), color=ROJO)
    flecha(eje, (240, 450), (240, 420), color=ROJO)
    flecha(eje, (440, 485), (580, 225), color=ROJO, curva=-0.35, discontinua=True)
    eje.text(500, 360, "exporta CSV / lee resultados", fontsize=8, color=ROJO)
    eje.set_xlim(0, 1000)
    eje.set_ylim(560, 0)
    guardar(figura, "arquitectura.png")


def figura_casos_de_uso():
    figura, eje = lienzo(13, 8, "Casos de uso por rol")
    casos = [
        ("Gestionar usuarios y roles", 120, {"Administrador"}),
        ("Consultar auditoría", 220, {"Administrador"}),
        ("Eliminar registros (borrado lógico)", 320, {"Administrador"}),
        ("Gestionar pacientes y citas", 420, {"Administrador", "Operador"}),
        ("Gestionar sedes, servicios y profesionales", 520, {"Administrador", "Operador"}),
        ("Ver cola de atención", 620, {"Administrador", "Operador", "Consulta"}),
        ("Consultar reportes y exportar CSV", 720, {"Administrador", "Operador", "Consulta"}),
        ("Ver tablero real vs simulado", 820, {"Administrador", "Operador", "Consulta"}),
    ]
    posiciones = {"Administrador": (100, 300), "Operador": (100, 480), "Consulta": (100, 660)}
    for nombre, (x, y) in posiciones.items():
        eje.plot([x], [y - 35], "o", color=AZUL, ms=14)
        eje.plot([x, x], [y - 28, y + 10], color=AZUL, lw=2)
        eje.plot([x - 20, x + 20], [y - 15, y - 15], color=AZUL, lw=2)
        eje.plot([x, x - 15], [y + 10, y + 40], color=AZUL, lw=2)
        eje.plot([x, x + 15], [y + 10, y + 40], color=AZUL, lw=2)
        eje.text(x, y + 62, nombre, ha="center", fontsize=10, fontweight="bold")
    eje.add_patch(Rectangle((300, 40), 620, 740, fc="none", ec=GRIS))
    for i, (texto, _, roles) in enumerate(casos):
        y = 90 + i * 88
        eje.add_patch(Ellipse((610, y), 400, 60, fc="#eef6f2", ec=VERDE))
        eje.text(610, y, texto, ha="center", va="center", fontsize=9)
        for rol in roles:
            flecha(eje, (posiciones[rol][0] + 30, posiciones[rol][1]), (410, y), estilo="-", color="#9aa5b1", ancho=0.9)
    eje.set_xlim(0, 960)
    eje.set_ylim(800, 0)
    guardar(figura, "casos_de_uso.png")


def secuencia(titulo, nombre_archivo, participantes, mensajes):
    figura, eje = lienzo(12, 7.5, titulo)
    xs = {p: 90 + i * (820 / (len(participantes) - 1)) for i, p in enumerate(participantes)}
    for p, x in xs.items():
        caja(eje, x - 60, 20, 120, 36, p, "#e8f0fb", AZUL, 9)
        eje.plot([x, x], [60, 60 + 60 * len(mensajes) + 20], color=GRIS, ls="--", lw=1)
    for i, (origen, destino, texto, retorno) in enumerate(mensajes):
        y = 100 + i * 55
        a, b = xs[origen], xs[destino]
        flecha(eje, (a, y), (b, y), color=ROJO if retorno else VERDE, discontinua=retorno)
        eje.text((a + b) / 2, y - 8, texto, ha="center", fontsize=8.5)
    eje.set_xlim(0, 1000)
    eje.set_ylim(60 * len(mensajes) + 120, 0)
    guardar(figura, nombre_archivo)


def figura_secuencias():
    secuencia(
        "Secuencia: inicio de sesión y consulta autorizada",
        "secuencia_login.png",
        ["Navegador", "API REST", "Seguridad", "Base de datos"],
        [
            ("Navegador", "API REST", "POST /api/auth/login (correo, clave)", False),
            ("API REST", "Base de datos", "Busca usuario activo", False),
            ("API REST", "Seguridad", "Verifica hash scrypt con sal", False),
            ("Seguridad", "API REST", "Genera token JWT con rol", True),
            ("API REST", "Navegador", "Token, nombre y rol", True),
            ("Navegador", "API REST", "GET /api/citas con Bearer", False),
            ("API REST", "Seguridad", "Valida token y permisos del rol", False),
            ("API REST", "Base de datos", "Consulta paginada y filtrada", False),
            ("API REST", "Navegador", "Página de resultados", True),
        ],
    )
    secuencia(
        "Secuencia: registro de una cita",
        "secuencia_cita.png",
        ["Operador", "API REST", "Negocio", "Base de datos", "Auditoría"],
        [
            ("Operador", "API REST", "POST /api/citas (datos del formulario)", False),
            ("API REST", "API REST", "Valida esquema y tiempos", False),
            ("API REST", "Negocio", "Verifica sede, profesional y servicio", False),
            ("Negocio", "API REST", "Datos preparados o error 422", True),
            ("API REST", "Base de datos", "Verifica referencias e inserta", False),
            ("API REST", "Auditoría", "Registra usuario, acción y fecha", False),
            ("API REST", "Base de datos", "Confirma la transacción", False),
            ("API REST", "Operador", "201 Creado con la cita", True),
        ],
    )


def figura_gantt():
    figura, eje = plt.subplots(figsize=(13, 6.5))
    tareas = [
        ("Análisis del problema y árbol de problemas", 1, 2, AZUL),
        ("Bitácora, Gantt y requisitos", 3, 4, AZUL),
        ("Modelo de datos y arquitectura", 3, 4, AZUL),
        ("Diagramas de modelación (B1)", 3, 4, AZUL),
        ("Backend, autenticación y roles", 5, 7, VERDE),
        ("Casos y mapa comparativo (B2)", 5, 7, ROJO),
        ("Carga de datos, reportes y exportación", 8, 9, VERDE),
        ("Ajuste de distribuciones y modelo base", 8, 9, ROJO),
        ("Verificación y validación", 9, 9, ROJO),
        ("Escenarios, réplicas y Monte Carlo", 10, 11, ROJO),
        ("Modelo financiero", 10, 11, ROJO),
        ("Dashboard y cambios derivados de la simulación", 10, 11, VERDE),
        ("Informe final, ensayos y sustentación", 12, 12, AZUL),
    ]
    for i, (nombre, inicio, fin, color) in enumerate(tareas):
        eje.barh(i, fin - inicio + 1, left=inicio - 1, color=color, edgecolor="white")
    eje.set_yticks(range(len(tareas)))
    eje.set_yticklabels([t[0] for t in tareas], fontsize=9)
    eje.invert_yaxis()
    eje.set_xticks(range(12))
    eje.set_xticklabels([f"S{i}" for i in range(1, 13)])
    for semana, nombre in ((2, "PC1"), (4, "PC2"), (7, "PC3"), (9, "PC4"), (11, "PC5")):
        eje.axvline(semana, color="black", ls="--", lw=0.8)
        eje.text(semana, -0.7, nombre, ha="center", fontsize=9, fontweight="bold")
    eje.set_title("Cronograma de 12 semanas (azul: planeación, verde: sistema, rojo: simulación)", pad=24)
    guardar(figura, "gantt.png")


def generar():
    SALIDA.mkdir(exist_ok=True)
    figura_erd()
    figura_arquitectura()
    figura_casos_de_uso()
    figura_secuencias()
    figura_gantt()


if __name__ == "__main__":
    generar()
