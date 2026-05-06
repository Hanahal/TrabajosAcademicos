import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import math
 
# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CRF — Unidad Minera Cerro Lindo",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;600;700&family=Source+Sans+3:wght@300;400;600&display=swap');
 
html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
}
 
/* Dark background */
.stApp {
    background: #0d1117;
    color: #e6edf3;
}
 
/* Sidebar */
section[data-testid="stSidebar"] {
    background: #161b22;
    border-right: 1px solid #30363d;
}
 
/* Titles */
h1, h2, h3 {
    font-family: 'Oswald', sans-serif;
    letter-spacing: 0.04em;
}
 
/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #1a2332 0%, #0d1117 50%, #1a1f26 100%);
    border: 1px solid #f0a500;
    border-left: 6px solid #f0a500;
    border-radius: 4px;
    padding: 24px 32px;
    margin-bottom: 28px;
}
.hero-banner h1 {
    color: #f0a500;
    font-size: 2rem;
    margin: 0 0 4px 0;
    text-transform: uppercase;
}
.hero-banner p {
    color: #8b949e;
    margin: 0;
    font-size: 0.95rem;
}
 
/* KPI cards */
.kpi-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-top: 3px solid #f0a500;
    border-radius: 6px;
    padding: 18px 20px;
    text-align: center;
}
.kpi-value {
    font-family: 'Oswald', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #f0a500;
}
.kpi-unit {
    font-size: 0.85rem;
    color: #8b949e;
}
.kpi-label {
    font-size: 0.8rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 4px;
}
 
