import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import io
import datetime
 
# PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image as RLImage,
)
 
# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CRF Analysis",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="collapsed"
)
 
st.markdown("""
<style>
section[data-testid="stSidebar"] {display: none !important;}
div[data-testid="stSidebarNav"]  {display: none !important;}
 
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&display=swap');
 
html, body, [class*="css"], .stApp {
    font-family: 'Lato', sans-serif !important;
    font-size: 12px !important;
    color: #e6edf3 !important;
}
h1, h2 {
    font-family: 'Lato', sans-serif !important;
    font-weight: 900 !important;
    font-size: 14px !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #f0a500 !important;
}
h3, h4 {
    font-family: 'Lato', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    color: #f0a500 !important;
}
.stApp { background: #0b253a !important; color: #e6edf3 !important; }
.stTabs [data-baseweb="tab"] {
    font-family: 'Lato', sans-serif !important;
    font-size: 12px !important; font-weight: 700 !important; color: #e6edf3 !important;
}
.stTabs [aria-selected="true"] {
    color: #ffffff !important; font-weight: 900 !important;
    border-bottom: 3px solid #f0a500 !important;
}
.hero-banner {
    background: linear-gradient(135deg, #1a2332 0%, #0d1117 50%, #1a1f26 100%);
    border: 1px solid #f0a500; border-left: 4px solid #f0a500;
    border-radius: 4px; padding: 8px 14px; margin-bottom: 10px;
}
.hero-banner h1 { color: #f0a500; font-size: 18px !important; }
.hero-banner p  { color: #8b949e; font-size: 12px !important; }
.styled-table { width: 100%; border-collapse: collapse; font-size: 12px !important; }
.styled-table th {
    background: #1f2937; color: #f0a500; padding: 8px 12px;
    text-transform: uppercase; font-size: 12px !important;
}
.styled-table td {
    padding: 7px 12px; border-bottom: 1px solid #1f2937;
    color: #c9d1d9; font-size: 12px !important;
}
.styled-table tr:hover td { background: #1a2030; }
</style>
""", unsafe_allow_html=True)
 
# ─────────────────────────────────────────────
#  PLOTLY THEME
# ─────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
    font=dict(family="Source Sans 3", color="#c9d1d9"),
    xaxis=dict(gridcolor="#21262d", linecolor="#30363d"),
    yaxis=dict(gridcolor="#21262d", linecolor="#30363d"),
    margin=dict(l=50, r=30, t=50, b=50),
)
COLORS = ["#f0a500", "#3fb950", "#388bfd", "#f85149"]
 
def render_table(df):
    rows = ""
    for _, row in df.iterrows():
        cols = "".join(f"<td>{v}</td>" for v in row)
        rows += f"<tr>{cols}</tr>"
    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    return f'<table class="styled-table"><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>'
 
 
# ─────────────────────────────────────────────
#  DEFAULTS
# ─────────────────────────────────────────────
DEFAULT_ESPEC = {"Fc_kgcm2":20,"Fcr_kgcm2":30,"Slump_pulg":0,"Agua_industrial_Lm3":72,"Aire_atrapado_pct":2}
DEFAULT_AGRE  = {"Tamano_maximo_pulg":3.0,"Tamano_nominal_pulg":2.0,"Modulo_fineza":8.4,
                 "Peso_unitario_suelto_kgm3":1787.0,"Peso_unitario_compactado_kgm3":1914.0,
                 "Peso_especifico_agregado_kgm3":3012.0,"Humedad_natural_pct":3.1,
                 "Absorcion_pct":0.6,"Peso_especifico_cemento_kgm3":3110.0,"Densidad_agua_kgm3":1.0}
DEFAULT_INFRA = {"Bomba_estacionaria_m3h":50.0,"Chancadora_secundaria_th":120.0,
                 "Faja_transportadora_th":300.0,"Tolva_regulacion_m3":25.0,
                 "Personal_operadores":3,"Personal_mecanicos":1,"Personal_supervisores":1,
                 "Largo_camara_m":18.0,"Ancho_util_m":4.0,"Alto_util_m":4.5,
                 "Espesor_concreto_m":0.20,"Espesor_shotcrete_m":0.10,
                 "Espesor_relleno_estructural_m":0.40,"Altura_buzon_m":3.0,"Ancho_bandeja_m":1.2}
DEFAULT_GEO   = {"Altura_caseron_H_m":25.0,"Ancho_caseron_B_m":6.0,"Longitud_caseron_L_m":20.0,
                 "Densidad_CRF_kgm3":2200.0,"Cohesion_CRF_kPa":150.0,"Angulo_friccion_phi_deg":35.0,
                 "Densidad_roca_kgm3":2700.0,"Factor_seguridad":1.2,"Coeficiente_Poisson":0.28}
 
 
# ─────────────────────────────────────────────
#  CSV TEMPLATE
# ─────────────────────────────────────────────
def generate_template_csv() -> bytes:
    out = io.StringIO()
    out.write("# CSV MAESTRO CRF\n#\n")
    out.write("SECCION,DESIGNS\nDiseño,Cemento (kg/m³),Agua (L/m³),Desmonte (kg/m³),Densidad (kg/m³)\n")
    for r in [["D01",75,60,2812,2947],["D02",90,72,2760,2922],["D03",103,82,2717,2902],["D04",138,110,2595,2843]]:
        out.write(",".join(str(v) for v in r)+"\n")
    out.write("#\nSECCION,RESISTENCIAS\nDías,D01,D02,D03,D04\n")
    for r in [[7,0.65,1.07,1.68,2.58],[14,1.01,1.37,2.73,3.14],[21,1.39,1.63,3.38,4.41],[28,1.66,2.08,4.82,5.21],[56,1.68,2.11,4.95,6.53]]:
        out.write(",".join(str(v) for v in r)+"\n")
    out.write("#\nSECCION,ESPECIFICACIONES\nParametro,Valor\n")
    for r in [("Fc_kgcm2",20),("Fcr_kgcm2",30),("Slump_pulg",0),("Agua_industrial_Lm3",72),("Aire_atrapado_pct",2)]:
        out.write(f"{r[0]},{r[1]}\n")
    out.write("#\nSECCION,AGREGADO\nParametro,Valor\n")
    for r in [("Tamano_maximo_pulg",3),("Tamano_nominal_pulg",2),("Modulo_fineza",8.4),
              ("Peso_unitario_suelto_kgm3",1787),("Peso_unitario_compactado_kgm3",1914),
              ("Peso_especifico_agregado_kgm3",3012),("Humedad_natural_pct",3.1),
              ("Absorcion_pct",0.6),("Peso_especifico_cemento_kgm3",3110),("Densidad_agua_kgm3",1.0)]:
        out.write(f"{r[0]},{r[1]}\n")
    out.write("#\nSECCION,INFRAESTRUCTURA\nParametro,Valor\n")
    for r in [("Bomba_estacionaria_m3h",50),("Chancadora_secundaria_th",120),
              ("Faja_transportadora_th",300),("Tolva_regulacion_m3",25),
              ("Personal_operadores",3),("Personal_mecanicos",1),("Personal_supervisores",1),
              ("Largo_camara_m",18.0),("Ancho_util_m",4.0),("Alto_util_m",4.5),
              ("Espesor_concreto_m",0.20),("Espesor_shotcrete_m",0.10),
              ("Espesor_relleno_estructural_m",0.40),("Altura_buzon_m",3.0),("Ancho_bandeja_m",1.2)]:
        out.write(f"{r[0]},{r[1]}\n")
    out.write("#\nSECCION,GEOMECANICA\nParametro,Valor\n")
    for r in [("Altura_caseron_H_m",25.0),("Ancho_caseron_B_m",6.0),("Longitud_caseron_L_m",20.0),
              ("Densidad_CRF_kgm3",2200.0),("Cohesion_CRF_kPa",150.0),("Angulo_friccion_phi_deg",35.0),
              ("Densidad_roca_kgm3",2700.0),("Factor_seguridad",1.2),("Coeficiente_Poisson",0.28)]:
        out.write(f"{r[0]},{r[1]}\n")
    return out.getvalue().encode("utf-8")
 
 
