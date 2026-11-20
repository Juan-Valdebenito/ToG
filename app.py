"""
app.py - Interfaz interactiva del simulador de red de distribución de paquetes.

Ejecutar desde la raíz del repositorio:
    streamlit run app.py

La interfaz solo dibuja y edita la red. Todos los cálculos (flujo máximo, corte
mínimo y comprobaciones) vienen de simulador/flujo.py, implementado con código
propio. Streamlit y Graphviz (DOT) se usan únicamente para mostrar resultados.
"""
import copy
import glob
import json
import os
import sys

import streamlit as st

from simulador.flujo import (arcos_activos, corte_minimo, edmonds_karp,
                             flujo_por_arco, verificar)

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "datos"))
from validar_red import validar  # noqa: E402  (reglas estructurales del enunciado)

CAP_MIN, CAP_MAX = 1, 12

# Colores de la partición del corte mínimo
COLOR_S, COLOR_T, COLOR_CORTE = "#cfe3ff", "#ffd9b3", "#d62728"


# --------------------------------------------------------------------------
# Datos y estado
# --------------------------------------------------------------------------
def redes_disponibles():
    """Resultado: {nombre visible: ruta} de todos los JSON de datos/."""
    rutas = sorted(glob.glob(os.path.join(RAIZ, "datos", "*.json")))
    redes = {}
    for ruta in rutas:
        with open(ruta, encoding="utf-8") as f:
            redes[f"{os.path.basename(ruta)} — {json.load(f)['nombre']}"] = ruta
    return redes


def cargar_red(ruta):
    """Entrada: ruta a un JSON. Efecto: deja la red en la sesión y borra resultados."""
    with open(ruta, encoding="utf-8") as f:
        st.session_state.grafo = json.load(f)
    st.session_state.archivo = os.path.basename(ruta)
    st.session_state.resultado = None
    st.session_state.mensaje = None


def buscar_arco(grafo, u, v):
    """Resultado: el diccionario del arco u -> v (activo o no), o None."""
    for a in grafo["arcos"]:
        if a["u"] == u and a["v"] == v:
            return a
    return None


def marcar_modificada(texto):
    """Efecto: deja un aviso de la modificación y marca el resultado como desactualizado."""
    st.session_state.mensaje = ("ok", texto)
    if st.session_state.resultado:
        st.session_state.resultado["desactualizado"] = True


def calcular(grafo, s, t):
    """Entrada: red, origen y destino.
    Resultado: diccionario con todo lo que la interfaz muestra tras ejecutar Edmonds–Karp."""
    vertices = [v["id"] for v in grafo["vertices"]]
    arcos = arcos_activos(grafo)
    valor, residual, iteraciones = edmonds_karp(vertices, arcos, s, t)
    x = flujo_por_arco(arcos, residual)
    S, T, corte = corte_minimo(vertices, arcos, residual, s)
    return {"s": s, "t": t, "valor": valor, "x": x, "S": S, "T": T, "corte": corte,
            "iteraciones": iteraciones,
            "verificacion": verificar(grafo, s, t, valor, x, corte),
            "grafo": copy.deepcopy(grafo), "desactualizado": False}


