import re
from pathlib import Path

from definicion import AUXILIARES, CAUSAL, CONSTANTES, CONTROLES, FLUJOS, NIVELES

CARPETA = Path(__file__).resolve().parent

ENCABEZADO_VISTA = "$192-192-192,0,Times New Roman|12||0-0-0|0-0-0|0-0-255|-1--1--1|-1--1--1|96,96,100,0"
COLA_ARCHIVO = """///---\\\\\\
:L<%^E!@
1:Current.vdf
9:Current
15:0,0,0,0,0,0
19:100,0
27:2,
34:0,
4:Time
5:{variable}
35:Date
36:YYYY-MM-DD
37:2000
38:1
39:1
40:2
41:0
42:1
24:0
25:{final}
26:{final}
"""
POLARIDAD = {"+": 43, "-": 45, "": 0}


def nombres_en(ecuacion, conocidos):
    encontrados = []
    for nombre in sorted(conocidos, key=len, reverse=True):
        patron = r"(?<!\w)" + re.escape(nombre) + r"(?!\w)"
        if re.search(patron, ecuacion):
            encontrados.append(nombre)
            ecuacion = re.sub(patron, "", ecuacion)
    return encontrados


def bloque(nombre, ecuacion, unidades, nota):
    return f"{nombre}= {ecuacion}\n\t~\t{unidades}\n\t~\t{nota}\n\t|\n\n"


def bloque_control():
    texto = ""
    for nombre, valor in CONTROLES.items():
        texto += bloque(nombre, str(valor), "Hora", "Parametro de control de la simulacion")
    return texto + bloque("SAVEPER", "TIME STEP", "Hora", "Frecuencia de registro")


def ecuaciones_flujos_niveles():
    texto = ""
    for nombre, n in NIVELES.items():
        entradas = [f for f, d in FLUJOS.items() if d["hacia"] == nombre]
        salidas = [f for f, d in FLUJOS.items() if d["desde"] == nombre]
        expresion = "+".join(entradas) + "".join(f"-{s}" for s in salidas)
        texto += bloque(nombre, f"INTEG({expresion}, {n['inicial']})", n["unidades"], n["nota"])
    for nombre, f in FLUJOS.items():
        texto += bloque(nombre, f["ecuacion"], f["unidades"], f["nota"])
    for nombre, a in AUXILIARES.items():
        texto += bloque(nombre, a["ecuacion"], a["unidades"], a["nota"])
    for nombre, c in CONSTANTES.items():
        texto += bloque(nombre, str(c["valor"]), c["unidades"], c["nota"])
    return texto + bloque_control()


def punto_medio(a, b):
    return round((a[0] + b[0]) / 2), round((a[1] + b[1]) / 2)


def flecha(numero, origen, destino, posiciones, forma=0, polaridad=0, grosor=0, tipo=192):
    x, y = punto_medio(posiciones[origen], posiciones[destino])
    return f"1,{numero},{origen},{destino},{forma},0,{polaridad},{grosor},0,{tipo},0,-1--1--1,,1|({x},{y})|"