# ─────────────────────────────────────────────
#  CSV PARSER
# ─────────────────────────────────────────────
def parse_master_csv(uploaded_file) -> dict:
    content = uploaded_file.read().decode("utf-8")
    sections, current_section, current_rows, header = {}, None, [], None
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        if line.upper().startswith("SECCION,"):
            if current_section and header and current_rows:
                sections[current_section] = pd.DataFrame(current_rows, columns=header)
            current_section = line.split(",",1)[1].strip().upper()
            current_rows, header = [], None
            continue
        parts = line.split(",")
        if header is None:
            header = parts
        else:
            parsed = []
            for v in parts:
                try: parsed.append(float(v) if "." in v else int(v))
                except ValueError: parsed.append(v.strip())
            current_rows.append(parsed)
    if current_section and header and current_rows:
        sections[current_section] = pd.DataFrame(current_rows, columns=header)
    return sections
 
 
# ─────────────────────────────────────────────
#  PDF BUILDER
# ─────────────────────────────────────────────
_GOLD  = colors.HexColor("#f0a500")
_DARK2 = colors.HexColor("#1f2937")
_ROW1  = colors.HexColor("#161b22")
_ROW2  = colors.HexColor("#0d1117")
_LIGHT = colors.HexColor("#c9d1d9")
 
def _tbl_style():
    return TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  _DARK2),
        ("TEXTCOLOR",     (0,0),(-1,0),  _GOLD),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 8),
        ("ALIGN",         (0,0),(-1,-1), "LEFT"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [_ROW1, _ROW2]),
        ("TEXTCOLOR",     (0,1),(-1,-1), _LIGHT),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#30363d")),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ("RIGHTPADDING",  (0,0),(-1,-1), 5),
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 3),
    ])
 
def _side_style():
    return TableStyle([
        ("VALIGN",       (0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1),0),
        ("RIGHTPADDING", (0,0),(-1,-1),0),
        ("TOPPADDING",   (0,0),(-1,-1),0),
        ("BOTTOMPADDING",(0,0),(-1,-1),0),
    ])
 
def df2tbl(df, widths):
    data = [list(df.columns)] + [list(r) for _,r in df.iterrows()]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(_tbl_style())
    return t
 
def side_by_side(left, right, lw=8.5*cm, rw=8.5*cm, gap=0.5*cm):
    t = Table([[left, Spacer(gap,1), right]], colWidths=[lw, gap, rw])
    t.setStyle(_side_style())
    return t
 
def plotly_img(fig, w=15*cm, h=7*cm):
    buf = io.BytesIO()
    fig.write_image(buf, format="png", width=900, height=420, scale=2)
    buf.seek(0)
    return RLImage(buf, width=w, height=h)
 
def mpl_img(fig, w=15*cm, h=5.5*cm):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0)
    return RLImage(buf, width=w, height=h)
 