# --------------------------------------------------------------------------
# Dibujo de la red (lenguaje DOT de Graphviz; solo visualización)
# --------------------------------------------------------------------------
def dot_red(grafo, res, s, t):
    """Entrada: red, resultado del cálculo (o None), origen y destino elegidos.
    Resultado: texto DOT con centros, rutas dirigidas y etiquetas.
      - sin cálculo: etiqueta = capacidad c
      - con cálculo: etiqueta = flujo/capacidad, S en azul, T en naranja,
        arcos del corte en rojo y gruesos, arcos sin flujo en gris
      - rutas desactivadas: línea discontinua gris."""
    vigente = res is not None and not res["desactualizado"]
    S = set(res["S"]) if vigente else set()
    corte = {(u, v) for u, v, _ in res["corte"]} if vigente else set()

    lineas = ["digraph G {", "  rankdir=LR; bgcolor=transparent; nodesep=0.55; ranksep=1.1;",
              '  node [shape=circle, style=filled, fontname="Helvetica", fontsize=18, width=0.7, fixedsize=true];',
              '  edge [fontname="Helvetica", fontsize=17, arrowsize=0.9];']
    for vert in grafo["vertices"]:
        vid = vert["id"]
        relleno = (COLOR_S if vid in S else COLOR_T) if vigente else "#eeeeee"
        borde = ', penwidth=3, color="#222222"' if vid in (s, t) else ""
        lineas.append(f'  "{vid}" [fillcolor="{relleno}", tooltip="{vert.get("nombre", vid)}"{borde}];')

    for a in grafo["arcos"]:
        u, v, c = a["u"], a["v"], a["cap"]
        if not a.get("activo", True):
            lineas.append(f'  "{u}" -> "{v}" [label="{c} (off)", style=dashed, color="#aaaaaa", fontcolor="#aaaaaa"];')
            continue
        if not vigente:
            lineas.append(f'  "{u}" -> "{v}" [label="{c}"];')
            continue
        f = res["x"][(u, v)]
        if (u, v) in corte:
            estilo = f'color="{COLOR_CORTE}", fontcolor="{COLOR_CORTE}", penwidth=3.5'
        elif f == 0:
            estilo = 'color="#bbbbbb", fontcolor="#888888"'
        else:
            estilo = 'color="#1f4e9c", penwidth=1.8'
        lineas.append(f'  "{u}" -> "{v}" [label="{f}/{c}", {estilo}];')
    lineas.append("}")
    return "\n".join(lineas)


# --------------------------------------------------------------------------
# Interfaz
# --------------------------------------------------------------------------
st.set_page_config(page_title="Simulador de red de paquetes", layout="wide")

redes = redes_disponibles()
if "grafo" not in st.session_state:
    # Parámetros opcionales de la URL (útiles para la demo y las capturas):
    #   ?red=config_2_sin_DH.json&calcular=1
    archivo = os.path.basename(st.query_params.get("red", "red_principal.json"))
    ruta = os.path.join(RAIZ, "datos", archivo)
    cargar_red(ruta if os.path.isfile(ruta) else os.path.join(RAIZ, "datos", "red_principal.json"))
    st.session_state.comparacion = []
    if st.query_params.get("calcular"):
        g = st.session_state.grafo
        st.session_state.resultado = calcular(g, g["origen"], g["destino"])

grafo = st.session_state.grafo
ids = [v["id"] for v in grafo["vertices"]]

# ---- Barra lateral: red, origen/destino y cálculo ----
with st.sidebar:
    st.header("Red")
    eleccion = st.selectbox("Archivo de datos", list(redes),
                            index=next((i for i, n in enumerate(redes) if n.startswith(st.session_state.archivo)), 0))
    if st.button("Cargar red", width="stretch"):
        cargar_red(redes[eleccion])
        st.rerun()

    st.header("Origen y destino")
    s = st.selectbox("Origen s", ids, index=ids.index(grafo["origen"]) if grafo["origen"] in ids else 0)
    t = st.selectbox("Destino t", ids, index=ids.index(grafo["destino"]) if grafo["destino"] in ids else len(ids) - 1)

    res = st.session_state.resultado
    texto_boton = "Recalcular" if res else "Calcular flujo máximo"
    if st.button(texto_boton, type="primary", width="stretch", disabled=(s == t)):
        st.session_state.resultado = calcular(grafo, s, t)
        st.session_state.mensaje = None
        st.rerun()
    if s == t:
        st.error("El origen y el destino deben ser distintos.")

    st.divider()
    st.download_button("Descargar red actual (JSON)",
                       json.dumps({**grafo, "origen": s, "destino": t}, ensure_ascii=False, indent=2),
                       file_name="red_modificada.json", mime="application/json",
                       width="stretch")

st.title("Simulador de una red de distribución de paquetes")
st.caption("Flujo máximo con Edmonds–Karp (código propio) y corte mínimo. Capacidades en paquetes por hora.")

res = st.session_state.resultado
if res and (res["s"], res["t"]) != (s, t):
    res["desactualizado"] = True
if res and res["desactualizado"]:
    st.warning("La red, el origen o el destino cambiaron después del último cálculo. Pulsa **Recalcular**.")
if st.session_state.mensaje:
    tipo, texto = st.session_state.mensaje
    (st.success if tipo == "ok" else st.error)(texto)