def croquis_flujos_niveles():
    elementos, posiciones, identificadores = [], {}, {}
    contador = iter(range(1, 10_000))

    def registrar(texto, identificador, x, y):
        elementos.append(texto)
        posiciones[identificador] = (x, y)

    for nombre, n in NIVELES.items():
        identificadores[nombre] = next(contador)
        registrar(f"10,{identificadores[nombre]},{nombre},{n['x']},{n['y']},40,20,3,3,0,0,0,0,0,0", identificadores[nombre], n["x"], n["y"])
    for nombre, a in list(AUXILIARES.items()) + list(CONSTANTES.items()):
        identificadores[nombre] = next(contador)
        registrar(f"10,{identificadores[nombre]},{nombre},{a['x']},{a['y']},40,20,8,3,0,0,0,0,0,0", identificadores[nombre], a["x"], a["y"])
    valvulas = {}
    for nombre, f in FLUJOS.items():
        valvula, etiqueta = next(contador), next(contador)
        valvulas[nombre], identificadores[nombre] = valvula, etiqueta
        registrar(f"11,{valvula},48,{f['x']},{f['y']},6,8,34,3,0,0,1,0,0,0", valvula, f["x"], f["y"])
        registrar(f"10,{etiqueta},{nombre},{f['x']},{f['y'] + 25},40,11,40,3,0,0,-1,0,0,0", etiqueta, f["x"], f["y"] + 25)
        extremos = [(f["desde"], valvula, 100), (valvula, f["hacia"], 4)]
        for origen, destino, forma in extremos:
            if origen is None or destino is None:
                nube = next(contador)
                x, y = f["nube"]
                registrar(f"12,{nube},48,{x},{y},10,8,0,3,0,0,-1,0,0,0", nube, x, y)
                origen, destino = (nube, valvula) if origen is None else (valvula, nube)
            origen = identificadores.get(origen, origen)
            destino = identificadores.get(destino, destino)
            elementos.append(flecha(next(contador), origen, destino, posiciones, forma, 0, 22, 0))
    conocidos = list(NIVELES) + list(AUXILIARES) + list(CONSTANTES) + list(FLUJOS)
    for nombre, definicion in list(FLUJOS.items()) + list(AUXILIARES.items()):
        destino = valvulas.get(nombre, identificadores[nombre])
        for dependencia in nombres_en(definicion["ecuacion"], conocidos):
            elementos.append(flecha(next(contador), identificadores[dependencia], destino, posiciones))
    return "\n".join(elementos)


def archivo_flujos_niveles():
    final = CONTROLES["FINAL TIME"]
    cuerpo = ecuaciones_flujos_niveles()
    vista = f"\\\\\\---/// Sketch information - do not modify anything except names\nV300  Do not put anything below this section - it will be ignored\n*Flujos y niveles\n{ENCABEZADO_VISTA}\n{croquis_flujos_niveles()}\n"
    return "{UTF-8}\n" + cuerpo + vista + COLA_ARCHIVO.format(variable="Cola de espera", final=final)


def archivo_causal():
    variables = CAUSAL["variables"]
    cuerpo = ""
    for nombre in variables:
        causas = [o for o, d, _ in CAUSAL["enlaces"] if d == nombre]
        cuerpo += f"{nombre}= A FUNCTION OF({', '.join(causas) if causas else nombre})\n\t~\tDmnl\n\t~\tVariable del diagrama causal\n\t|\n\n"
    cuerpo += bloque_control()
    elementos, identificadores, posiciones = [], {}, {}
    for numero, (nombre, (x, y)) in enumerate(variables.items(), start=1):
        identificadores[nombre] = numero
        posiciones[numero] = (x, y)
        elementos.append(f"10,{numero},{nombre},{x},{y},40,20,8,3,0,0,0,0,0,0")
    siguiente = len(variables)
    for origen, destino, signo in CAUSAL["enlaces"]:
        siguiente += 1
        elementos.append(flecha(siguiente, identificadores[origen], identificadores[destino], posiciones, 0, POLARIDAD[signo]))
    vista = f"\\\\\\---/// Sketch information - do not modify anything except names\nV300  Do not put anything below this section - it will be ignored\n*Diagrama causal\n{ENCABEZADO_VISTA}\n" + "\n".join(elementos) + "\n"
    return "{UTF-8}\n" + cuerpo + vista + COLA_ARCHIVO.format(variable="Cola de espera", final=CONTROLES["FINAL TIME"])


def generar():
    (CARPETA / "turnos_flujos_niveles.mdl").write_text(archivo_flujos_niveles(), encoding="utf-8")
    (CARPETA / "turnos_causal.mdl").write_text(archivo_causal(), encoding="utf-8")


if __name__ == "__main__":
    generar()