/* Status badges */
.badge-ok   { background:#1a3a2a; color:#3fb950; border:1px solid #3fb950; border-radius:4px; padding:2px 10px; font-size:0.78rem; font-weight:600; }
.badge-warn { background:#3a2a1a; color:#f0a500; border:1px solid #f0a500; border-radius:4px; padding:2px 10px; font-size:0.78rem; font-weight:600; }
.badge-fail { background:#3a1a1a; color:#f85149; border:1px solid #f85149; border-radius:4px; padding:2px 10px; font-size:0.78rem; font-weight:600; }
 
/* Section header */
.section-header {
    font-family: 'Oswald', sans-serif;
    font-size: 1.1rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #f0a500;
    border-bottom: 1px solid #30363d;
    padding-bottom: 6px;
    margin: 24px 0 14px 0;
}
 
/* Table */
.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
}
.styled-table th {
    background: #1f2937;
    color: #f0a500;
    font-family: 'Oswald', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 8px 12px;
    text-align: left;
}
.styled-table td {
    padding: 7px 12px;
    border-bottom: 1px solid #1f2937;
    color: #c9d1d9;
}
.styled-table tr:hover td { background: #1a2030; }
 
/* Info box */
.info-box {
    background: #1a2332;
    border-left: 4px solid #388bfd;
    border-radius: 4px;
    padding: 12px 16px;
    margin: 10px 0;
    font-size: 0.9rem;
    color: #c9d1d9;
}
 
/* Formula display */
.formula-box {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 16px 20px;
    font-family: 'Courier New', monospace;
    font-size: 1rem;
    color: #79c0ff;
    text-align: center;
    margin: 12px 0;
}
 
/* Streamlit elements overrides */
.stSlider > div { color: #c9d1d9; }
[data-testid="stMetricValue"] { color: #f0a500; font-family: 'Oswald', sans-serif; }
</style>
""", unsafe_allow_html=True)
 
# ─────────────────────────────────────────────
#  PLOTLY THEME
# ─────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#161b22",
    font=dict(family="Source Sans 3", color="#c9d1d9"),
    xaxis=dict(gridcolor="#21262d", linecolor="#30363d", zerolinecolor="#30363d"),
    yaxis=dict(gridcolor="#21262d", linecolor="#30363d", zerolinecolor="#30363d"),
    margin=dict(l=50, r=30, t=50, b=50),
)
COLORS = ["#f0a500", "#3fb950", "#388bfd", "#f85149"]
 
# ═══════════════════════════════════════════════
#  SIDEBAR — PARÁMETROS DE DISEÑO
# ═══════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Parámetros de Diseño")
    st.markdown("---")
 
    st.markdown("### 🪨 Propiedades del Agregado")
    peso_unit_suelto   = st.number_input("Peso unitario suelto (kg/m³)", value=1787)
    peso_unit_compact  = st.number_input("Peso unitario compactado (kg/m³)", value=1914)
    peso_esp_masa      = st.number_input("Peso específico masa (kg/m³)", value=3012)
    contenido_humedad  = st.number_input("Humedad natural (%)", value=3.1)
    contenido_absorc   = st.number_input("Absorción (%)", value=0.6)
 
    st.markdown("### 🏗️ Geometría del Tajeo")
    H = st.slider("Altura del tajeo H (m)", 10, 80, 30)
    L = st.slider("Longitud del tajeo L (m)", 5, 50, 15)
    P = st.slider("Profundidad P (m)", 50, 300, 120)
    a_ancho = st.slider("Ancho de tajeo a (m)", 5, 30, 15)
 
    st.markdown("### 🔧 Parámetros Geomecánicos")
    N_fs   = st.number_input("Factor de seguridad N", value=1.5)
    alpha  = st.slider("Ángulo de fricción α (°)", 20, 45, 28)
    Hc_val = st.slider("Altura crítica Hc (m)", 30, 120, 60)
    Hi_val = st.slider("Altura inferior Hi (m)", 10, 60, 33)
    m_val  = st.number_input("Factor m", value=1)
 
    st.markdown("### 💧 Diseño de Mezcla")
    cemento_kg = st.number_input("Cemento (kg/m³)", value=90)
    agua_L     = st.number_input("Agua (L/m³)", value=72)
 
# ═══════════════════════════════════════════════
#  HERO
# ═══════════════════════════════════════════════
st.markdown("""
<div class="hero-banner">
  <h1>⛏️ Cemented Rock Fill (CRF) — Cerro Lindo</h1>
  <p>Análisis técnico-económico de factibilidad del relleno detrítico cementado · Método Sub Level Stoping</p>
</div>
""", unsafe_allow_html=True)
 
# ═══════════════════════════════════════════════
#  TABS PRINCIPALES
# ═══════════════════════════════════════════════
tabs = st.tabs([
    "📋 Resumen General",
    "🧪 Diseños de Mezcla",
    "📐 Diseño de Mezcla Seleccionado",
    "🏗️ Infraestructura",
    "📊 Cálculos Geomecánicos",
])
 
# ╔══════════════════════════════════════════════╗
#  TAB 1 — RESUMEN GENERAL
# ╚══════════════════════════════════════════════╝
with tabs[0]:
    st.markdown('<div class="section-header">Contexto del Proyecto</div>', unsafe_allow_html=True)
 
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""
        <div class="info-box">
        <b>Unidad Minera:</b> Cerro Lindo<br>
        <b>Método de Explotación:</b> Sub Level Stoping<br>
        <b>Relleno Actual:</b> Relleno en Pasta (3.5% cemento + relave)<br>
        <b>Resistencia Requerida:</b> 0.8 MPa<br>
        <b>Alternativa Propuesta:</b> Cemented Rock Fill (CRF)
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="info-box">
        <b>Problemas del sistema actual:</b><br>
        • Dilución con mineral al avanzar tajos aledaños<br>
        • Alta infraestructura de costo (tuberías superficie→mina)<br>
        • Personal, servicios y monitoreo constante<br><br>
        <b>Ventajas del CRF:</b><br>
        • Elimina la dilución<br>
        • Reduce costos operativos<br>
        • Usa desmonte minero disponible in-situ
        </div>
        """, unsafe_allow_html=True)
 
    st.markdown('<div class="section-header">Indicadores Clave</div>', unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown('<div class="kpi-card"><div class="kpi-value">0.8</div><div class="kpi-unit">MPa</div><div class="kpi-label">Resistencia Mínima</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="kpi-card"><div class="kpi-value">3.0%</div><div class="kpi-unit">cemento</div><div class="kpi-label">CRF diseño</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown('<div class="kpi-card"><div class="kpi-value">3.5%</div><div class="kpi-unit">cemento</div><div class="kpi-label">Pasta actual</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown('<div class="kpi-card"><div class="kpi-value">500</div><div class="kpi-unit">m³/día</div><div class="kpi-label">Producción relleno</div></div>', unsafe_allow_html=True)
    with k5:
        st.markdown('<div class="kpi-card"><div class="kpi-value">2,990</div><div class="kpi-unit">kg/m³</div><div class="kpi-label">Densidad CRF</div></div>', unsafe_allow_html=True)
 
    # Gráfico comparativo pasta vs CRF
    st.markdown('<div class="section-header">Comparativa: Relleno en Pasta vs CRF</div>', unsafe_allow_html=True)
    categorias = ["Cemento (%)", "Resistencia Mín. (×0.1 MPa)", "Dilución", "Costo Infra. (rel.)"]
    pasta_vals = [3.5, 8.0, 3.0, 9.0]
    crf_vals   = [3.0, 8.0, 1.0, 4.0]
 
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(name="Relleno en Pasta", x=categorias, y=pasta_vals,
                              marker_color="#388bfd", opacity=0.85))
    fig_comp.add_trace(go.Bar(name="CRF", x=categorias, y=crf_vals,
                              marker_color="#f0a500", opacity=0.85))
    fig_comp.update_layout(
        **PLOTLY_LAYOUT,
        title="Comparativa cualitativa: Pasta vs CRF",
        barmode="group",
        legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
        height=360,
    )
    st.plotly_chart(fig_comp, use_container_width=True)
 
# ╔══════════════════════════════════════════════╗
#  TAB 2 — DISEÑOS DE MEZCLA (PRUEBA PILOTO)
# ╚══════════════════════════════════════════════╝
with tabs[1]:
    st.markdown('<div class="section-header">Prueba Piloto — 4 Diseños de Mezcla CRF</div>', unsafe_allow_html=True)
 
    # Datos de diseño
    designs = {
        "Diseño": ["D01", "D02", "D03", "D04"],
        "Cemento (%)": [2.54, 3.08, 3.55, 4.85],
        "Cemento (kg/m³)": [75, 90, 103, 138],
        "Agua (%)": [2.04, 2.46, 2.83, 3.87],
        "Agua (L/m³)": [60, 72, 82, 110],
        "Desmonte (%)": [95.42, 94.46, 93.63, 91.28],
        "Desmonte (kg/m³)": [2812, 2760, 2717, 2595],
        "Densidad (kg/m³)": [2947, 2922, 2902, 2843],
        "A/C": [0.80, 0.80, 0.80, 0.80],
    }
    df_designs = pd.DataFrame(designs)
 
    # Tabla HTML bonita
    def render_table(df):
        rows = ""
        for _, row in df.iterrows():
            cols = "".join(f"<td>{v}</td>" for v in row)
            rows += f"<tr>{cols}</tr>"
        headers = "".join(f"<th>{c}</th>" for c in df.columns)
        return f'<table class="styled-table"><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>'
 
    st.markdown(render_table(df_designs), unsafe_allow_html=True)
 
    # Resistencias
    dias = [7, 14, 21, 28, 56]
    resist = {
        "D01": [0.65, 1.01, 1.39, 1.66, 1.68],
        "D02": [1.07, 1.37, 1.63, 2.08, 2.11],
        "D03": [1.68, 2.73, 3.38, 4.82, 4.95],
        "D04": [2.58, 3.14, 4.41, 5.21, 6.53],
    }
    df_resist = pd.DataFrame(resist, index=dias)
    df_resist.index.name = "Días"
 
    st.markdown('<div class="section-header">Desarrollo de Resistencia a Compresión (MPa)</div>', unsafe_allow_html=True)
 
    col_t, col_g = st.columns([1, 2])
    with col_t:
        st.markdown(render_table(df_resist.reset_index()), unsafe_allow_html=True)
 
    with col_g:
        fig_r = go.Figure()
        for i, (d, vals) in enumerate(resist.items()):
            fig_r.add_trace(go.Scatter(
                x=dias, y=vals, mode="lines+markers", name=d,
                line=dict(color=COLORS[i], width=2.5),
                marker=dict(size=8, color=COLORS[i]),
            ))
        fig_r.add_hline(
            y=0.8, line_dash="dash", line_color="#f85149", line_width=2,
            annotation_text="  Resistencia mínima (0.8 MPa)",
            annotation_font_color="#f85149",
        )
        fig_r.update_layout(
            **PLOTLY_LAYOUT,
            title="Curvas de Resistencia vs Tiempo",
            xaxis_title="Tiempo (días)",
            yaxis_title="Resistencia (MPa)",
            legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
            height=380,
        )
        st.plotly_chart(fig_r, use_container_width=True)
 
    # Gráfico de barras comparativo a 28 días
    st.markdown('<div class="section-header">Resistencia a 28 días por Diseño</div>', unsafe_allow_html=True)
    fig_28 = go.Figure()
    resist_28 = [1.66, 2.08, 4.82, 5.21]
    fig_28.add_trace(go.Bar(
        x=["D01 (2.54% cem)", "D02 (3.08% cem)", "D03 (3.55% cem)", "D04 (4.85% cem)"],
        y=resist_28,
        marker_color=COLORS,
        text=[f"{v} MPa" for v in resist_28],
        textposition="outside",
        textfont=dict(color="#e6edf3"),
    ))
    fig_28.add_hline(y=0.8, line_dash="dot", line_color="#f85149", line_width=2,
                     annotation_text="  Mínimo requerido 0.8 MPa", annotation_font_color="#f85149")
    fig_28.update_layout(
        **PLOTLY_LAYOUT,
        title="Resistencia a 28 días — Comparativa de Diseños",
        yaxis_title="Resistencia (MPa)",
        height=360,
        showlegend=False,
    )
    st.plotly_chart(fig_28, use_container_width=True)
 
    # Conclusión
    ok_28 = [v >= 0.8 for v in resist_28]
    st.markdown("**Estado de diseños respecto al requisito mínimo (0.8 MPa a 28 días):**")
    cols_badge = st.columns(4)
    for i, (label, ok) in enumerate(zip(["D01","D02","D03","D04"], ok_28)):
        badge = "badge-ok" if ok else "badge-fail"
        txt   = "✔ CUMPLE" if ok else "✖ NO CUMPLE"
        cols_badge[i].markdown(f'<span class="{badge}">{label}: {txt}</span>', unsafe_allow_html=True)
 
# ╔══════════════════════════════════════════════╗
#  TAB 3 — DISEÑO DE MEZCLA SELECCIONADO (D02)
# ╚══════════════════════════════════════════════╝
with tabs[2]:
    st.markdown('<div class="section-header">Diseño 02 Seleccionado — ACI 211 (Cemento Portland Tipo I)</div>', unsafe_allow_html=True)
 
    # Especificaciones
    col_spec, col_agr = st.columns(2)
    with col_spec:
        st.markdown("**Especificaciones de Diseño**")
        spec_data = {
            "Parámetro": ["F'c Especificado", "F'cr Requerido", "Relación A/C", "Slump", "Agua Industrial", "Aire atrapado"],
            "Valor": ["20 kg/cm²", "30 kg/cm²", "0.8", "0 pulg.", "72 L/m³", "1%"],
        }
        st.markdown(render_table(pd.DataFrame(spec_data)), unsafe_allow_html=True)
 
    with col_agr:
        st.markdown("**Características del Agregado (Desmonte interior mina 3\")**")
        agr_data = {
            "Característica": [
                "Tamaño máximo", "Tamaño máx. nominal", "Módulo de fineza",
                f"Peso unit. suelto", f"Peso unit. compactado",
                "Peso específico", "Humedad natural", "Absorción"
            ],
            "Valor": [
                '3"', '2"', f"{8.4}",
                f"{peso_unit_suelto} kg/m³", f"{peso_unit_compact} kg/m³",
                f"{peso_esp_masa} kg/m³", f"{contenido_humedad}%", f"{contenido_absorc}%"
            ],
        }
        st.markdown(render_table(pd.DataFrame(agr_data)), unsafe_allow_html=True)
 
    st.markdown('<div class="section-header">Cálculo del Diseño de Mezcla (Volúmenes Absolutos)</div>', unsafe_allow_html=True)
 
    # Cálculos
    cemento_pct = cemento_kg / (cemento_kg + agua_L + 2678) * 100
    agua_pct    = agua_L / (cemento_kg + agua_L + 2678) * 100
    desmonte_kg = 2678
    densidad_base = cemento_kg + agua_L + desmonte_kg
 
    # Volúmenes absolutos
    v_cemento  = cemento_kg / 3110
    v_agua     = agua_L / 1000
    v_agregado = desmonte_kg / peso_esp_masa
    v_aire     = 0.010
    suma_vol   = v_cemento + v_agua + v_agregado + v_aire
 
    # Corrección por humedad
    agregado_corregido = desmonte_kg * (1 + contenido_humedad / 100)
    aporte_agua        = desmonte_kg * ((contenido_humedad - contenido_absorc) / 100)
    agua_efectiva      = agua_L - aporte_agua
 
    # Diseño húmedo
    tanda   = 13.761
    cem_tanda   = cemento_kg * tanda
    agua_tanda  = agua_efectiva * tanda
    agr_tanda   = agregado_corregido * tanda
    densidad_final = cemento_kg + agua_efectiva + agregado_corregido
 
    col_vol, col_hum = st.columns(2)
    with col_vol:
        st.markdown("**Volúmenes Absolutos**")
        vol_data = {
            "Componente": ["Cemento", "Agua", "Agregado", "Aire", "TOTAL"],
            "kg o L/m³": [cemento_kg, agua_L, desmonte_kg, "—", "—"],
            "Volumen (m³/m³)": [
                f"{v_cemento:.3f}", f"{v_agua:.3f}", f"{v_agregado:.3f}",
                f"{v_aire:.3f}", f"{suma_vol:.3f}"
            ],
        }
        st.markdown(render_table(pd.DataFrame(vol_data)), unsafe_allow_html=True)
 
    with col_hum:
        st.markdown("**Corrección por Humedad Natural**")
        hum_data = {
            "Componente": ["Cemento", "Agua efectiva", "Agregado corregido", "Densidad húmeda"],
            "kg o L/m³": [
                f"{cemento_kg:.1f}",
                f"{agua_efectiva:.1f}",
                f"{agregado_corregido:.1f}",
                f"{densidad_final:.1f}",
            ],
            "Proporción (%)": [
                f"{cemento_kg/densidad_final*100:.2f}%",
                f"{agua_efectiva/densidad_final*100:.2f}%",
                f"{agregado_corregido/densidad_final*100:.2f}%",
                "100%",
            ],
        }
        st.markdown(render_table(pd.DataFrame(hum_data)), unsafe_allow_html=True)
 
    st.markdown(f"""
    <div class="formula-box">
    Tanda = {tanda:.3f} &nbsp;|&nbsp;
    Cemento = {cem_tanda:.0f} kg &nbsp;|&nbsp;
    Agua = {agua_tanda:.0f} L &nbsp;|&nbsp;
    Agregado = {agr_tanda:.0f} kg &nbsp;|&nbsp;
    TOTAL = {cem_tanda+agua_tanda+agr_tanda:.0f} kg
    </div>
    """, unsafe_allow_html=True)
 
    # Gráfico de composición
    st.markdown('<div class="section-header">Composición del CRF — Diseño 02</div>', unsafe_allow_html=True)
    col_pie, col_bar = st.columns(2)
    with col_pie:
        fig_pie = go.Figure(go.Pie(
            labels=["Desmonte", "Agua", "Cemento"],
            values=[agregado_corregido, agua_efectiva, cemento_kg],
            marker=dict(colors=["#f0a500", "#388bfd", "#3fb950"],
                        line=dict(color="#0d1117", width=2)),
            textfont=dict(size=13),
            hole=0.35,
        ))
        fig_pie.update_layout(**PLOTLY_LAYOUT, title="Composición en masa (%)", height=340)
        st.plotly_chart(fig_pie, use_container_width=True)
 
    with col_bar:
        fig_bar = go.Figure(go.Bar(
            x=["Cemento", "Agua", "Desmonte"],
            y=[cemento_kg, agua_efectiva, agregado_corregido],
            marker_color=["#3fb950", "#388bfd", "#f0a500"],
            text=[f"{v:.1f} kg/m³" for v in [cemento_kg, agua_efectiva, agregado_corregido]],
            textposition="outside",
            textfont=dict(color="#e6edf3"),
        ))
        fig_bar.update_layout(
            **PLOTLY_LAYOUT, title="Cantidades por m³ (kg o L)", yaxis_title="kg o L/m³", height=340, showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
 
    st.markdown("""
    <div class="info-box">
    📌 <b>Normas aplicables:</b>
    Agregados → NTP 400.012 &nbsp;|&nbsp; Cemento → NTP 334.090 &nbsp;|&nbsp;
    Agua → DS N°0.31-2010-SA &nbsp;|&nbsp; Aditivos → NTP 209.038 &nbsp;|&nbsp;
    Proporciones → ACI 211
    </div>
    """, unsafe_allow_html=True)
 
# ╔══════════════════════════════════════════════╗
#  TAB 4 — INFRAESTRUCTURA
# ╚══════════════════════════════════════════════╝
with tabs[3]:
    st.markdown('<div class="section-header">Infraestructura y Recursos para el Relleno CRF</div>', unsafe_allow_html=True)
 
    col_infra, col_equip = st.columns(2)
    with col_infra:
        st.markdown("**Infraestructura Interior Mina**")
        infra_items = [
            "Cámaras de acumulación de desmonte",
            "Cámara de mezclado (gradiente -1% a -2%)",
            "Labor de disposición al tajeo",
            "Labor de instalación de planta móvil",
        ]
        for item in infra_items:
            st.markdown(f"• {item}")
 
        st.markdown("---")
        st.markdown("**Cámara de Planta**")
        st.markdown("Dimensiones: **5m × 4.5m × 20m**")
        st.markdown("Componentes: Bomba Putzmeister, Planta mezcladora, Silo horizontal, Bombona de bajo perfil")
 
        st.markdown("---")
        st.markdown("**Cámara de Acarreo al Tajeo**")
        st.markdown("Bajo telemando · Refugio requerido · Berma de seguridad")
 
    with col_equip:
        st.markdown("**Equipos Principales**")
        equip_data = {
            "Cant.": [1, 1, 1, 1, 1, 1],
            "Descripción": [
                "Bombona de bajo perfil 11 ton",
                "Mezclador para lechada de cemento",
                "Silo horizontal 20 ton",
                "Bomba Concreto",
                "Cabina automatizada",
                "Scoop 6 Yd³ (250 m³/día)",
            ],
        }
        st.markdown(render_table(pd.DataFrame(equip_data)), unsafe_allow_html=True)
 
        st.markdown("---")
        st.markdown("**Personal Directo (por turno)**")
        pers_data = {
            "Cant.": [3, 3, 3, 3, 3],
            "Rol": [
                "Jefes de turno",
                "Operadores de bajo perfil",
                "Operadores de scoop",
                "Operadores de planta",
                "Operadores de bomba",
            ],
        }
        st.markdown(render_table(pd.DataFrame(pers_data)), unsafe_allow_html=True)
        st.markdown("**Total: 15 personas por turno**")
 
    st.markdown('<div class="section-header">Secuencia Operativa de Preparación y Acarreo CRF</div>', unsafe_allow_html=True)
    steps = [
        ("1", "Control disposición desmonte", "Control de disposición de material detrítico en cámara de acumulación."),
        ("2", "Acarreo y conformación", "Scooptram 6 Yd³ acarrea el desmonte desde cámara de acumulación hacia cámara de mezcla."),
        ("3", "Aspersión lechada cemento", "Tuberías de 4\" (flujo ACI). Salidas de 2\" en 4 puntos a lo largo de 8 m de cámara."),
        ("4", "Mezclado bajo perfil", "Scooptram 6 Yd³ en 2 ciclos de mezcla dentro de la cámara."),
        ("5", "Acarreo al tajeo", "Scooptram 6 Yd³ transporta la mezcla al tajeo bajo telemando."),
        ("6", "Conformación final", "Acumulación hasta talud natural; ingreso al tajeo para conformar y rellenar."),
    ]
 
    cols_steps = st.columns(3)
    for i, (num, title, desc) in enumerate(steps):
        with cols_steps[i % 3]:
            st.markdown(f"""
            <div style="background:#161b22;border:1px solid #30363d;border-top:3px solid #f0a500;
                        border-radius:6px;padding:14px;margin-bottom:12px;min-height:110px;">
              <span style="font-family:Oswald;font-size:1.4rem;color:#f0a500;">{num}.</span>
              <span style="font-family:Oswald;font-size:0.95rem;color:#e6edf3;margin-left:6px;">{title}</span>
              <p style="font-size:0.82rem;color:#8b949e;margin-top:8px;margin-bottom:0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
 
# ╔══════════════════════════════════════════════╗
#  TAB 5 — CÁLCULOS GEOMECÁNICOS
# ╚══════════════════════════════════════════════╝
with tabs[4]:
    st.markdown('<div class="section-header">Cálculos de Resistencia Requerida del Relleno</div>', unsafe_allow_html=True)
 
    D_MN = 0.030  # MN/m³ (densidad fija diseño)
 
    # ── 1. PARED AUTOESTABLE (Mitchell 1982) ──────────────────────────
    pared_auto = (N_fs * D_MN * H) / (1 + H / L)
 
    st.markdown("#### 1. Pared Autoestable — Mitchell et al. (1982)")
    st.markdown('<div class="formula-box">PARED AUTOESTABLE = (N × D × H) / (1 + H/L)</div>', unsafe_allow_html=True)
 
    col_pa1, col_pa2 = st.columns([1, 2])
    with col_pa1:
        pa_data = {
            "Parámetro": ["N (FS)", "D (MN/m³)", "H (m)", "L (m)", "Resultado"],
            "Valor": [N_fs, D_MN, H, L, f"{pared_auto:.4f} MPa"],
        }
        st.markdown(render_table(pd.DataFrame(pa_data)), unsafe_allow_html=True)
        badge = "badge-ok" if pared_auto >= 0.8 else "badge-warn"
        txt   = "✔ Supera requisito 0.8 MPa" if pared_auto >= 0.8 else "⚠ Por debajo de 0.8 MPa"
        st.markdown(f'<br><span class="{badge}">{txt}</span>', unsafe_allow_html=True)
 
    with col_pa2:
        H_range = np.linspace(5, 80, 200)
        pa_range = (N_fs * D_MN * H_range) / (1 + H_range / L)
        fig_pa = go.Figure()
        fig_pa.add_trace(go.Scatter(x=H_range, y=pa_range, mode="lines",
                                    line=dict(color="#f0a500", width=2.5), name="Pared Autoestable"))
        fig_pa.add_vline(x=H, line_dash="dash", line_color="#388bfd",
                         annotation_text=f"  H = {H} m", annotation_font_color="#388bfd")
        fig_pa.add_hline(y=0.8, line_dash="dot", line_color="#f85149",
                         annotation_text="  0.8 MPa min", annotation_font_color="#f85149")
        fig_pa.add_scatter(x=[H], y=[pared_auto], mode="markers",
                           marker=dict(color="#3fb950", size=12, symbol="star"),
                           name=f"H actual = {pared_auto:.3f} MPa")
        fig_pa.update_layout(**PLOTLY_LAYOUT,
                              title="Pared Autoestable vs Altura de Tajeo",
                              xaxis_title="Altura H (m)", yaxis_title="MPa", height=340)
        st.plotly_chart(fig_pa, use_container_width=True)
 
    st.markdown("---")
 
    # ── 2. FACTOR DE SEGURIDAD CONTRA VOLCAMIENTO (Dujisin 1974) ──────
    st.markdown("#### 2. Factor de Seguridad contra Volcamiento — Dujisin & Rutllant (1974)")
 
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        fs_data = {
            "Tipo de Relleno": ["Relleno Cohesivo (CRF)", "Relleno Granular"],
            "FS Estático": [2.0, 1.5],
            "FS Dinámico": [1.5, 1.2],
        }
        st.markdown(render_table(pd.DataFrame(fs_data)), unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box" style="margin-top:10px;">
        El CRF se clasifica como <b>relleno cohesivo</b> gracias al contenido de cemento,
        por lo que aplica FS Estático ≥ 2.0 y FS Dinámico ≥ 1.5.
        </div>
        """, unsafe_allow_html=True)
    with col_v2:
        categorias_fs = ["Cohesivo Estático", "Cohesivo Dinámico", "Granular Estático", "Granular Dinámico"]
        valores_fs    = [2.0, 1.5, 1.5, 1.2]
        fig_fs = go.Figure(go.Bar(
            x=categorias_fs, y=valores_fs,
            marker_color=["#3fb950", "#f0a500", "#388bfd", "#8b949e"],
            text=[f"FS = {v}" for v in valores_fs],
            textposition="outside", textfont=dict(color="#e6edf3"),
        ))
        fig_fs.update_layout(**PLOTLY_LAYOUT, title="Factores de Seguridad requeridos", yaxis_title="FS", height=320, showlegend=False)
        st.plotly_chart(fig_fs, use_container_width=True)
 
    st.markdown("---")
 
    # ── 3. PRESIÓN LATERAL (EMPUJE DE CAJAS) ─────────────────────────
    st.markdown("#### 3. Presión Lateral — Empuje de Cajas")
    st.markdown('<div class="formula-box">P_lateral = (N × D × a × P) / (K × L)</div>', unsafe_allow_html=True)
 
    alpha_rad = math.radians(alpha)
    K         = (1 + math.sin(alpha_rad)) / (1 - math.sin(alpha_rad))
    presion_lat = (N_fs * D_MN * a_ancho * P) / (K * L)
 
    col_pl1, col_pl2 = st.columns([1, 2])
    with col_pl1:
        pl_data = {
            "Parámetro": ["N (FS)", "D (MN/m³)", "H (m)", "L (m)", "P profundidad (m)", "a ancho (m)", "α fricción (°)", "K coeficiente", "Presión Lateral"],
            "Valor": [N_fs, D_MN, H, L, P, a_ancho, alpha, f"{K:.4f}", f"{presion_lat:.6f} MPa"],
        }
        st.markdown(render_table(pd.DataFrame(pl_data)), unsafe_allow_html=True)
 
    with col_pl2:
        P_range  = np.linspace(10, 300, 200)
        pl_range = (N_fs * D_MN * a_ancho * P_range) / (K * L)
        fig_pl   = go.Figure()
        fig_pl.add_trace(go.Scatter(x=P_range, y=pl_range, mode="lines",
                                    line=dict(color="#388bfd", width=2.5), name="Presión Lateral"))
        fig_pl.add_vline(x=P, line_dash="dash", line_color="#f0a500",
                         annotation_text=f"  P = {P} m", annotation_font_color="#f0a500")
        fig_pl.add_scatter(x=[P], y=[presion_lat], mode="markers",
                           marker=dict(color="#3fb950", size=12, symbol="star"),
                           name=f"{presion_lat:.3f} MPa")
        fig_pl.update_layout(**PLOTLY_LAYOUT,
                              title="Presión Lateral vs Profundidad",
                              xaxis_title="Profundidad P (m)", yaxis_title="MPa", height=340)
        st.plotly_chart(fig_pl, use_container_width=True)
 
    st.markdown("---")
 
    # ── 4. SOPORTE DEL TECHO ──────────────────────────────────────────
    st.markdown("#### 4. Soporte del Techo")
    st.markdown('<div class="formula-box">Sc = n × (2·gs/m + gr·(Hc − Hi))</div>', unsafe_allow_html=True)
 
    n_val  = N_fs
    gs_val = D_MN
    gr_val = D_MN
    Sc     = n_val * (2 * gs_val * H / m_val + gr_val * (Hc_val - Hi_val))
 
    col_sc1, col_sc2 = st.columns([1, 2])
    with col_sc1:
        sc_data = {
            "Parámetro": ["n (FS)", "gs (MN/m³)", "m", "h (m)", "Hc (m)", "Hi (m)", "gr (MN/m³)", "Sc (Soporte techo)"],
            "Valor": [n_val, gs_val, m_val, H, Hc_val, Hi_val, gr_val, f"{Sc:.2f} MPa"],
        }
        st.markdown(render_table(pd.DataFrame(sc_data)), unsafe_allow_html=True)
 
    with col_sc2:
        Hc_range = np.linspace(Hi_val + 1, 150, 200)
        Sc_range = n_val * (2 * gs_val * H / m_val + gr_val * (Hc_range - Hi_val))
        fig_sc   = go.Figure()
        fig_sc.add_trace(go.Scatter(x=Hc_range, y=Sc_range, mode="lines",
                                    line=dict(color="#3fb950", width=2.5), name="Soporte del Techo"))
        fig_sc.add_vline(x=Hc_val, line_dash="dash", line_color="#f0a500",
                         annotation_text=f"  Hc = {Hc_val} m", annotation_font_color="#f0a500")
        fig_sc.add_scatter(x=[Hc_val], y=[Sc], mode="markers",
                           marker=dict(color="#f85149", size=12, symbol="star"),
                           name=f"Sc = {Sc:.2f} MPa")
        fig_sc.update_layout(**PLOTLY_LAYOUT,
                              title="Soporte del Techo vs Altura Crítica Hc",
                              xaxis_title="Hc (m)", yaxis_title="MPa", height=340)
        st.plotly_chart(fig_sc, use_container_width=True)
 
    st.markdown("---")
 
    # ── RESUMEN TOTAL ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">Resumen de Presiones Totales Requeridas</div>', unsafe_allow_html=True)
    total_mpa = pared_auto + presion_lat + Sc
 
    col_res, col_graf = st.columns([1, 2])
    with col_res:
        res_data = {
            "Componente": ["Pared Autoestable", "Presión Lateral", "Soporte del Techo", "TOTAL"],
            "MPa": [f"{pared_auto:.4f}", f"{presion_lat:.4f}", f"{Sc:.2f}", f"{total_mpa:.2f}"],
        }
        st.markdown(render_table(pd.DataFrame(res_data)), unsafe_allow_html=True)
 
        st.markdown(f"""
        <br>
        <div class="kpi-card" style="background:#1a3a2a;border-top-color:#3fb950;">
          <div class="kpi-value" style="color:#3fb950;">{total_mpa:.2f}</div>
          <div class="kpi-unit">MPa</div>
          <div class="kpi-label">Resistencia Total Requerida</div>
        </div>
        """, unsafe_allow_html=True)
 
        # ¿Diseño 02 cumple?
        resist_d2_28 = 2.08
        resist_d2_56 = 2.11
        cumple = resist_d2_28 >= 0.8
        st.markdown(f"""
        <br>
        <div class="info-box">
        <b>Diseño 02 a 28 días:</b> {resist_d2_28} MPa → 
        <span class="badge-ok">✔ Cumple pared autoestable ({pared_auto:.3f} MPa)</span><br><br>
        Para la presión lateral y soporte de techo, se requiere análisis adicional de combinación
        de acciones, que puede cubrirse con la dosificación D03 o D04.
        </div>
        """, unsafe_allow_html=True)
 
    with col_graf:
        fig_total = go.Figure()
        labels_total = ["Pared Autoestable", "Presión Lateral", "Soporte del Techo"]
        vals_total   = [pared_auto, presion_lat, Sc]
        fig_total.add_trace(go.Bar(
            x=labels_total, y=vals_total,
            marker_color=["#f0a500", "#388bfd", "#3fb950"],
            text=[f"{v:.3f} MPa" for v in vals_total],
            textposition="outside", textfont=dict(color="#e6edf3"),
        ))
        fig_total.update_layout(
            **PLOTLY_LAYOUT,
            title=f"Componentes de Presión Total = {total_mpa:.2f} MPa",
            yaxis_title="MPa", height=380, showlegend=False,
        )
        st.plotly_chart(fig_total, use_container_width=True)
 
    # Waterfall
    fig_wf = go.Figure(go.Waterfall(
        x=["Pared Autoestable", "Presión Lateral", "Soporte Techo", "TOTAL"],
        y=[pared_auto, presion_lat, Sc, 0],
        measure=["relative", "relative", "relative", "total"],
        marker=dict(color=["#f0a500", "#388bfd", "#3fb950", "#f85149"]),
        connector=dict(line=dict(color="#30363d")),
        text=[f"{v:.3f}" for v in [pared_auto, presion_lat, Sc]] + [f"{total_mpa:.2f}"],
        textposition="outside",
    ))
    fig_wf.update_layout(**PLOTLY_LAYOUT,
                         title="Acumulación de Presiones (Waterfall)",
                         yaxis_title="MPa", height=360)
    st.plotly_chart(fig_wf, use_container_width=True)
 
# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#484f58;font-size:0.78rem;padding:10px 0;">
  Cemented Rock Fill Analysis · Unidad Minera Cerro Lindo · Sub Level Stoping ·
  Mitchell et al. (1982) · Dujisin & Rutllant (1974) · ACI 211
</div>
""", unsafe_allow_html=True)
 