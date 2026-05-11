import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# ─────────────────────────────────────────────
#  PAGE CONFIG — SIN SIDEBAR
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CRF — Unidad Minera Cerro Lindo",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# FORZAR DESAPARICIÓN TOTAL DEL SIDEBAR
st.markdown("""
<style>

 /* ─────────────────────────────────────────────
      OCULTAR SIDEBAR
   ───────────────────────────────────────────── */
section[data-testid="stSidebar"] {display: none !important;}
div[data-testid="stSidebarNav"] {display: none !important;}


 /* ─────────────────────────────────────────────
      TIPOGRAFÍA GLOBAL — LATO
   ───────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Lato', sans-serif !important;
    font-size: 12px !important;
    color: #e6edf3 !important;
}

/* Titulos principales */
h1, h2 {
    font-family: 'Lato', sans-serif !important;
    font-weight: 900 !important;
    font-size: 14px !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #f0a500 !important;
}

/* Titulos secundarios */
h3, h4 {
    font-family: 'Lato', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    color: #f0a500 !important;
}


 /* ─────────────────────────────────────────────
      FONDO GENERAL
   ───────────────────────────────────────────── */
.stApp {
    background: #0b253a !important;
    color: #e6edf3 !important;
}


 /* ─────────────────────────────────────────────
      PESTAÑAS — COLORES Y TIPOGRAFÍA
   ───────────────────────────────────────────── */
.stTabs [data-baseweb="tab"] {
    font-family: 'Lato', sans-serif !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    color: #e6edf3 !important;
}

.stTabs [aria-selected="true"] {
    color: #ffffff !important;
    font-weight: 900 !important;
    border-bottom: 3px solid #f0a500 !important;
}


 /* ─────────────────────────────────────────────
      BANNER
   ───────────────────────────────────────────── */
.hero-banner {
    background: linear-gradient(135deg, #1a2332 0%, #0d1117 50%, #1a1f26 100%);
    border: 1px solid #f0a500;
    border-left: 4px solid #f0a500;
    border-radius: 4px;
    padding: 8px 14px;
    margin-bottom: 10px;
}

.hero-banner h1 {
    color: #f0a500;
    font-size: 18px !important;  /* equivalente a 14 pt */
}

.hero-banner p {
    color: #8b949e;
    font-size: 12px !important;
}


 /* ─────────────────────────────────────────────
      TABLAS
   ───────────────────────────────────────────── */
.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px !important;
}

.styled-table th {
    background: #1f2937;
    color: #f0a500;
    padding: 8px 12px;
    text-transform: uppercase;
    font-size: 12px !important;
}

.styled-table td {
    padding: 7px 12px;
    border-bottom: 1px solid #1f2937;
    color: #c9d1d9;
    font-size: 12px !important;
}

.styled-table tr:hover td {
    background: #1a2030;
}


 /* ─────────────────────────────────────────────
      INFO BOX
   ───────────────────────────────────────────── */
.info-box {
    background: #1a2332;
    border-left: 4px solid #388bfd;
    padding: 12px 16px;
    font-size: 12px !important;
}


 /* ─────────────────────────────────────────────
      FORMULAS
   ───────────────────────────────────────────── */
.formula-box {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 16px 20px;
    color: #79c0ff;
    font-size: 12px !important;
    font-family: 'Courier New', monospace;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PLOTLY THEME
# ─────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#161b22",
    font=dict(family="Source Sans 3", color="#c9d1d9"),
    xaxis=dict(gridcolor="#21262d", linecolor="#30363d"),
    yaxis=dict(gridcolor="#21262d", linecolor="#30363d"),
    margin=dict(l=50, r=30, t=50, b=50),
)
COLORS = ["#f0a500", "#3fb950", "#388bfd", "#f85149"]

# ─────────────────────────────────────────────
#  FUNCIÓN TABLA HTML (REUSADA)
# ─────────────────────────────────────────────
def render_table(df):
    rows = ""
    for _, row in df.iterrows():
        cols = "".join(f"<td>{v}</td>" for v in row)
        rows += f"<tr>{cols}</tr>"
    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    return f'<table class="styled-table"><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>'

# ─────────────────────────────────────────────
#  BANNER PRINCIPAL
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <h1> Cemented Rock Fill (CRF) </h1>
  <p>Análisis técnico-económico de factibilidad del relleno detrítico cementado · Método Sub Level Stoping</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  DEFINICIÓN DE PESTAÑAS
# ─────────────────────────────────────────────
tabs = st.tabs([
    "🧪 Diseños de Mezcla",
    "📐 Diseño Seleccionado",
    "🏗️ Infraestructura",
    "📊 Cálculos Geomecánicos",
])

# ╔══════════════════════════════════════════════╗
#  TAB 1 — DISEÑOS DE MEZCLA (COMPLETO ACTUALIZADO)
# ╚══════════════════════════════════════════════╝
with tabs[0]:

    st.markdown("###  Diseños de Mezcla — Prueba Piloto")

    st.markdown("""
    Se ingresa los valores de 4 diseños de muestra
    (D01 – D04).  
    Se ingresan las resistencias reales obtenidas en campo.
    """)

    # ----------------------------
    # DATOS INICIALES
    # ----------------------------
    if "designs_df" not in st.session_state:

        st.session_state.designs_df = pd.DataFrame({
            "Diseño": ["D01", "D02", "D03", "D04"],
            "Cemento (kg/m³)": [75, 90, 103, 138],
            "Agua (L/m³)": [60, 72, 82, 110],
            "Desmonte (kg/m³)": [2812, 2760, 2717, 2595],
            "Densidad (kg/m³)": [2947, 2922, 2902, 2843],
        })

    df = st.session_state.designs_df.copy()

    # -------------------------------------------
    # ENTRADAS EDITABLES PARA DISEÑOS
    # -------------------------------------------
    st.markdown("####  Ingresar Datos del Diseño (kg/m³ y L/m³)")

    edit_cols = st.columns(4)

    for i in range(4):
        with edit_cols[i]:
            st.markdown(f"##### {df.loc[i,'Diseño']}")

            df.loc[i, "Cemento (kg/m³)"] = st.number_input(
                f"Cemento {df.loc[i,'Diseño']}",
                value=float(df.loc[i,"Cemento (kg/m³)"]),
                key=f"cem_{i}"
            )

            df.loc[i, "Agua (L/m³)"] = st.number_input(
                f"Agua {df.loc[i,'Diseño']}",
                value=float(df.loc[i,"Agua (L/m³)"]),
                key=f"agua_{i}"
            )

            df.loc[i, "Desmonte (kg/m³)"] = st.number_input(
                f"Desmonte {df.loc[i,'Diseño']}",
                value=float(df.loc[i,"Desmonte (kg/m³)"]),
                key=f"des_{i}"
            )

            df.loc[i, "Densidad (kg/m³)"] = st.number_input(
                f"Densidad {df.loc[i,'Diseño']}",
                value=float(df.loc[i,"Densidad (kg/m³)"]),
                key=f"dens_{i}"
            )

    # ------------------------------------------------------
    # CÁLCULOS: porcentajes y relación A/C
    # ------------------------------------------------------
    df["Total"] = df["Cemento (kg/m³)"] + df["Agua (L/m³)"] + df["Desmonte (kg/m³)"]
    df["Cemento (%)"] = df["Cemento (kg/m³)"] / df["Total"] * 100
    df["Agua (%)"] = df["Agua (L/m³)"] / df["Total"] * 100
    df["Desmonte (%)"] = df["Desmonte (kg/m³)"] / df["Total"] * 100

    df["A/C"] = df["Agua (L/m³)"] / df["Cemento (kg/m³)"]

    st.session_state.designs_df = df

    # -------------------------------
    # MOSTRAR TABLA COMPLETA (REORDENADA)
    # -------------------------------
    table_df = df[[ 
        "Diseño",
        "Cemento (kg/m³)", "Cemento (%)",
        "Agua (L/m³)", "Agua (%)",
        "Desmonte (kg/m³)", "Desmonte (%)",
        "Densidad (kg/m³)",
        "A/C"
    ]].copy()

    st.markdown(render_table(table_df), unsafe_allow_html=True)

    # ═══════════════════════════════════════
    # RESISTENCIAS — TABLA EDITABLE
    # ═══════════════════════════════════════
    st.markdown("###  Desarrollo de Resistencia a Compresión (MPa)")

    dias_lista = [7, 14, 21, 28, 56]

    if "resist_df" not in st.session_state:
        st.session_state.resist_df = pd.DataFrame({
            "Días": dias_lista,
            "D01": [0.65, 1.01, 1.39, 1.66, 1.68],
            "D02": [1.07, 1.37, 1.63, 2.08, 2.11],
            "D03": [1.68, 2.73, 3.38, 4.82, 4.95],
            "D04": [2.58, 3.14, 4.41, 5.21, 6.53],
        })

    resist_df = st.session_state.resist_df.copy()

    res_cols = st.columns(4)

    for j, d in enumerate(["D01","D02","D03","D04"]):
        with res_cols[j]:
            st.markdown(f"#### {d}")
            for i, dia in enumerate(dias_lista):
                resist_df.loc[i, d] = st.number_input(
                    f"{d} a {dia} días",
                    value=float(resist_df.loc[i,d]),
                    key=f"{d}_{dia}"
                )

    st.session_state.resist_df = resist_df

    # -------------------------------
    # MOSTRAR TABLA DE RESISTENCIAS
    # -------------------------------
    st.markdown(render_table(resist_df), unsafe_allow_html=True)

    # ==================================================
    # NUEVA UBICACIÓN → SELECCIÓN DE DISEÑO
    # ==================================================
    st.markdown("###  Seleccionar Diseño")

    selected = st.selectbox(
        "Seleccione un diseño:",
        df["Diseño"].tolist(),
        key="select_design"
    )

    st.session_state.selected_design = selected

    st.info(f"📌 Diseño seleccionado: **{selected}**")

    # -------------------------------
    # GRAFICO DE RESISTENCIAS DINÁMICO
    # -------------------------------
    st.markdown("###  Curva de Resistencia")

    fig_res = go.Figure()

    for d, color in zip(["D01","D02","D03","D04"], COLORS):

        width = 4 if d == selected else 2
        opacity = 1.0 if d == selected else 0.3

        fig_res.add_trace(go.Scatter(
            x=resist_df["Días"],
            y=resist_df[d],
            mode="lines+markers",
            name=d,
            opacity=opacity,
            line=dict(color=color, width=width)
        ))

    fig_res.update_layout(
        **PLOTLY_LAYOUT,
        height=380,
        title=f"Curva de Resistencia — Diseño Seleccionado: {selected}"
    )

    st.plotly_chart(fig_res, use_container_width=True)

    # ---------------------------------
    # GRÁFICO DE 28 DÍAS DINÁMICO
    # ---------------------------------
    st.markdown("###  Resistencia a 28 días")

    res_28 = resist_df[resist_df["Días"]==28].iloc[0]

    fig_28 = go.Figure()

    for d, color in zip(["D01","D02","D03","D04"], COLORS):

        opacity = 1.0 if d == selected else 0.25

        fig_28.add_trace(go.Bar(
            x=[d],
            y=[res_28[d]],
            marker_color=color,
            opacity=opacity,
            text=[f"{res_28[d]:.2f} MPa"],
            textposition="outside"
        ))

    fig_28.update_layout(
        **PLOTLY_LAYOUT,
        title=f"Resistencia a 28 días — Diseño: {selected}",
        height=360,
        showlegend=False
    )

    st.plotly_chart(fig_28, use_container_width=True)

# ╔══════════════════════════════════════════════╗
#  TAB 2 — DISEÑO DE MEZCLA SELECCIONADO (COMPLETO)
# ╚══════════════════════════════════════════════╝
with tabs[1]:

    st.markdown("## 📐 Diseño de Mezcla Seleccionado")

    # ------------------------------------------------------------------------------------------------
    # 1. OBTENER DISEÑO SELECCIONADO DE LA PESTAÑA ANTERIOR
    # ------------------------------------------------------------------------------------------------
    if "selected_design" not in st.session_state:
        st.warning("Seleccione un diseño en la pestaña anterior.")
        st.stop()

    selected = st.session_state.selected_design

    st.markdown(f"### 🎯 Diseño seleccionado: **{selected}**")

    df_all = st.session_state.designs_df.copy()
    df_resist = st.session_state.resist_df.copy()

    row = df_all[df_all["Diseño"] == selected].iloc[0]

    # Datos heredados
    cem = row["Cemento (kg/m³)"]
    agua = row["Agua (L/m³)"]
    desm = row["Desmonte (kg/m³)"]
    densidad_base = row["Densidad (kg/m³)"]
    rel_ac = row["A/C"]

    resist_28 = df_resist[df_resist["Días"] == 28][selected].values[0]

    # ------------------------------------------------------------------------------------------------
    # 2. INGRESO DE ESPECIFICACIONES DEL DISEÑO (MANUALES MENOS A/C)
    # ------------------------------------------------------------------------------------------------
    st.markdown("### 🧱 Especificaciones del Diseño (Ingresadas por el usuario)")

    col1, col2, col3 = st.columns(3)

    with col1:
        Fc = st.number_input("F'c especificado (kg/cm²)", value=20)
    with col2:
        Fcr = st.number_input("F'cr requerido (kg/cm²)", value=30)
    with col3:
        slump = st.number_input("Consistencia requerida (Slump, pulgadas)", value=0)

    col4, col5, col6 = st.columns(3)
    with col4:
        agua_industrial = st.number_input("Volumen unitario de agua industrial (L/m³)", value=72)
    with col5:
        aire_atrapado = st.selectbox("Contenido de aire atrapado (%)", [1,2,3,4,5])
    with col6:
        st.number_input("Relación agua/cemento (heredada)", value=float(rel_ac), disabled=True)

    # ------------------------------------------------------------------------------------------------
    # 3. CARACTERÍSTICAS DEL AGREGADO (TODAS MANUALES)
    # ------------------------------------------------------------------------------------------------
    st.markdown("### 🪨 Características del Agregado (Ingresadas por el usuario)")

    colA, colB, colC = st.columns(3)
    with colA:
        tam_max = st.text_input("Tamaño máximo (pulg.)", value='3"')
        tam_nom = st.text_input("Tamaño máximo nominal (pulg.)", value='2"')
        mod_fineza = st.number_input("Módulo de fineza", value=8.4)
    with colB:
        peso_suelto = st.number_input("Peso unitario suelto (kg/m³)", value=1787)
        peso_compact = st.number_input("Peso unitario compactado (kg/m³)", value=1914)
        peso_esp_masa = st.number_input("Peso específico del agregado (kg/m³)", value=3012)
    with colC:
        humedad_nat = st.number_input("Contenido de humedad natural (%)", value=3.1)
        absorcion = st.number_input("Contenido de absorción (%)", value=0.6)

    # ------------------------------------------------------------------------------------------------
    # 4. CARACTERÍSTICAS DE LOS ADICIONADOS
    # ------------------------------------------------------------------------------------------------
    st.markdown("### 🧪 Características de los Adicionados")

    colAD1, colAD2 = st.columns(2)
    with colAD1:
        peso_esp_cem = st.number_input("Peso específico del cemento (kg/m³)", value=3110)
    with colAD2:
        dens_agua = st.number_input("Densidad aparente del agua (kg/m³)", value=1.0)

    # Mostrar tabla
    df_adic = pd.DataFrame({
        "Propiedad": ["Peso específico del cemento", "Densidad del agua"],
        "Valor": [peso_esp_cem, dens_agua]
    })
    st.markdown(render_table(df_adic), unsafe_allow_html=True)

    # ------------------------------------------------------------------------------------------------
    # 5. CÁLCULO DE DISEÑO DE MEZCLA (NUEVO)
    # ------------------------------------------------------------------------------------------------
    st.markdown("## 📏 Cálculo del Diseño de Mezcla")

    # Agregado corregido por humedad
    agregado_corregido = desm / (1 + humedad_nat/100)

    # Aporte de agua por humedad/absorción
    aporte_agua = agregado_corregido * ((humedad_nat - absorcion) / 100)

    # Densidad final (cemento + agua industrial + aporte + agregado corregido)
    densidad_mezcla = cem + agua_industrial + aporte_agua + agregado_corregido

    # Tabla
    df_calc = pd.DataFrame({
        "Concepto": [
            "Cemento (kg/m³)",
            "Agua industrial (L/m³)",
            "Agregado corregido (kg/m³)",
            "Aporte de agua humedad/absorción (L/m³)",
            "Aire (%)",
            "Densidad mezcla final (kg/m³)"
        ],
        "Valor": [
            f"{cem:.2f}",
            f"{agua_industrial:.2f}",
            f"{agregado_corregido:.2f}",
            f"{aporte_agua:.2f}",
            f"{aire_atrapado}%",
            f"{densidad_mezcla:.2f}"
        ]
    })
    st.markdown(render_table(df_calc), unsafe_allow_html=True)

    # ------------------------------------------------------------------------------------------------
    # 6. CÁLCULOS POR TANDA
    # ------------------------------------------------------------------------------------------------
    st.markdown("### 🧮 Cálculo por Tanda")

    tanda = st.number_input("Tanda (m³ por ciclo)", value=10.0)

    cement_t = cem * tanda
    agua_t = (agua_industrial + aporte_agua) * tanda
    agr_t = agregado_corregido * tanda

    df_tanda = pd.DataFrame({
        "Material": ["Cemento", "Agua (total)", "Agregado"],
        "Por tanda": [f"{cement_t:.2f}", f"{agua_t:.2f}", f"{agr_t:.2f}"]
    })
    st.markdown(render_table(df_tanda), unsafe_allow_html=True)

    # ------------------------------------------------------------------------------------------------
    # 7. TABLA FINAL — DOSIFICACIÓN DE MEZCLA
    # ------------------------------------------------------------------------------------------------
    st.markdown("## 🧾 DOSIFICACIÓN DE MEZCLA (Resumen Final)")

    df_dosi = pd.DataFrame({
        "Componente": ["Cemento", "Desmonte", "Agua", "Relación A/C", "Densidad final"],
        "Valor": [
            f"{cem:.2f} kg/m³",
            f"{desm:.2f} kg/m³",
            f"{agua_industrial:.2f} L/m³",
            f"{rel_ac:.2f}",
            f"{densidad_mezcla:.2f} kg/m³"
        ]
    })
    st.markdown(render_table(df_dosi), unsafe_allow_html=True)

    # ------------------------------------------------------------------------------------------------
    # 8. GRÁFICOS
    # ------------------------------------------------------------------------------------------------

    st.markdown("### 📊 Gráficos del Diseño Seleccionado")

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        # Pie
        fig_pie = go.Figure(go.Pie(
            labels=["Cemento", "Agua", "Agregado"],
            values=[cem, agua_industrial + aporte_agua, agregado_corregido],
            hole=0.35
        ))
        fig_pie.update_layout(**PLOTLY_LAYOUT, title=f"Composición CRF — {selected}")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_g2:
        # Bars
        fig_bar = go.Figure(go.Bar(
            x=["Cemento", "Agua total", "Agregado"],
            y=[cem, agua_industrial + aporte_agua, agregado_corregido],
            marker_color=["#3fb950", "#388bfd", "#f0a500"],
            text=[f"{cem:.1f}", f"{agua_industrial+aporte_agua:.1f}", f"{agregado_corregido:.1f}"],
            textposition="outside"
        ))
        fig_bar.update_layout(**PLOTLY_LAYOUT, title="Componentes por m³")
        st.plotly_chart(fig_bar, use_container_width=True)

    # ------------------------------------------------------------------------------------------------
    # 9. BOTÓN GUARDAR (solo si todo está lleno)
    # ------------------------------------------------------------------------------------------------

    campos_completos = all([
        Fc, Fcr, slump, agua_industrial,
        tam_max, tam_nom, mod_fineza,
        peso_suelto, peso_compact, peso_esp_masa,
        humedad_nat, absorcion
    ])

    if campos_completos:
        if st.button("💾 Guardar Diseño"):
            st.session_state.saved_mix = {
                "diseño": selected,
                "cemento": cem,
                "agua": agua_industrial,
                "agregado": desm,
                "rel_ac": rel_ac,
                "densidad_mezcla": densidad_mezcla,
                "aire": aire_atrapado,
                "resistencia_28d": resist_28
            }
            st.success("✔ Diseño guardado correctamente.")
    else:
        st.info("Complete todos los campos para habilitar el guardado.")

# ╔══════════════════════════════════════════════╗
#  TAB 3 — INFRAESTRUCTURA (MODELO MINERO COMPLETO)
# ╚══════════════════════════════════════════════╝

with tabs[2]:

    st.markdown("## 🏗️ Infraestructura · Cámara de Mezclado del CRF")

    st.markdown("""
    En esta sección se definen las características geométricas y operativas 
    de la cámara de mezclado en el nivel 14 de la Unidad Minera.  
    Incluye selección del gradiente del piso, configuración estructural 
    y la visualización del perfil minero con detalle ampliado (1:20).
    """)

    # ─────────────────────────────────────────────
    #  1. DATOS DE EQUIPOS PRINCIPALES
    # ─────────────────────────────────────────────
    st.markdown("### ⚙️ Equipos Principales (Se mantienen)")

    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        eq_bomba = st.number_input("Bomba estacionaria (m³/h)", value=50)
        eq_chancadora = st.number_input("Chancadora secundaria (t/h)", value=120)
    with col_eq2:
        eq_faja = st.number_input("Faja transportadora (t/h)", value=300)
        eq_tolva = st.number_input("Tolva de regulación (m³)", value=25)

    df_equipos = pd.DataFrame({
        "Equipo": ["Bomba", "Chancadora", "Faja Transportadora", "Tolva"],
        "Capacidad": [eq_bomba, eq_chancadora, eq_faja, eq_tolva]
    })
    st.markdown(render_table(df_equipos), unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    #  2. PERSONAL DIRECTO
    # ─────────────────────────────────────────────
    st.markdown("### 👷 Personal Directo Requerido")

    col_pe1, col_pe2, col_pe3 = st.columns(3)
    with col_pe1:
        per_oper = st.number_input("Operadores", value=3)
    with col_pe2:
        per_mant = st.number_input("Mecánicos", value=1)
    with col_pe3:
        per_sup = st.number_input("Supervisor", value=1)

    df_personal = pd.DataFrame({
        "Cargo": ["Operador", "Mecánico", "Supervisor"],
        "Cantidad": [per_oper, per_mant, per_sup]
    })
    st.markdown(render_table(df_personal), unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    #  3. PARÁMETROS DE LA CÁMARA DE MEZCLADO
    # ─────────────────────────────────────────────
    st.markdown("## 📐 Geometría de la Cámara de Mezclado")

    col1, col2, col3 = st.columns(3)
    with col1:
        largo = st.number_input("Longitud de la cámara (m)", value=18.0)
        ancho = st.number_input("Ancho útil (m)", value=4.0)
        alto = st.number_input("Altura útil (m)", value=4.5)
    with col2:
        esp_conc = st.number_input("Espesor de concreto (m)", value=0.20)
        esp_shot = st.number_input("Espesor de shotcrete (m)", value=0.10)
        esp_relleno = st.number_input("Espesor del relleno estructural (m)", value=0.40)
    with col3:
        altura_buzon = st.number_input("Altura del buzón (m)", value=3.0)
        ancho_bandeja = st.number_input("Ancho de bandeja (m)", value=1.2)
        pendiente = st.selectbox("Pendiente del piso (%)", [-1, -2])

    # ----------------------------
    # CÁLCULOS DE VOLÚMENES
    # ----------------------------
    piso_drop = largo * (abs(pendiente)/100)
    volumen_util = largo * ancho * alto
    volumen_r = largo * ancho * esp_conc
    volumen_excavado = (ancho + 2*esp_conc) * (alto + 2*esp_conc) * largo

    df_vol = pd.DataFrame({
        "Concepto": [
            "Volumen útil de la cámara (m³)",
            "Caída del piso por pendiente (m)",
            "Volumen de concreto del piso (m³)",
            "Volumen excavado total (m³)"
        ],
        "Valor": [
            f"{volumen_util:.2f}",
            f"{piso_drop:.2f}",
            f"{volumen_r:.2f}",
            f"{volumen_excavado:.2f}"
        ]
    })
    st.markdown("### 📦 Cálculos de Volúmenes")
    st.markdown(render_table(df_vol), unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # 4. GRÁFICO DEL PERFIL MINERO
    # ─────────────────────────────────────────────
    st.markdown("## 📊 Perfil Longitudinal de la Cámara de Mezclado")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_facecolor("#161b22")
    fig.patch.set_facecolor("#0d1117")

    # Dibujar contorno general
    ax.add_patch(Rectangle((0, 0), largo, alto,
        edgecolor="#f0a500", facecolor="none", linewidth=2))

    # Piso con pendiente
    ax.plot(
        [0, largo],
        [0, -piso_drop],
        color="#3fb950",
        linewidth=2,
        label="Piso con pendiente"
    )

    # Shotcrete
    ax.add_patch(Rectangle(
        (0, alto),
        largo,
        esp_shot,
        edgecolor="#388bfd",
        facecolor="none",
        linestyle="--",
        linewidth=1.8
    ))

    # Detalle ampliado
    axins = inset_axes(ax, width="30%", height="50%", loc="upper right")

    axins.plot([0, 5], [0, -5*(abs(pendiente)/100)], color="#3fb950")
    axins.set_title("Detalle 1:20", color="#c9d1d9", fontsize=9)
    axins.set_facecolor("#202833")
    axins.tick_params(colors="#7d8590")

    ax.set_title("Perfil Longitudinal de la Cámara", color="#f0a500")
    ax.set_xlabel("Longitud (m)", color="#c9d1d9")
    ax.set_ylabel("Altura (m)", color="#c9d1d9")
    ax.grid(color="#30363d")

    st.pyplot(fig)

# ╔══════════════════════════════════════════════╗
#  TAB 4 — CÁLCULOS GEOMECÁNICOS (CORREGIDOS COMPLETOS)
# ╚══════════════════════════════════════════════╝

with tabs[3]:

    st.markdown("## 📊 Cálculos Geomecánicos — Método Mitchell + Dujisin")

    st.markdown("""
    Esta sección calcula las presiones inducidas sobre el caserón por el relleno CRF,
    aplicando las formulaciones de **Mitchell (1970)** y **Dujisin (1992)**.  
    Los datos se ingresan manualmente y se realizan conversiones, factores de seguridad
    y gráficos automáticos.
    """)

    # ─────────────────────────────────────────────
    # 1. INGRESO DE PARÁMETROS GEOMECÁNICOS
    # ─────────────────────────────────────────────

    st.markdown("### 📥 Parámetros de Entrada")

    col1, col2, col3 = st.columns(3)

    with col1:
        H = st.number_input("Altura del caserón H (m)", value=25.0)
        B = st.number_input("Ancho del caserón B (m)", value=6.0)
        L = st.number_input("Longitud del caserón L (m)", value=20.0)

    with col2:
        dens_rell = st.number_input("Densidad del CRF (kg/m³)", value=2200.0)
        cohes = st.number_input("Cohesión del CRF (kPa)", value=150.0)
        phi = st.number_input("Ángulo de fricción interna φ (°)", value=35.0)

    with col3:
        dens_roca = st.number_input("Densidad roca encajonante (kg/m³)", value=2700.0)
        fs = st.selectbox("Factor de Seguridad (según Dujisin)", [1.1, 1.2, 1.3, 1.4, 1.5])
        poisson = st.number_input("Coeficiente de Poisson ν", value=0.28)

    # ─────────────────────────────────────────────
    # 2. CONVERSIONES DE DENSIDAD A MN/m³
    # ─────────────────────────────────────────────
    # kg/m³ → kN/m³ → MN/m³
    gamma_rell = dens_rell * 9.81 / 1000 / 1000  # MN/m³
    gamma_roca = dens_roca * 9.81 / 1000 / 1000  # MN/m³

    st.markdown("### 🔁 Conversión de Densidades")

    df_conv = pd.DataFrame({
        "Material": ["Relleno CRF", "Roca encajonante"],
        "Densidad (kg/m³)": [dens_rell, dens_roca],
        "γ (MN/m³)": [gamma_rell, gamma_roca]
    })
    st.markdown(render_table(df_conv), unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # 3. CÁLCULOS – MITCHELL (1970)
    # ─────────────────────────────────────────────
    st.markdown("## 🧮 Cálculos según Mitchell (1970)")

    # Sobrecarga vertical
    sigma_v = gamma_rell * H

    # Coeficiente activo K (Rankine)
    phi_rad = math.radians(phi)
    K = (1 - math.sin(phi_rad)) / (1 + math.sin(phi_rad))

    # Presión lateral
    sigma_h = K * sigma_v

    df_mit = pd.DataFrame({
        "Concepto": ["Sobrecarga vertical σv (MN/m²)", "Coef. activo K", "Presión lateral σh (MN/m²)"],
        "Valor": [f"{sigma_v:.4f}", f"{K:.4f}", f"{sigma_h:.4f}"],
    })
    st.markdown(render_table(df_mit), unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # 4. CÁLCULOS – DUJISIN (1992)
    # ─────────────────────────────────────────────
    st.markdown("## 🧮 Cálculos según Dujisin (1992)")

    # Ecuaciones de Dujisin:
    # σ_techo = (γ * H / FS)
    # σ_lateral = (K * γ * H) / FS

    sigma_techo = sigma_v / fs
    sigma_lateral = sigma_h / fs

    df_duj = pd.DataFrame({
        "Concepto": [
            "Presión vertical reducida σ_techo (MN/m²)",
            "Presión lateral reducida σ_lateral (MN/m²)",
            "Factor de Seguridad aplicado"
        ],
        "Valor": [
            f"{sigma_techo:.4f}",
            f"{sigma_lateral:.4f}",
            f"{fs}"
        ]
    })
    st.markdown(render_table(df_duj), unsafe_allow_html=True)

    # Presión total combinada
    sigma_total = sigma_techo + sigma_lateral

    st.info(f"📌 **Presión total actuante sobre el caserón:** {sigma_total:.4f} MN/m²")

    # ─────────────────────────────────────────────
    # 5. GRÁFICO — DISTRIBUCIÓN DE PRESIÓN LATERAL
    # ─────────────────────────────────────────────

    st.markdown("### 📈 Distribución de Presión Lateral (Mitchell y Dujisin)")

    z = np.linspace(0, H, 50)
    p_mitchell = K * gamma_rell * z
    p_dujisin = p_mitchell / fs

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=p_mitchell, y=z,
        name="Mitchell",
        mode="lines",
        line=dict(color="#f0a500", width=3)
    ))
    fig1.add_trace(go.Scatter(
        x=p_dujisin, y=z,
        name="Dujisin (reducido)",
        mode="lines",
        line=dict(color="#3fb950", width=3, dash="dash")
    ))

    fig1.update_layout(
        **PLOTLY_LAYOUT,
        title="Distribución de Presión Lateral (MN/m²)",
        xaxis_title="Presión (MN/m²)",
        yaxis_title="Altura (m)",
        height=420
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ─────────────────────────────────────────────
    # 6. GRÁFICO — SOPORTE REQUERIDO EN TECHO
    # ─────────────────────────────────────────────

    st.markdown("### 📉 Soporte Requerido en el Techo del Caserón")

    fig2 = go.Figure(go.Bar(
        x=["σ techo reducida"],
        y=[sigma_techo],
        text=[f"{sigma_techo:.4f} MN/m²"],
        textposition="outside",
        marker_color="#388bfd"
    ))

    fig2.update_layout(
        **PLOTLY_LAYOUT,
        title="Presión Vertical que Debe Soportar el Techo",
        height=380,
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)


# ╔══════════════════════════════════════════════╗
#  FOOTER PROFESIONAL — CRF CERRO LINDO
# ╚══════════════════════════════════════════════╝

import datetime
hoy = datetime.datetime.now().strftime("%d/%m/%Y")

st.markdown("""
<style>
.footer-box {
    margin-top: 40px;
    padding: 18px;
    width: 100%;
    text-align: center;
    background: rgba(240, 165, 0, 0.10);
    border-top: 2px solid #f0a500;
    border-radius: 6px;
    font-size: 0.9rem;
    color: #e6edf3;
}
.footer-title {
    font-family: 'Oswald', sans-serif;
    font-size: 1.1rem;
    color: #f0a500;
}
.footer-sub {
    color: #c9d1d9;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="footer-box">
    <div class="footer-title">Cemented Rock Fill · Sistema CRF</div>
    <div class="footer-sub">Aplicación generada para análisis técnico-geomecánico y diseño de relleno detrítico cementado.</div>
    <br>
    <div class="footer-sub">Versión 1.0 · Actualizado el {hoy}</div>
    <div class="footer-sub">Desarrollado por: <b>Bradoc Chambilla</b></div>
</div>
""", unsafe_allow_html=True)