vigente = res is not None and not res["desactualizado"]

# ---- Resultados principales ----
if vigente:
    ver = res["verificacion"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Flujo máximo |x|", f"{res['valor']} paq/h")
    c2.metric("Capacidad del corte c(S,T)", f"{ver['cap_corte']} paq/h")
    c3.metric("Caminos aumentantes", len(res["iteraciones"]))
    c4.metric("Comprobaciones", "✔ correctas" if ver["ok"] else "✘ fallan")

# Grafo a todo el ancho
st.graphviz_chart(dot_red(grafo, res, s, t), width="stretch")
if vigente:
    st.caption("Azul = conjunto S · Naranja = conjunto T · Rojo grueso = arcos del corte mínimo · "
               "Gris = sin flujo · Discontinuo = ruta desactivada · Etiqueta = flujo/capacidad")
else:
    st.caption("Etiqueta = capacidad. Pulsa **Calcular** para ver flujo y corte mínimo.")

if vigente:
    col_corte, col_tabla = st.columns([2, 3])
    with col_corte:
        st.subheader("Corte mínimo")
        st.markdown(f"**S** = {{{', '.join(res['S'])}}}  \n**T** = {{{', '.join(res['T'])}}}")
        suma = " + ".join(f"c({u},{v})={c}" for u, v, c in res["corte"]) or "—"
        st.markdown(f"Arcos de S hacia T: {suma} = **{res['verificacion']['cap_corte']}**")
        if res["valor"] == res["verificacion"]["cap_corte"]:
            st.success(f"Flujo máximo = capacidad del corte = {res['valor']} (teorema flujo máximo–corte mínimo).")
    with col_tabla:
        st.subheader("Flujo por arco")
        corte = {(u, v) for u, v, _ in res["corte"]}
        filas = []
        for (u, v), f in res["x"].items():
            c = buscar_arco(res["grafo"], u, v)["cap"]
            estado = "corte S→T" if (u, v) in corte else ("saturado" if f == c else ("sin flujo" if f == 0 else ""))
            filas.append({"Arco": f"{u} → {v}", "Flujo x": f, "Capacidad c": c, "Estado": estado})
        st.dataframe(filas, hide_index=True, width="stretch")
else:
    with st.expander("Rutas de la red"):
        st.dataframe([{"Arco": f"{a['u']} → {a['v']}", "Capacidad c": a["cap"],
                       "Activa": "sí" if a.get("activo", True) else "no"} for a in grafo["arcos"]],
                     hide_index=True, width="stretch")

if vigente:
    with st.expander("Detalle del cálculo y comprobaciones"):
        st.markdown("**Caminos aumentantes encontrados por BFS (en orden):**")
        for i, (camino, cuello) in enumerate(res["iteraciones"], 1):
            st.markdown(f"{i}. {' → '.join(camino)} — cuello de botella **{cuello}**")
        ver = res["verificacion"]
        st.markdown("**Comprobaciones del apartado 5:**")
        st.markdown(f"- Capacidad 0 ≤ x ≤ c en todos los arcos: {'✔' if not ver['capacidad'] else '✘ ' + str(ver['capacidad'])}")
        st.markdown(f"- Conservación en los vértices intermedios: {'✔' if not ver['conservacion'] else '✘ ' + str(ver['conservacion'])}")
        st.markdown(f"- Valor neto que sale de s = {ver['valor_neto']}, c(S,T) = {ver['cap_corte']}: "
                    f"{'✔ coinciden' if ver['valor_neto'] == ver['cap_corte'] else '✘ no coinciden'}")

# ---- Modificaciones de la red ----
st.header("Modificar la red")
nombres_arcos = [f"{a['u']} → {a['v']}" for a in grafo["arcos"]]
tab_off, tab_cap, tab_new = st.tabs(["Desactivar / activar ruta", "Cambiar capacidad", "Agregar conexión"])

with tab_off:
    sel = st.selectbox("Ruta", nombres_arcos, key="sel_off")
    arco = grafo["arcos"][nombres_arcos.index(sel)]
    activo = arco.get("activo", True)
    if st.button("Desactivar ruta" if activo else "Activar ruta", key="btn_off"):
        if not activo and (r := buscar_arco(grafo, arco["v"], arco["u"])) and r.get("activo", True):
            st.session_state.mensaje = ("error", f"No se puede activar {sel}: crearía arcos recíprocos con {arco['v']} → {arco['u']}.")
        else:
            arco["activo"] = not activo
            marcar_modificada(f"Ruta {sel} {'desactivada' if activo else 'activada'}.")
        st.rerun()

with tab_cap:
    sel = st.selectbox("Ruta", nombres_arcos, key="sel_cap")
    arco = grafo["arcos"][nombres_arcos.index(sel)]
    nueva = st.number_input("Nueva capacidad (paquetes/hora)", CAP_MIN, CAP_MAX, value=arco["cap"], step=1, key=f"cap_{sel}")
    if st.button("Aplicar capacidad", key="btn_cap"):
        anterior, arco["cap"] = arco["cap"], int(nueva)
        marcar_modificada(f"Capacidad de {sel}: {anterior} → {arco['cap']}.")
        st.rerun()

with tab_new:
    c1, c2, c3 = st.columns(3)
    u = c1.selectbox("Desde", ids, key="new_u")
    v = c2.selectbox("Hacia", ids, index=1, key="new_v")
    cap = c3.number_input("Capacidad", CAP_MIN, CAP_MAX, value=5, step=1, key="new_cap")
    if st.button("Agregar conexión", key="btn_new"):
        directo, reciproco = buscar_arco(grafo, u, v), buscar_arco(grafo, v, u)
        if u == v:
            error = "No se admiten lazos (origen y destino de la ruta iguales)."
        elif directo:
            error = f"La ruta {u} → {v} ya existe" + (" (está desactivada: actívala en la primera pestaña)." if not directo.get("activo", True) else ".")
        elif reciproco and reciproco.get("activo", True):
            error = f"No se admiten arcos recíprocos: ya existe {v} → {u}."
        else:
            error = None
        if error:
            st.session_state.mensaje = ("error", f"Conexión rechazada. {error}")
        else:
            grafo["arcos"].append({"u": u, "v": v, "cap": int(cap), "activo": True})
            marcar_modificada(f"Conexión {u} → {v} agregada con capacidad {int(cap)}.")
        st.rerun()

activos = [a for a in grafo["arcos"] if a.get("activo", True)]
errores = validar(ids, activos, s, t, inicial=False)
if errores:
    st.info("Observaciones sobre la red actual: " + "; ".join(errores))

# ---- Comparación de configuraciones ----
st.header("Comparar configuraciones")
st.caption("Guarda el resultado actual o carga directamente las tres configuraciones del proyecto.")
b1, b2, b3 = st.columns(3)
etiqueta = b1.text_input("Nombre de la configuración", value=grafo["nombre"][:60])
if b2.button("Guardar resultado actual", disabled=not vigente, width="stretch"):
    st.session_state.comparacion.append((etiqueta, res))
    st.rerun()
if b3.button("Cargar las 3 configuraciones del proyecto", width="stretch"):
    st.session_state.comparacion = []
    for archivo in ["red_principal.json", "config_2_sin_DH.json", "config_3_nueva_ET.json"]:
        with open(os.path.join(RAIZ, "datos", archivo), encoding="utf-8") as f:
            g = json.load(f)
        st.session_state.comparacion.append((g["nombre"], calcular(g, g["origen"], g["destino"])))
    st.rerun()

if st.session_state.comparacion:
    base = st.session_state.comparacion[0][1]["valor"]
    st.dataframe([{"Configuración": nombre,
                   "s → t": f"{r['s']} → {r['t']}",
                   "Arcos activos": len(r["x"]),
                   "Flujo máximo": r["valor"],
                   "Δ vs. primera": r["valor"] - base,
                   "S": "{" + ", ".join(r["S"]) + "}",
                   "T": "{" + ", ".join(r["T"]) + "}",
                   "Arcos del corte": ", ".join(f"{u}→{v} ({c})" for u, v, c in r["corte"]),
                   "Verificación": "✔" if r["verificacion"]["ok"] else "✘"}
                  for nombre, r in st.session_state.comparacion],
                 hide_index=True, width="stretch")
    if st.button("Vaciar comparación"):
        st.session_state.comparacion = []
        st.rerun()