def build_pdf_report(s: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    base = getSampleStyleSheet()
    base.add(ParagraphStyle("T1", parent=base["Normal"], fontSize=15, textColor=_GOLD,
        fontName="Helvetica-Bold", spaceAfter=4, alignment=TA_CENTER))
    base.add(ParagraphStyle("T2", parent=base["Normal"], fontSize=10, textColor=_GOLD,
        fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3))
    base.add(ParagraphStyle("T3", parent=base["Normal"], fontSize=8.5, textColor=_GOLD,
        fontName="Helvetica-Bold", spaceBefore=5, spaceAfter=2))
    base.add(ParagraphStyle("SB", parent=base["Normal"], fontSize=7.5, textColor=_LIGHT, spaceAfter=4))
 
    def sec(txt): return Paragraph(txt, base["T2"])
    def sub(txt): return Paragraph(txt, base["T3"])
    def sp(n=0.3): return Spacer(1, n*cm)
    def hr(): return HRFlowable(width="100%", thickness=0.5, color=_DARK2, spaceAfter=4)
 
    hoy = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    selected = s["selected"]
    story = []
 
    # ── Portada
    story += [sp(1),
        Paragraph("REPORTE TECNICO — CEMENTED ROCK FILL (CRF)", base["T1"]),
        Paragraph("Unidad Minera · Metodo Sub Level Stoping", base["SB"]),
        HRFlowable(width="100%", thickness=1.5, color=_GOLD, spaceAfter=6),
        Paragraph(f"Generado: {hoy}   |   Diseno activo: <b>{selected}</b>", base["SB"]),
        sp(0.5)]
 
    # ── 1. DISEÑOS DE MEZCLA
    story += [sec("1. DISENOS DE MEZCLA"), hr()]
    df_mix = s["designs_df"].copy()
    if "A/C" not in df_mix.columns:
        df_mix["A/C"] = (df_mix["Agua (L/m³)"]/df_mix["Cemento (kg/m³)"]).round(3)
    show = df_mix[["Diseño","Cemento (kg/m³)","Agua (L/m³)","Desmonte (kg/m³)","Densidad (kg/m³)","A/C"]]
    story.append(df2tbl(show, [2*cm,3*cm,2.5*cm,3*cm,3*cm,2*cm]))
    story += [sp(0.25), sub("Resistencias a Compresion (MPa)")]
    story.append(df2tbl(s["resist_df"], [2*cm,3.5*cm,3.5*cm,3.5*cm,3.5*cm]))
    story += [sp(0.25)]
 
    resist_df = s["resist_df"]
    fig_res = go.Figure()
    for d, c in zip(["D01","D02","D03","D04"],["#f0a500","#3fb950","#388bfd","#f85149"]):
        fig_res.add_trace(go.Scatter(x=resist_df["Días"], y=resist_df[d], mode="lines+markers",
            name=d, opacity=1.0 if d==selected else 0.4,
            line=dict(color=c, width=3 if d==selected else 1.5)))
    fig_res.update_layout(**PLOTLY_LAYOUT, height=320, title=f"Curva de Resistencia — {selected}")
    story.append(plotly_img(fig_res, w=15*cm, h=6.5*cm))
 
    # ── 2. DISEÑO SELECCIONADO
    story += [PageBreak(), sec("2. DISENO SELECCIONADO"), hr()]
    espec=s["espec"]; agre=s["agre"]
    row_d = df_mix[df_mix["Diseño"]==selected].iloc[0]
    cem=float(row_d["Cemento (kg/m³)"]); desm=float(row_d["Desmonte (kg/m³)"])
    rel_ac=float(row_d["A/C"]); agua_ind=float(espec["Agua_industrial_Lm3"])
    aire=int(espec["Aire_atrapado_pct"]); hum=float(agre["Humedad_natural_pct"])
    absorc=float(agre["Absorcion_pct"])
    agg_corr = desm/(1+hum/100)
    aporte   = agg_corr*((hum-absorc)/100)
    dens_m   = cem+agua_ind+aporte+agg_corr
 
    df_esp = pd.DataFrame({"Parametro":["F'c (kg/cm2)","F'cr (kg/cm2)","Slump (pulg)","Agua ind. (L/m3)","Aire (%)","A/C"],
        "Valor":[f"{espec['Fc_kgcm2']:.0f}",f"{espec['Fcr_kgcm2']:.0f}",f"{espec['Slump_pulg']:.1f}",
                 f"{agua_ind:.1f}",f"{aire}",f"{rel_ac:.3f}"]})
    df_agg = pd.DataFrame({"Parametro":["Tam. max. (pulg)","Tam. nom. (pulg)","Mod. fineza",
                                          "P.U. suelto (kg/m3)","P.U. compact. (kg/m3)","P.E. agr. (kg/m3)","Hum. nat. (%)","Absorcion (%)"],
        "Valor":[f"{agre['Tamano_maximo_pulg']:.2f}",f"{agre['Tamano_nominal_pulg']:.2f}",f"{agre['Modulo_fineza']:.2f}",
                 f"{agre['Peso_unitario_suelto_kgm3']:.0f}",f"{agre['Peso_unitario_compactado_kgm3']:.0f}",
                 f"{agre['Peso_especifico_agregado_kgm3']:.0f}",f"{agre['Humedad_natural_pct']:.2f}",f"{agre['Absorcion_pct']:.2f}"]})
    story.append(side_by_side(df2tbl(df_esp,[5*cm,3*cm]), df2tbl(df_agg,[5.5*cm,3*cm])))
    story.append(sp(0.25))
 
    df_calc = pd.DataFrame({"Concepto":["Cemento (kg/m3)","Agua ind. (L/m3)","Agg. corregido (kg/m3)",
                                         "Aporte agua (L/m3)","Aire atrapado (%)","Densidad mezcla (kg/m3)"],
        "Valor":[f"{cem:.2f}",f"{agua_ind:.2f}",f"{agg_corr:.2f}",f"{aporte:.2f}",f"{aire}%",f"{dens_m:.2f}"]})
    story.append(sub("Calculo del Diseno de Mezcla"))
    story.append(df2tbl(df_calc,[9*cm,6*cm]))
    story.append(sp(0.25))
 
    fig_pie = go.Figure(go.Pie(labels=["Cemento","Agua","Agregado"],
        values=[cem,agua_ind+aporte,agg_corr], hole=0.35,
        marker=dict(colors=["#3fb950","#388bfd","#f0a500"])))
    fig_pie.update_layout(**PLOTLY_LAYOUT, title=f"Composicion CRF — {selected}", height=300)
    story.append(plotly_img(fig_pie, w=13*cm, h=6*cm))
 
    # ── 3. INFRAESTRUCTURA
    story += [PageBreak(), sec("3. INFRAESTRUCTURA — CAMARA DE MEZCLADO"), hr()]
    infra=s["infra"]; pend=s["pendiente"]
    largo=float(infra["Largo_camara_m"]); ancho=float(infra["Ancho_util_m"]); alto=float(infra["Alto_util_m"])
    esp_conc=float(infra["Espesor_concreto_m"]); esp_shot=float(infra["Espesor_shotcrete_m"])
    piso_drop=largo*(abs(pend)/100)
    vol_util=largo*ancho*alto; vol_conc=largo*ancho*esp_conc
    vol_exc=(ancho+2*esp_conc)*(alto+2*esp_conc)*largo
 
    df_eq = pd.DataFrame({"Equipo":["Bomba estacionaria","Chancadora secundaria","Faja transportadora","Tolva de regulacion"],
        "Capacidad":[f"{infra['Bomba_estacionaria_m3h']:.0f} m3/h",f"{infra['Chancadora_secundaria_th']:.0f} t/h",
                     f"{infra['Faja_transportadora_th']:.0f} t/h",f"{infra['Tolva_regulacion_m3']:.0f} m3"]})
    df_per = pd.DataFrame({"Cargo":["Operador","Mecanico","Supervisor"],
        "Cantidad":[int(infra["Personal_operadores"]),int(infra["Personal_mecanicos"]),int(infra["Personal_supervisores"])]})
    story.append(side_by_side(df2tbl(df_eq,[5.5*cm,3.5*cm]), df2tbl(df_per,[4*cm,3*cm]), lw=9.5*cm, rw=7*cm))
    story.append(sp(0.25))
 
    df_geom = pd.DataFrame({"Parametro":["Longitud (m)","Ancho util (m)","Altura util (m)",
                                           "Pendiente piso (%)","Esp. concreto (m)","Esp. shotcrete (m)"],
        "Valor":[largo,ancho,alto,pend,esp_conc,esp_shot]})
    df_vol = pd.DataFrame({"Concepto":["Volumen util (m3)","Caida piso (m)","Vol. concreto (m3)","Vol. excavado (m3)"],
        "Valor":[f"{vol_util:.2f}",f"{piso_drop:.2f}",f"{vol_conc:.2f}",f"{vol_exc:.2f}"]})
    story.append(side_by_side(df2tbl(df_geom,[5.5*cm,3*cm]), df2tbl(df_vol,[5.5*cm,3*cm])))
    story.append(sp(0.3))
 
    fig_mpl, ax = plt.subplots(figsize=(8,3))
    ax.set_facecolor("#161b22"); fig_mpl.patch.set_facecolor("#0d1117")
    ax.add_patch(Rectangle((0,0),largo,alto,edgecolor="#f0a500",facecolor="none",linewidth=2))
    ax.plot([0,largo],[0,-piso_drop],color="#3fb950",linewidth=2)
    ax.add_patch(Rectangle((0,alto),largo,esp_shot,edgecolor="#388bfd",facecolor="none",linestyle="--",linewidth=1.5))
    ax.set_title("Perfil Longitudinal de la Camara",color="#f0a500",fontsize=9)
    ax.set_xlabel("Longitud (m)",color="#c9d1d9",fontsize=8); ax.set_ylabel("Altura (m)",color="#c9d1d9",fontsize=8)
    ax.tick_params(colors="#c9d1d9",labelsize=7); ax.grid(color="#30363d")
    story.append(mpl_img(fig_mpl, w=15*cm, h=5.5*cm))
    plt.close(fig_mpl)
 
    # ── 4. GEOMECÁNICA
    story += [PageBreak(), sec("4. CALCULOS GEOMECANICOS — MITCHELL + DUJISIN"), hr()]
    geo=s["geo"]
    H=float(geo["Altura_caseron_H_m"]); dens_rell=float(geo["Densidad_CRF_kgm3"])
    phi=float(geo["Angulo_friccion_phi_deg"]); fs=float(geo["Factor_seguridad"])
    dens_roca=float(geo["Densidad_roca_kgm3"])
    gamma_rell=dens_rell*9.81/1e6; gamma_roca=dens_roca*9.81/1e6
    K=(1-math.sin(math.radians(phi)))/(1+math.sin(math.radians(phi)))
    sigma_v=gamma_rell*H; sigma_h=K*sigma_v
    sigma_t=sigma_v/fs; sigma_l=sigma_h/fs; sigma_tot=sigma_t+sigma_l
 
    df_p1 = pd.DataFrame({"Parametro":["H (m)","B (m)","L (m)","Dens. CRF (kg/m3)","Cohesion (kPa)","Phi (deg)"],
        "Valor":[f"{geo['Altura_caseron_H_m']:.1f}",f"{geo['Ancho_caseron_B_m']:.1f}",f"{geo['Longitud_caseron_L_m']:.1f}",
                 f"{dens_rell:.0f}",f"{geo['Cohesion_CRF_kPa']:.0f}",f"{phi:.1f}"]})
    df_p2 = pd.DataFrame({"Parametro":["Dens. roca (kg/m3)","Factor seg.","Poisson nu","Gamma CRF (MN/m3)","Gamma roca (MN/m3)"],
        "Valor":[f"{dens_roca:.0f}",f"{fs}",f"{geo['Coeficiente_Poisson']:.2f}",f"{gamma_rell:.6f}",f"{gamma_roca:.6f}"]})
    story.append(side_by_side(df2tbl(df_p1,[5*cm,3*cm]), df2tbl(df_p2,[5*cm,3*cm])))
    story.append(sp(0.25))
 
    df_mit = pd.DataFrame({"Concepto":["sigma_v (MN/m2)","K activo","sigma_h (MN/m2)"],
        "Valor":[f"{sigma_v:.4f}",f"{K:.4f}",f"{sigma_h:.4f}"]})
    df_duj = pd.DataFrame({"Concepto":["sigma techo (MN/m2)","sigma lateral (MN/m2)","F.S. aplicado","sigma total (MN/m2)"],
        "Valor":[f"{sigma_t:.4f}",f"{sigma_l:.4f}",f"{fs}",f"{sigma_tot:.4f}"]})
    story.append(side_by_side(df2tbl(df_mit,[6*cm,3.5*cm]), df2tbl(df_duj,[6*cm,3.5*cm])))
    story.append(sp(0.3))
 
    z = np.linspace(0, H, 50)
    fig_geo = go.Figure()
    fig_geo.add_trace(go.Scatter(x=K*gamma_rell*z, y=z, name="Mitchell",
        mode="lines", line=dict(color="#f0a500",width=3)))
    fig_geo.add_trace(go.Scatter(x=K*gamma_rell*z/fs, y=z, name="Dujisin",
        mode="lines", line=dict(color="#3fb950",width=3,dash="dash")))
    fig_geo.update_layout(**PLOTLY_LAYOUT, height=340,
        title="Distribucion de Presion Lateral (MN/m2)",
        xaxis_title="Presion (MN/m2)", yaxis_title="Altura (m)")
    story.append(plotly_img(fig_geo, w=15*cm, h=7*cm))
 
    # ── Footer
    story += [sp(0.5),
        HRFlowable(width="100%", thickness=1, color=_GOLD, spaceAfter=4),
        Paragraph(f"Cemented Rock Fill · Sistema CRF  |  Desarrollado por: <b>Bradoc Chambilla</b>  |  {hoy}", base["SB"])]
 
    doc.build(story)
    buf.seek(0)
    return buf.read()
 
 
# ─────────────────────────────────────────────
#  BANNER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <h1>⛏ Cemented Rock Fill (CRF)</h1>
  <p>Análisis técnico-económico de factibilidad del relleno detrítico cementado · Método Sub Level Stoping</p>
</div>
""", unsafe_allow_html=True)
 
 
# ═══════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════
if "csv_activo" not in st.session_state: st.session_state.csv_activo = False
if "designs_df" not in st.session_state:
    st.session_state.designs_df = pd.DataFrame({
        "Diseño":["D01","D02","D03","D04"],
        "Cemento (kg/m³)":[75.,90.,103.,138.],
        "Agua (L/m³)":[60.,72.,82.,110.],
        "Desmonte (kg/m³)":[2812.,2760.,2717.,2595.],
        "Densidad (kg/m³)":[2947.,2922.,2902.,2843.],
    })
if "resist_df" not in st.session_state:
    st.session_state.resist_df = pd.DataFrame({
        "Días":[7,14,21,28,56],
        "D01":[0.65,1.01,1.39,1.66,1.68],"D02":[1.07,1.37,1.63,2.08,2.11],
        "D03":[1.68,2.73,3.38,4.82,4.95],"D04":[2.58,3.14,4.41,5.21,6.53],
    })
if "espec" not in st.session_state: st.session_state.espec = DEFAULT_ESPEC.copy()
if "agre"  not in st.session_state: st.session_state.agre  = DEFAULT_AGRE.copy()
if "infra" not in st.session_state: st.session_state.infra = DEFAULT_INFRA.copy()
if "geo"   not in st.session_state: st.session_state.geo   = DEFAULT_GEO.copy()
if "pendiente" not in st.session_state: st.session_state.pendiente = -1
 
 
# ═══════════════════════════════════════════════════════════
#  CARGA CSV
# ═══════════════════════════════════════════════════════════
st.markdown("### 📂 Carga de Datos Maestros")
col_info, col_dl = st.columns([3,1])
with col_info:
    st.info("**Paso 1:** Descargue la plantilla CSV → **Paso 2:** Complete sus datos → **Paso 3:** Suba el archivo aquí.")
with col_dl:
    st.download_button("⬇️ Descargar Plantilla CSV", data=generate_template_csv(),
        file_name="plantilla_CRF_maestro.csv", mime="text/csv", use_container_width=True)
 
uploaded_csv = st.file_uploader("Seleccionar archivo CSV maestro (.csv)", type=["csv"], key="master_csv")
if uploaded_csv is not None:
    try:
        sections = parse_master_csv(uploaded_csv)
        def load_kv(sec, default):
            if sec not in sections: return default.copy()
            df_ = sections[sec].copy(); df_.columns = ["Parametro","Valor"]
            d = default.copy()
            for _, r in df_.iterrows():
                k = str(r["Parametro"]).strip()
                if k in d: d[k] = float(r["Valor"])
            return d
        if "DESIGNS" in sections:
            dc = sections["DESIGNS"].copy()
            dc.columns = ["Diseño","Cemento (kg/m³)","Agua (L/m³)","Desmonte (kg/m³)","Densidad (kg/m³)"]
            for col in dc.columns[1:]: dc[col] = pd.to_numeric(dc[col], errors="coerce")
            st.session_state.designs_df = dc.reset_index(drop=True)
        if "RESISTENCIAS" in sections:
            dr = sections["RESISTENCIAS"].copy(); dr.columns = ["Días","D01","D02","D03","D04"]
            for col in dr.columns: dr[col] = pd.to_numeric(dr[col], errors="coerce")
            st.session_state.resist_df = dr.reset_index(drop=True)
        st.session_state.espec = load_kv("ESPECIFICACIONES", DEFAULT_ESPEC)
        st.session_state.agre  = load_kv("AGREGADO",        DEFAULT_AGRE)
        st.session_state.infra = load_kv("INFRAESTRUCTURA", DEFAULT_INFRA)
        st.session_state.geo   = load_kv("GEOMECANICA",     DEFAULT_GEO)
        st.session_state.csv_activo = True
        st.success(f"✔ CSV cargado — secciones: {', '.join(sections.keys())}.")
    except Exception as e:
        st.error(f"❌ Error al procesar el CSV: {e}")
 
if st.session_state.csv_activo:
    if st.button("🔄 Restaurar datos por defecto"):
        for k in ["csv_activo","designs_df","resist_df","espec","agre","infra","geo"]:
            if k in st.session_state: del st.session_state[k]
        st.rerun()
 
st.markdown("---")
 
 
# ═══════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════
tabs = st.tabs(["🧪 Diseños de Mezcla","📐 Diseño Seleccionado","🏗️ Infraestructura","📊 Cálculos Geomecánicos"])
 
 
# ╔══════════════════════════════════════════════╗
#  TAB 1 — DISEÑOS DE MEZCLA
# ╚══════════════════════════════════════════════╝
with tabs[0]:
    st.markdown("### 🧪 Diseños de Mezcla — Prueba Piloto")
    df = st.session_state.designs_df.copy()
    resist_df = st.session_state.resist_df.copy()
    df["Total"]       = df["Cemento (kg/m³)"]+df["Agua (L/m³)"]+df["Desmonte (kg/m³)"]
    df["Cemento (%)"] = (df["Cemento (kg/m³)"]/df["Total"]*100).round(2)
    df["Agua (%)"]    = (df["Agua (L/m³)"]/df["Total"]*100).round(2)
    df["Desmonte (%)"]= (df["Desmonte (kg/m³)"]/df["Total"]*100).round(2)
    df["A/C"]         = (df["Agua (L/m³)"]/df["Cemento (kg/m³)"]).round(3)
 
    st.markdown("#### Diseño de Mezcla (kg/m³ y L/m³)")
    st.markdown(render_table(df[["Diseño","Cemento (kg/m³)","Cemento (%)","Agua (L/m³)","Agua (%)","Desmonte (kg/m³)","Desmonte (%)","Densidad (kg/m³)","A/C"]]), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Desarrollo de Resistencia a Compresión (MPa)")
    st.markdown(render_table(resist_df), unsafe_allow_html=True)
    st.session_state.designs_df = df
 
    st.markdown("### 🎯 Seleccionar Diseño")
    selected = st.selectbox("Seleccione un diseño:", df["Diseño"].tolist(), key="select_design")
    st.session_state.selected_design = selected
    st.info(f"📌 Diseño seleccionado: **{selected}**")
 
    st.markdown("### 📈 Curva de Resistencia")
    fig_res = go.Figure()
    for d, color in zip(["D01","D02","D03","D04"], COLORS):
        fig_res.add_trace(go.Scatter(x=resist_df["Días"], y=resist_df[d],
            mode="lines+markers", name=d,
            opacity=1.0 if d==selected else 0.3,
            line=dict(color=color, width=4 if d==selected else 2)))
    fig_res.update_layout(**PLOTLY_LAYOUT, height=380, title=f"Curva de Resistencia — {selected}")
    st.plotly_chart(fig_res, use_container_width=True)
 
    st.markdown("### 📊 Resistencia a 28 días")
    res_28 = resist_df[resist_df["Días"]==28].iloc[0]
    fig_28 = go.Figure()
    for d, color in zip(["D01","D02","D03","D04"], COLORS):
        fig_28.add_trace(go.Bar(x=[d], y=[res_28[d]], marker_color=color,
            opacity=1.0 if d==selected else 0.25,
            text=[f"{res_28[d]:.2f} MPa"], textposition="outside"))
    fig_28.update_layout(**PLOTLY_LAYOUT, title=f"Resistencia 28d — {selected}", height=360, showlegend=False)
    st.plotly_chart(fig_28, use_container_width=True)
 
 
# ╔══════════════════════════════════════════════╗
#  TAB 2 — DISEÑO SELECCIONADO
# ╚══════════════════════════════════════════════╝
with tabs[1]:
    st.markdown("## 📐 Diseño de Mezcla Seleccionado")
    if "selected_design" not in st.session_state:
        st.warning("Seleccione un diseño en la pestaña anterior."); st.stop()
 
    selected = st.session_state.selected_design
    st.markdown(f"### 🎯 Diseño: **{selected}**")
    df_all = st.session_state.designs_df.copy()
    if "A/C" not in df_all.columns:
        df_all["A/C"] = (df_all["Agua (L/m³)"]/df_all["Cemento (kg/m³)"]).round(3)
    df_resist = st.session_state.resist_df.copy()
    espec = st.session_state.espec; agre = st.session_state.agre
    row = df_all[df_all["Diseño"]==selected].iloc[0]
    cem=float(row["Cemento (kg/m³)"]); desm=float(row["Desmonte (kg/m³)"])
    rel_ac=float(row["A/C"]); resist_28=float(df_resist[df_resist["Días"]==28][selected].values[0])
    agua_ind=float(espec["Agua_industrial_Lm3"]); aire_at=int(espec["Aire_atrapado_pct"])
    hum=float(agre["Humedad_natural_pct"]); absorc=float(agre["Absorcion_pct"])
    peso_esp_cem=float(agre["Peso_especifico_cemento_kgm3"]); dens_agua=float(agre["Densidad_agua_kgm3"])
    agg_corr=desm/(1+hum/100); aporte=agg_corr*((hum-absorc)/100)
    dens_m=cem+agua_ind+aporte+agg_corr
 
    # Fila 1: Especificaciones | Agregado
    st.markdown("### 🧱 Especificaciones y Características del Agregado")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Especificaciones del Diseño**")
        st.markdown(render_table(pd.DataFrame({
            "Parámetro":["F'c (kg/cm²)","F'cr (kg/cm²)","Slump (pulg)","Agua ind. (L/m³)","Aire (%)","A/C"],
            "Valor":[f"{espec['Fc_kgcm2']:.0f}",f"{espec['Fcr_kgcm2']:.0f}",f"{espec['Slump_pulg']:.1f}",
                     f"{agua_ind:.1f}",f"{aire_at}",f"{rel_ac:.3f}"]
        })), unsafe_allow_html=True)
    with c2:
        st.markdown("**Características del Agregado**")
        st.markdown(render_table(pd.DataFrame({
            "Parámetro":["Tam. máx. (pulg)","Tam. nom. (pulg)","Mód. fineza",
                         "P.U. suelto (kg/m³)","P.U. compact. (kg/m³)","P.E. agr. (kg/m³)","Hum. nat. (%)","Absorción (%)"],
            "Valor":[f"{agre['Tamano_maximo_pulg']:.2f}",f"{agre['Tamano_nominal_pulg']:.2f}",f"{agre['Modulo_fineza']:.2f}",
                     f"{agre['Peso_unitario_suelto_kgm3']:.0f}",f"{agre['Peso_unitario_compactado_kgm3']:.0f}",
                     f"{agre['Peso_especifico_agregado_kgm3']:.0f}",f"{agre['Humedad_natural_pct']:.2f}",f"{agre['Absorcion_pct']:.2f}"]
        })), unsafe_allow_html=True)
 
    # Fila 2: Adicionados | Cálculo mezcla
    st.markdown("### 🧪 Adicionados y Cálculo de Mezcla")
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**Adicionados**")
        st.markdown(render_table(pd.DataFrame({
            "Propiedad":["P.E. cemento (kg/m³)","Densidad agua (kg/m³)"],
            "Valor":[f"{peso_esp_cem:.0f}",f"{dens_agua:.2f}"]
        })), unsafe_allow_html=True)
    with c4:
        st.markdown("**Cálculo del Diseño de Mezcla**")
        st.markdown(render_table(pd.DataFrame({
            "Concepto":["Cemento (kg/m³)","Agua ind. (L/m³)","Agg. corregido (kg/m³)",
                        "Aporte agua (L/m³)","Aire atrapado (%)","Densidad mezcla (kg/m³)"],
            "Valor":[f"{cem:.2f}",f"{agua_ind:.2f}",f"{agg_corr:.2f}",
                     f"{aporte:.2f}",f"{aire_at}%",f"{dens_m:.2f}"]
        })), unsafe_allow_html=True)
 
    # Tanda
    st.markdown("### 🧮 Cálculo por Tanda")
    tanda = st.number_input("Tanda (m³ por ciclo)", value=10.0, step=0.5)
    st.markdown(render_table(pd.DataFrame({
        "Material":["Cemento","Agua (total)","Agregado"],
        "Por tanda":[f"{cem*tanda:.2f}",f"{(agua_ind+aporte)*tanda:.2f}",f"{agg_corr*tanda:.2f}"]
    })), unsafe_allow_html=True)
 
    # Dosificación final
    st.markdown("### 🧾 Dosificación de Mezcla — Resumen Final")
    st.markdown(render_table(pd.DataFrame({
        "Componente":["Cemento","Desmonte","Agua industrial","Relación A/C","Densidad mezcla final"],
        "Valor":[f"{cem:.2f} kg/m³",f"{desm:.2f} kg/m³",f"{agua_ind:.2f} L/m³",f"{rel_ac:.3f}",f"{dens_m:.2f} kg/m³"]
    })), unsafe_allow_html=True)
 
    st.markdown("### 📊 Gráficos del Diseño Seleccionado")
    cg1, cg2 = st.columns(2)
    with cg1:
        fig_pie = go.Figure(go.Pie(labels=["Cemento","Agua","Agregado"],
            values=[cem,agua_ind+aporte,agg_corr], hole=0.35))
        fig_pie.update_layout(**PLOTLY_LAYOUT, title=f"Composición — {selected}")
        st.plotly_chart(fig_pie, use_container_width=True)
    with cg2:
        fig_bar = go.Figure(go.Bar(x=["Cemento","Agua total","Agregado"],
            y=[cem,agua_ind+aporte,agg_corr], marker_color=["#3fb950","#388bfd","#f0a500"],
            text=[f"{cem:.1f}",f"{agua_ind+aporte:.1f}",f"{agg_corr:.1f}"], textposition="outside"))
        fig_bar.update_layout(**PLOTLY_LAYOUT, title="Componentes por m³")
        st.plotly_chart(fig_bar, use_container_width=True)
 
    if st.button("💾 Guardar Diseño"):
        st.session_state.saved_mix = {"diseño":selected,"cemento":cem,"agua":agua_ind,
            "agregado":desm,"rel_ac":rel_ac,"densidad_mezcla":dens_m,"aire":aire_at,"resistencia_28d":resist_28}
        st.success("✔ Diseño guardado correctamente.")
 
 
# ╔══════════════════════════════════════════════╗
#  TAB 3 — INFRAESTRUCTURA
# ╚══════════════════════════════════════════════╝
with tabs[2]:
    st.markdown("## 🏗️ Infraestructura · Cámara de Mezclado del CRF")
    if st.session_state.csv_activo:
        st.success("📂 Parámetros cargados desde el CSV maestro.")
    else:
        st.info("📋 Mostrando datos por defecto.")
 
    infra = st.session_state.infra
    largo=float(infra["Largo_camara_m"]); ancho=float(infra["Ancho_util_m"]); alto=float(infra["Alto_util_m"])
    esp_conc=float(infra["Espesor_concreto_m"]); esp_shot=float(infra["Espesor_shotcrete_m"])
 
    pendiente = st.selectbox("Pendiente del piso (%)", [-1, -2])
    st.session_state.pendiente = pendiente
 
    # Fila 1: Equipos | Personal
    st.markdown("### ⚙️ Equipos y Personal")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Equipos Principales**")
        st.markdown(render_table(pd.DataFrame({
            "Equipo":["Bomba estacionaria","Chancadora secundaria","Faja transportadora","Tolva de regulación"],
            "Capacidad":[f"{infra['Bomba_estacionaria_m3h']:.0f} m³/h",f"{infra['Chancadora_secundaria_th']:.0f} t/h",
                         f"{infra['Faja_transportadora_th']:.0f} t/h",f"{infra['Tolva_regulacion_m3']:.0f} m³"]
        })), unsafe_allow_html=True)
    with c2:
        st.markdown("**Personal Directo Requerido**")
        st.markdown(render_table(pd.DataFrame({
            "Cargo":["Operador","Mecánico","Supervisor"],
            "Cantidad":[int(infra["Personal_operadores"]),int(infra["Personal_mecanicos"]),int(infra["Personal_supervisores"])]
        })), unsafe_allow_html=True)
 
    # Fila 2: Geometría | Volúmenes
    piso_drop=largo*(abs(pendiente)/100)
    vol_util=largo*ancho*alto; vol_conc=largo*ancho*esp_conc
    vol_exc=(ancho+2*esp_conc)*(alto+2*esp_conc)*largo
 
    st.markdown("### 📐 Geometría y Volúmenes")
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**Geometría de la Cámara**")
        st.markdown(render_table(pd.DataFrame({
            "Parámetro":["Longitud (m)","Ancho útil (m)","Altura útil (m)","Pendiente piso (%)",
                         "Esp. concreto (m)","Esp. shotcrete (m)","Esp. relleno (m)","Altura buzón (m)","Ancho bandeja (m)"],
            "Valor":[largo,ancho,alto,pendiente,esp_conc,esp_shot,
                     infra["Espesor_relleno_estructural_m"],infra["Altura_buzon_m"],infra["Ancho_bandeja_m"]]
        })), unsafe_allow_html=True)
    with c4:
        st.markdown("**Cálculos de Volúmenes**")
        st.markdown(render_table(pd.DataFrame({
            "Concepto":["Volumen útil (m³)","Caída del piso (m)","Vol. concreto (m³)","Vol. excavado (m³)"],
            "Valor":[f"{vol_util:.2f}",f"{piso_drop:.2f}",f"{vol_conc:.2f}",f"{vol_exc:.2f}"]
        })), unsafe_allow_html=True)
 
    st.markdown("## 📊 Perfil Longitudinal de la Cámara de Mezclado")
    fig, ax = plt.subplots(figsize=(10,4))
    ax.set_facecolor("#161b22"); fig.patch.set_facecolor("#0d1117")
    ax.add_patch(Rectangle((0,0),largo,alto,edgecolor="#f0a500",facecolor="none",linewidth=2))
    ax.plot([0,largo],[0,-piso_drop],color="#3fb950",linewidth=2,label="Piso con pendiente")
    ax.add_patch(Rectangle((0,alto),largo,esp_shot,edgecolor="#388bfd",facecolor="none",linestyle="--",linewidth=1.8))
    axins = inset_axes(ax,width="30%",height="50%",loc="upper right")
    axins.plot([0,5],[0,-5*(abs(pendiente)/100)],color="#3fb950")
    axins.set_title("Detalle 1:20",color="#c9d1d9",fontsize=9)
    axins.set_facecolor("#202833"); axins.tick_params(colors="#7d8590")
    ax.set_title("Perfil Longitudinal de la Cámara",color="#f0a500")
    ax.set_xlabel("Longitud (m)",color="#c9d1d9"); ax.set_ylabel("Altura (m)",color="#c9d1d9")
    ax.grid(color="#30363d")
    st.pyplot(fig)
    plt.close(fig)
 
 
# ╔══════════════════════════════════════════════╗
#  TAB 4 — CÁLCULOS GEOMECÁNICOS
# ╚══════════════════════════════════════════════╝
with tabs[3]:
    st.markdown("## 📊 Cálculos Geomecánicos — Método Mitchell + Dujisin")
    if st.session_state.csv_activo:
        st.success("📂 Parámetros cargados desde el CSV maestro.")
    else:
        st.info("📋 Mostrando datos por defecto.")
 
    geo = st.session_state.geo
    H=float(geo["Altura_caseron_H_m"]); B=float(geo["Ancho_caseron_B_m"]); L=float(geo["Longitud_caseron_L_m"])
    dens_rell=float(geo["Densidad_CRF_kgm3"]); cohes=float(geo["Cohesion_CRF_kPa"])
    phi=float(geo["Angulo_friccion_phi_deg"]); dens_roca=float(geo["Densidad_roca_kgm3"])
    fs=float(geo["Factor_seguridad"]); poisson=float(geo["Coeficiente_Poisson"])
    gamma_rell=dens_rell*9.81/1e6; gamma_roca=dens_roca*9.81/1e6
    K=(1-math.sin(math.radians(phi)))/(1+math.sin(math.radians(phi)))
    sigma_v=gamma_rell*H; sigma_h=K*sigma_v
    sigma_techo=sigma_v/fs; sigma_lat=sigma_h/fs; sigma_tot=sigma_techo+sigma_lat
 
    # Fila 1: Geometría/Materiales | Propiedades geomecánicas
    st.markdown("### 📥 Parámetros de Entrada")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Geometría y Materiales**")
        st.markdown(render_table(pd.DataFrame({
            "Parámetro":["Altura caserón H (m)","Ancho caserón B (m)","Longitud caserón L (m)",
                         "Densidad CRF (kg/m³)","Cohesión CRF (kPa)"],
            "Valor":[f"{H:.1f}",f"{B:.1f}",f"{L:.1f}",f"{dens_rell:.0f}",f"{cohes:.0f}"]
        })), unsafe_allow_html=True)
    with c2:
        st.markdown("**Propiedades Geomecánicas**")
        st.markdown(render_table(pd.DataFrame({
            "Parámetro":["Ángulo fricción φ (°)","Densidad roca (kg/m³)","Factor de Seguridad","Coef. Poisson ν"],
            "Valor":[f"{phi:.1f}",f"{dens_roca:.0f}",f"{fs}",f"{poisson:.2f}"]
        })), unsafe_allow_html=True)
 
    # Fila 2: Pesos unitarios | Mitchell
    st.markdown("### 🔁 Conversión y Mitchell (1970)")
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**Pesos Unitarios**")
        st.markdown(render_table(pd.DataFrame({
            "Material":["Relleno CRF","Roca encajonante"],
            "Densidad (kg/m³)":[dens_rell,dens_roca],
            "γ (MN/m³)":[f"{gamma_rell:.6f}",f"{gamma_roca:.6f}"]
        })), unsafe_allow_html=True)
    with c4:
        st.markdown("**Cálculos Mitchell (1970)**")
        st.markdown(render_table(pd.DataFrame({
            "Concepto":["Sobrecarga vertical σv (MN/m²)","Coef. activo K","Presión lateral σh (MN/m²)"],
            "Valor":[f"{sigma_v:.4f}",f"{K:.4f}",f"{sigma_h:.4f}"]
        })), unsafe_allow_html=True)
 
    # Fila 3: Dujisin | Resultado final
    st.markdown("### 🧮 Dujisin (1992) y Resultado")
    c5, c6 = st.columns(2)
    with c5:
        st.markdown("**Presiones Reducidas**")
        st.markdown(render_table(pd.DataFrame({
            "Concepto":["σ techo reducida (MN/m²)","σ lateral reducida (MN/m²)","Factor de Seguridad"],
            "Valor":[f"{sigma_techo:.4f}",f"{sigma_lat:.4f}",f"{fs}"]
        })), unsafe_allow_html=True)
    with c6:
        st.markdown("**Presión Total Actuante**")
        st.markdown(render_table(pd.DataFrame({
            "Concepto":["σ total sobre caserón (MN/m²)"],
            "Valor":[f"{sigma_tot:.4f}"]
        })), unsafe_allow_html=True)
 
    st.info(f"📌 **Presión total actuante sobre el caserón:** {sigma_tot:.4f} MN/m²")
 
    # Gráficos side-by-side
    st.markdown("### 📈 Gráficos Geomecánicos")
    cg1, cg2 = st.columns(2)
    z = np.linspace(0, H, 50)
    with cg1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=K*gamma_rell*z, y=z, name="Mitchell",
            mode="lines", line=dict(color="#f0a500",width=3)))
        fig1.add_trace(go.Scatter(x=K*gamma_rell*z/fs, y=z, name="Dujisin",
            mode="lines", line=dict(color="#3fb950",width=3,dash="dash")))
        fig1.update_layout(**PLOTLY_LAYOUT, title="Presión Lateral (MN/m²)",
            xaxis_title="Presión", yaxis_title="Altura (m)", height=380)
        st.plotly_chart(fig1, use_container_width=True)
    with cg2:
        fig2 = go.Figure(go.Bar(x=["σ techo reducida"], y=[sigma_techo],
            text=[f"{sigma_techo:.4f} MN/m²"], textposition="outside", marker_color="#388bfd"))
        fig2.update_layout(**PLOTLY_LAYOUT, title="Soporte Requerido — Techo",
            height=380, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
 
    # ══ BOTÓN GENERAR REPORTE ══
    st.markdown("---")
    st.markdown("### 📄 Exportar Reporte Completo")
    if "selected_design" not in st.session_state:
        st.warning("⚠️ Seleccione un diseño en la pestaña 'Diseños de Mezcla' antes de generar el reporte.")
    else:
        if st.button("📄 Generar Reporte PDF", type="primary", use_container_width=True):
            with st.spinner("Generando reporte PDF, por favor espere..."):
                try:
                    pdf_bytes = build_pdf_report({
                        "selected":   st.session_state.selected_design,
                        "designs_df": st.session_state.designs_df,
                        "resist_df":  st.session_state.resist_df,
                        "espec":      st.session_state.espec,
                        "agre":       st.session_state.agre,
                        "infra":      st.session_state.infra,
                        "geo":        st.session_state.geo,
                        "pendiente":  st.session_state.get("pendiente", -1),
                    })
                    hoy_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                    st.download_button(
                        label="⬇️ Descargar PDF",
                        data=pdf_bytes,
                        file_name=f"Reporte_CRF_{st.session_state.selected_design}_{hoy_str}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    st.success("✔ Reporte generado. Haga clic en el botón de descarga.")
                except Exception as e:
                    st.error(f"❌ Error al generar el reporte: {e}")
                    st.exception(e)
 
 
# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
hoy = datetime.datetime.now().strftime("%d/%m/%Y")
st.markdown(f"""
<style>
.footer-box {{
    margin-top: 40px; padding: 18px; width: 100%; text-align: center;
    background: rgba(240,165,0,0.10); border-top: 2px solid #f0a500;
    border-radius: 6px; font-size: 0.9rem; color: #e6edf3;
}}
.footer-title {{ font-family: 'Oswald', sans-serif; font-size: 1.1rem; color: #f0a500; }}
.footer-sub   {{ color: #c9d1d9; }}
</style>
<div class="footer-box">
    <div class="footer-title">Cemented Rock Fill · Sistema CRF</div>
    <div class="footer-sub">Aplicación generada para análisis técnico-geomecánico y diseño de relleno detrítico cementado.</div>
    <br>
    <div class="footer-sub">Versión 1.4 · Actualizado el {hoy}</div>
    <div class="footer-sub">Desarrollado por: <b>Bradoc Chambilla</b></div>
</div>
""", unsafe_allow_html=True)
