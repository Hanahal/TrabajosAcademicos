import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import pandas as pd

st.title("Diseño de Sostenimiento en Minería Subterránea")
st.subheader("Diseño de Cimbras 'H'")
st.subheader("Metodología de Cemal Biron")

# Entradas del usuario
RMR = st.number_input("RMR del macizo rocoso", min_value=1, max_value=100, value=30)
yr = st.number_input("Peso específico de la roca (ton/m3)", value=2.5, step=0.1)
La = st.number_input("Claro del túnel (m)", value=3.2, step=0.1)
r = st.number_input("Radio efectivo r (m)", value=1.5, step=0.1)
h_ = st.number_input("Altura efectiva h' (m)", value=1.5, step=0.1)
a = st.number_input("Espaciamiento de cimbras (m)", value=1.0, step=0.1)

# Relación RMR y alfa
if RMR > 41:
    alfa = 0.25
elif 31 <= RMR <= 40:
    alfa = 0.50
elif 20 <= RMR <= 30:
    alfa = 1.0
else:
    alfa = 1.5

st.write(f"Coeficiente alfa (α) asignado: **{alfa}**")

# Altura de perturbación
h = alfa * La
st.write(f"Altura de perturbación (h): {h:.2f} m")

# Presión en corona y hastiales
σt = yr * h
st.write(f"Presión (σt): {σt:.2f} ton/m²")

# Carga distribuida
qt = σt * a
st.write(f"Carga distribuida (qt): {qt:.2f} ton/m")

# Reacciones horizontales
Ay = ((0.78*h_ + 0.666*r)*(qt)*(r**3)) / ((0.666*h_**3) + (np.pi*r*(h_**2)) + (4*(h_**2)) + (1.57*(r**3)))
st.write(f"Reacciones laterales (Ay = By): {Ay:.2f} ton")

# Tabulación de ángulos
angulos = np.arange(0, 95, 5)
momentos, normales = [], []

for ang in angulos:
    rad = np.deg2rad(ang)
    M = (0.5*qt*(r**2)*(np.sin(rad)**2)) - (Ay*(h_ + (r*np.sin(rad))))
    N = (-qt*r*(np.cos(rad)**2)) - (Ay*np.sin(rad))
    momentos.append(M)
    normales.append(N)

# Crear DataFrame
df = pd.DataFrame({
    "Ángulo (°)": angulos,
    "Momento (ton*m)": momentos,
    "Normal (ton)": normales
})

# Identificar máximos y mínimos con los nombres correctos
mom_max_idx = df["Momento (ton*m)"].idxmax()
mom_min_idx = df["Momento (ton*m)"].idxmin()
norm_max_idx = df["Normal (ton)"].idxmax()
norm_min_idx = df["Normal (ton)"].idxmin()

# Función de resaltado
def resaltar_extremos(s):
    estilo = [""] * len(s)
    if s.name == "Momento (ton*m)":
        estilo[mom_max_idx] = "background-color: #ff7043; color: white"   # naranja fuerte
        estilo[mom_min_idx] = "background-color: #42a5f5; color: white"  # azul fuerte
    elif s.name == "Normal (ton)":
        estilo[norm_max_idx] = "background-color: #66bb6a; color: white" # verde
        estilo[norm_min_idx] = "background-color: #ab47bc; color: white" # morado
    return estilo

# Aplicar estilos y limitar decimales
styled_valores = df.style.apply(resaltar_extremos, axis=0).format(precision=2)

# Mostrar tabla
st.write("### Tabulación de Momentos Flectores y Fuerza Normal")
st.dataframe(styled_valores, width="stretch")



# ==========================
# Gráficas
# ==========================
# ==========================
# Gráfico cimbra tipo baúl con simetría
# ==========================
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(8,6))

# Parámetros geométricos de la cimbra
r = 1.5   # radio del arco
h = 1.5   # altura de los postes

# Arco superior
theta = np.linspace(0, np.pi, 200)
x_arc = r * np.cos(theta)
y_arc = r * np.sin(theta) + h
ax.plot(x_arc, y_arc, color="black")

# Postes verticales
ax.plot([-r, -r], [0, h], color="black")
ax.plot([ r,  r], [0, h], color="black")

# Base horizontal
ax.plot([-r, r], [0, 0], color="black")

# Apoyos
ax.plot([-r, 0, r], [0, 0, 0], "wo", markeredgecolor="black", markersize=12)

# ==========================
# Valores máximos y mínimos
# ==========================
mom_max = np.max(momentos)
mom_min = np.min(momentos)
norm_max = np.max(normales)
norm_min = np.min(normales)

# CORONA (parte superior del arco)
ax.annotate(f"M máx = {mom_max:.2f}",
            xy=(0, h+r), xycoords="data",
            xytext=(0, 20), textcoords="offset points",
            ha="center", color="red", fontsize=10,
            arrowprops=dict(arrowstyle="->", color="red"),
            bbox=dict(facecolor="white", edgecolor="red", boxstyle="round,pad=0.3"))

ax.annotate(f"N máx = {norm_max:.2f}",
            xy=(0, h+r), xycoords="data",
            xytext=(0, -35), textcoords="offset points",
            ha="center", color="blue", fontsize=10,
            arrowprops=dict(arrowstyle="->", color="blue"),
            bbox=dict(facecolor="white", edgecolor="blue", boxstyle="round,pad=0.3"))
# LATERALES (mínimos en ambos lados)
ax.annotate(f"M mín = {mom_min:.2f}",
            xy=(-r, h/2), xycoords="data",
            xytext=(-70, 0), textcoords="offset points",
            ha="center", color="green", fontsize=10,
            arrowprops=dict(arrowstyle="->", color="green"),
            bbox=dict(facecolor="white", edgecolor="green", boxstyle="round,pad=0.3"))

ax.annotate(f"M mín = {mom_min:.2f}",
            xy=( r, h/2), xycoords="data",
            xytext=(70, 0), textcoords="offset points",
            ha="center", color="green", fontsize=10,
            arrowprops=dict(arrowstyle="->", color="green"),
            bbox=dict(facecolor="white", edgecolor="green", boxstyle="round,pad=0.3"))

ax.annotate(f"N mín = {norm_min:.2f}",
            xy=(-r, h/2-0.4), xycoords="data",
            xytext=(-70, -15), textcoords="offset points",
            ha="center", color="purple", fontsize=10,
            arrowprops=dict(arrowstyle="->", color="purple"),
            bbox=dict(facecolor="white", edgecolor="purple", boxstyle="round,pad=0.3"))

ax.annotate(f"N mín = {norm_min:.2f}",
            xy=( r, h/2-0.4), xycoords="data",
            xytext=(70, -15), textcoords="offset points",
            ha="center", color="purple", fontsize=10,
            arrowprops=dict(arrowstyle="->", color="purple"),
            bbox=dict(facecolor="white", edgecolor="purple", boxstyle="round,pad=0.3"))

# ==========================
# Dibujar macizo rocoso con líneas diagonales
# ==========================
rock = patches.Rectangle(
    (-3, -0.5), 6, 4, 
    facecolor="#FFB74D", alpha=0.2, 
    hatch="//"   # 👈 líneas diagonales
)
ax.add_patch(rock)

# Hueco excavado (zona de la cimbra)
theta = np.linspace(0, np.pi, 200)
x_arc = r * np.cos(theta)
y_arc = r * np.sin(theta) + h
excavacion_x = np.concatenate([[-r, -r], x_arc, [r, r]])
excavacion_y = np.concatenate([[0, h], y_arc, [h, 0]])
ax.fill(excavacion_x, excavacion_y, "white")

# ==========================
# Dibujar la cimbra
# ==========================
ax.plot(x_arc, y_arc, color="black")           # arco
ax.plot([-r, -r], [0, h], color="black")       # poste izq
ax.plot([ r,  r], [0, h], color="black")       # poste der
ax.plot([-r, r], [0, 0], color="black")        # base
ax.plot([-r, 0, r], [0, 0, 0], "wo", markeredgecolor="black", markersize=12) # apoyos


# ==========================
# Configuración
# ==========================
ax.set_aspect("equal")
ax.axis("off")

st.pyplot(fig, clear_figure=False)


# Cálculo de módulo de sección
σsf = 14000  # ton/m2 (acero normal)
a_coef = 0.149 * σsf
b_coef = 9.780 * σsf - qt * r - 0.149 * Ay * (h_ + 0.5 * Ay / qt)
c_coef = -9.780 * Ay * (h_ + 0.5 * Ay / qt)

disc = b_coef**2 - 4*a_coef*c_coef

if disc < 0:
    st.error("No hay solución real para el módulo de sección (discriminante negativo).")
else:
    S1 = (-b_coef + math.sqrt(disc)) / (2*a_coef)
    S2 = (-b_coef - math.sqrt(disc)) / (2*a_coef)
    S_m3 = S1 if S1 > 0 else S2
    S_cm3 = S_m3 * 1e6

    ###st.write("**Ecuación cuadrática de S:**")
    #st.latex(r"\sigma_{sf} = \frac{q_t r}{0.149S + 9.780} + \frac{A_y(h' + 0.5 A_y/q_t)}{S}")

    #st.write("**Coeficientes:**")
    #st.latex(f"a = {a_coef:.3f}, \\quad b = {b_coef:.3f}, \\quad c = {c_coef:.3f}")

    #st.write(f"Discriminante Δ = {disc:.3e}")

    st.success(f"Módulo de sección requerido: **{S_cm3:.2f} cm³**")

    # ==========================
    # Tabla de perfiles completa
    # ==========================
    data = [
        {"Designación":"W12x87","Área (cm²)":163.0,"Peralte (cm)":31.8,"Ancho Patín (cm)":30.8,"Espesor Alma (cm)":1.3,"Espesor Patín (cm)":2.1,"Ix (cm⁴)":30439.9,"Sx (cm³)":19129.9,"Iy (cm⁴)":100216.6,"Sy (cm³)":650.8},
        {"Designación":"W12x50","Área (cm²)":92.8,"Peralte (cm)":31.0,"Ancho Patín (cm)":20.5,"Espesor Alma (cm)":0.9,"Espesor Patín (cm)":1.6,"Ix (cm⁴)":16038.2,"Sx (cm³)":10360.0,"Iy (cm⁴)":23440.0,"Sy (cm³)":228.4},
        {"Designación":"W12x45","Área (cm²)":83.3,"Peralte (cm)":30.6,"Ancho Patín (cm)":20.4,"Espesor Alma (cm)":0.9,"Espesor Patín (cm)":1.5,"Ix (cm⁴)":14218.3,"Sx (cm³)":928.3,"Iy (cm⁴)":2078.4,"Sy (cm³)":203.4},
        {"Designación":"W12x26","Área (cm²)":48.8,"Peralte (cm)":31.0,"Ancho Patín (cm)":16.5,"Espesor Alma (cm)":0.6,"Espesor Patín (cm)":1.0,"Ix (cm⁴)":8398.3,"Sx (cm³)":541.1,"Iy (cm⁴)":72.1,"Sy (cm³)":87.5},
        {"Designación":"W12x22","Área (cm²)":41.3,"Peralte (cm)":31.3,"Ancho Patín (cm)":10.2,"Espesor Alma (cm)":0.7,"Espesor Patín (cm)":1.1,"Ix (cm⁴)":6394.4,"Sx (cm³)":409.0,"Iy (cm⁴)":193.7,"Sy (cm³)":37.8},
        {"Designación":"W12x16","Área (cm²)":29.9,"Peralte (cm)":30.5,"Ancho Patín (cm)":10.1,"Espesor Alma (cm)":0.6,"Espesor Patín (cm)":0.7,"Ix (cm⁴)":4174.2,"Sx (cm³)":274.1,"Iy (cm⁴)":117.2,"Sy (cm³)":23.1},
        {"Designación":"W12x14","Área (cm²)":26.3,"Peralte (cm)":30.3,"Ancho Patín (cm)":10.1,"Espesor Alma (cm)":0.5,"Espesor Patín (cm)":0.6,"Ix (cm⁴)":3582.7,"Sx (cm³)":236.9,"Iy (cm⁴)":98.0,"Sy (cm³)":19.4},
        {"Designación":"W10x100","Área (cm²)":188.3,"Peralte (cm)":28.2,"Ancho Patín (cm)":26.3,"Espesor Alma (cm)":1.7,"Espesor Patín (cm)":2.8,"Ix (cm⁴)":25746.4,"Sx (cm³)":1826.4,"Iy (cm⁴)":8599.1,"Sy (cm³)":654.8},
        {"Designación":"W10x54","Área (cm²)":100.7,"Peralte (cm)":25.6,"Ancho Patín (cm)":25.5,"Espesor Alma (cm)":0.9,"Espesor Patín (cm)":1.6,"Ix (cm⁴)":12433.7,"Sx (cm³)":970.3,"Iy (cm⁴)":4306.4,"Sy (cm³)":138.1},
        {"Designación":"W10x45","Área (cm²)":84.2,"Peralte (cm)":25.7,"Ancho Patín (cm)":20.4,"Espesor Alma (cm)":0.9,"Espesor Patín (cm)":1.6,"Ix (cm⁴)":10517.7,"Sx (cm³)":791.9,"Iy (cm⁴)":2220.0,"Sy (cm³)":218.0},
        {"Designación":"W10x39","Área (cm²)":72.6,"Peralte (cm)":25.2,"Ancho Patín (cm)":20.3,"Espesor Alma (cm)":0.8,"Espesor Patín (cm)":1.3,"Ix (cm⁴)":8534.0,"Sx (cm³)":677.4,"Iy (cm⁴)":1872.9,"Sy (cm³)":184.7},
        {"Designación":"W10x30","Área (cm²)":56.5,"Peralte (cm)":26.6,"Ancho Patín (cm)":14.8,"Espesor Alma (cm)":0.8,"Espesor Patín (cm)":1.3,"Ix (cm⁴)":7000.9,"Sx (cm³)":526.5,"Iy (cm⁴)":694.8,"Sy (cm³)":94.2},
        {"Designación":"W10x19","Área (cm²)":36.6,"Peralte (cm)":26.0,"Ancho Patín (cm)":10.7,"Espesor Alma (cm)":0.6,"Espesor Patín (cm)":1.0,"Ix (cm⁴)":4080.0,"Sx (cm³)":313.3,"Iy (cm⁴)":203.5,"Sy (cm³)":38.2},
        {"Designación":"W10x15","Área (cm²)":28.0,"Peralte (cm)":25.4,"Ancho Patín (cm)":10.2,"Espesor Alma (cm)":0.6,"Espesor Patín (cm)":0.7,"Ix (cm⁴)":2797.3,"Sx (cm³)":220.5,"Iy (cm⁴)":120.3,"Sy (cm³)":23.7},
        {"Designación":"W10x12","Área (cm²)":22.3,"Peralte (cm)":25.1,"Ancho Patín (cm)":10.1,"Espesor Alma (cm)":0.5,"Espesor Patín (cm)":0.5,"Ix (cm⁴)":2171.4,"Sx (cm³)":173.2,"Iy (cm⁴)":90.7,"Sy (cm³)":18.0},
        {"Designación":"W8x67","Área (cm²)":126.1,"Peralte (cm)":22.9,"Ancho Patín (cm)":21.0,"Espesor Alma (cm)":1.4,"Espesor Patín (cm)":2.4,"Ix (cm⁴)":11243.4,"Sx (cm³)":983.7,"Iy (cm⁴)":3686.6,"Sy (cm³)":350.6},
        {"Designación":"W8x58","Área (cm²)":109.4,"Peralte (cm)":22.2,"Ancho Patín (cm)":20.9,"Espesor Alma (cm)":1.3,"Espesor Patín (cm)":2.1,"Ix (cm⁴)":947.3,"Sx (cm³)":846.6,"Iy (cm⁴)":3124.2,"Sy (cm³)":299.3},
        {"Designación":"W8x48","Área (cm²)":90.1,"Peralte (cm)":21.6,"Ancho Patín (cm)":20.6,"Espesor Alma (cm)":1.0,"Espesor Patín (cm)":1.7,"Ix (cm⁴)":7582.1,"Sx (cm³)":702.4,"Iy (cm⁴)":2586.3,"Sy (cm³)":246.3},
        {"Designación":"W8x40","Área (cm²)":74.9,"Peralte (cm)":21.0,"Ancho Patín (cm)":20.5,"Espesor Alma (cm)":0.9,"Espesor Patín (cm)":1.4,"Ix (cm⁴)":6024.3,"Sx (cm³)":575.0,"Iy (cm⁴)":2042.9,"Sy (cm³)":199.3},
        {"Designación":"W8x31","Área (cm²)":58.0,"Peralte (cm)":20.3,"Ancho Patín (cm)":20.3,"Espesor Alma (cm)":0.7,"Espesor Patín (cm)":1.1,"Ix (cm⁴)":4565.1,"Sx (cm³)":443.4,"Iy (cm⁴)":1542.7,"Sy (cm³)":151.9},
        {"Designación":"W8x24","Área (cm²)":44.8,"Peralte (cm)":20.1,"Ancho Patín (cm)":16.5,"Espesor Alma (cm)":0.6,"Espesor Patín (cm)":1.0,"Ix (cm⁴)":3376.6,"Sx (cm³)":0,"Iy (cm⁴)":0,"Sy (cm³)":0},
        {"Designación":"W8 x 15","Área (cm²)":28.1,"Peralte (cm)":20.6,"Ancho Patín (cm)":10.2,"Espesor Alma (cm)":0.6,"Espesor Patín (cm)":0.8,"Ix (cm⁴)":1955.8,"Sx (cm³)":189.9,"Iy (cm⁴)":141.8,"Sy (cm³)":27.8},
        {"Designación":"W6 x 25","Área (cm²)":47.0,"Peralte (cm)":16.2,"Ancho Patín (cm)":15.4,"Espesor Alma (cm)":0.8,"Espesor Patín (cm)":1.2,"Ix (cm⁴)":2206.8,"Sx (cm³)":272.4,"Iy (cm⁴)":710.0,"Sy (cm³)":92.0},
        {"Designación":"W6 x 20","Área (cm²)":37.5,"Peralte (cm)":15.7,"Ancho Patín (cm)":15.3,"Espesor Alma (cm)":0.7,"Espesor Patín (cm)":0.9,"Ix (cm⁴)":1706.6,"Sx (cm³)":216.7,"Iy (cm⁴)":552.7,"Sy (cm³)":72.3},
        {"Designación":"W6 x 16","Área (cm²)":30.2,"Peralte (cm)":16.0,"Ancho Patín (cm)":10.2,"Espesor Alma (cm)":0.7,"Espesor Patín (cm)":1.0,"Ix (cm⁴)":1321.9,"Sx (cm³)":165.7,"Iy (cm⁴)":184.2,"Sy (cm³)":36.0},
        {"Designación":"W6 x 15","Área (cm²)":28.2,"Peralte (cm)":15.2,"Ancho Patín (cm)":15.2,"Espesor Alma (cm)":0.6,"Espesor Patín (cm)":0.7,"Ix (cm⁴)":1195.5,"Sx (cm³)":157.1,"Iy (cm⁴)":387.9,"Sy (cm³)":51.0},
        {"Designación":"W6 x 12","Área (cm²)":22.6,"Peralte (cm)":15.3,"Ancho Patín (cm)":10.2,"Espesor Alma (cm)":0.6,"Espesor Patín (cm)":0.7,"Ix (cm⁴)":901.8,"Sx (cm³)":117.8,"Iy (cm⁴)":124.5,"Sy (cm³)":24.5},
        {"Designación":"W6 x 9","Área (cm²)":16.9,"Peralte (cm)":15.0,"Ancho Patín (cm)":10.0,"Espesor Alma (cm)":0.4,"Espesor Patín (cm)":0.5,"Ix (cm⁴)":666.6,"Sx (cm³)":89.0,"Iy (cm⁴)":91.3,"Sy (cm³)":18.2},
        {"Designación":"W5 x 19","Área (cm²)":35.4,"Peralte (cm)":13.1,"Ancho Patín (cm)":12.8,"Espesor Alma (cm)":0.7,"Espesor Patín (cm)":1.1,"Ix (cm⁴)":1079.5,"Sx (cm³)":165.1,"Iy (cm⁴)":379.9,"Sy (cm³)":59.5},
        {"Designación":"W5 x 16","Área (cm²)":29.0,"Peralte (cm)":12.7,"Ancho Patín (cm)":12.7,"Espesor Alma (cm)":0.6,"Espesor Patín (cm)":0.9,"Ix (cm⁴)":872.2,"Sx (cm³)":137.0,"Iy (cm⁴)":312.4,"Sy (cm³)":40.2},
        {"Designación":"W4 x 13","Área (cm²)":24.3,"Peralte (cm)":16.6,"Ancho Patín (cm)":10.3,"Espesor Alma (cm)":0.7,"Espesor Patín (cm)":0.9,"Ix (cm⁴)":466.0,"Sx (cm³)":88.2,"Iy (cm⁴)":160.4,"Sy (cm³)":31.1},
        {"Designación":"HEB 100 x 20.4","Área (cm²)":26.0,"Peralte (cm)":10.0,"Ancho Patín (cm)":10.0,"Espesor Alma (cm)":0.6,"Espesor Patín (cm)":1.0,"Ix (cm⁴)":449.0,"Sx (cm³)":89.9,"Iy (cm⁴)":167.0,"Sy (cm³)":33.4},
        {"Designación":"HEB 120 x 26.7","Área (cm²)":34.0,"Peralte (cm)":12.0,"Ancho Patín (cm)":12.0,"Espesor Alma (cm)":0.65,"Espesor Patín (cm)":1.1,"Ix (cm⁴)":864.0,"Sx (cm³)":144.0,"Iy (cm⁴)":317.0,"Sy (cm³)":52.9},
        {"Designación":"HEB 140 x 33.7","Área (cm²)":43.0,"Peralte (cm)":14.0,"Ancho Patín (cm)":14.0,"Espesor Alma (cm)":0.7,"Espesor Patín (cm)":1.2,"Ix (cm⁴)":1510.0,"Sx (cm³)":216.0,"Iy (cm⁴)":549.0,"Sy (cm³)":78.5},
        {"Designación":"HEB 160 x 42.6","Área (cm²)":54.3,"Peralte (cm)":16.0,"Ancho Patín (cm)":16.0,"Espesor Alma (cm)":0.8,"Espesor Patín (cm)":1.3,"Ix (cm⁴)":2490.0,"Sx (cm³)":311.0,"Iy (cm⁴)":889.0,"Sy (cm³)":111.0},
        {"Designación":"HEB 180 x 51.2","Área (cm²)":65.3,"Peralte (cm)":18.0,"Ancho Patín (cm)":18.0,"Espesor Alma (cm)":0.85,"Espesor Patín (cm)":1.4,"Ix (cm⁴)":3830.0,"Sx (cm³)":426.0,"Iy (cm⁴)":1360.0,"Sy (cm³)":151.0},
    ]

    df_perfiles = pd.DataFrame(data)

    # Seleccionar perfil más cercano pero superior
    df_superiores = df_perfiles[df_perfiles["Sx (cm³)"] >= S_cm3].copy()

    if not df_superiores.empty:
        df_superiores["Diferencia"] = df_superiores["Sx (cm³)"] - S_cm3
        perfil_recomendado = df_superiores.loc[df_superiores["Diferencia"].idxmin()]
    else:
        # fallback: si no hay superior, se elige el más cercano absoluto
        df_perfiles["Diferencia"] = abs(df_perfiles["Sx (cm³)"] - S_cm3)
        perfil_recomendado = df_perfiles.loc[df_perfiles["Diferencia"].idxmin()]

    st.info(f"Perfil recomendado: **{perfil_recomendado['Designación']}** con Sx = {perfil_recomendado['Sx (cm³)']} cm³")

    # Mostrar tabla completa en el orden original de ingreso
   # st.dataframe(df_perfiles.reset_index(drop=True))


perfil_nombre = perfil_recomendado["Designación"]

def resaltar_fila_y_columna(x, perfil, columna_objetivo="Sx (cm³)"):
    # Crear un "mapa" de estilos vacío con el mismo índice y columnas de la serie
    estilos = pd.Series("", index=x.index)

    # Resaltar toda la fila si es el perfil recomendado
    if x["Designación"] == perfil:
        estilos[:] = "background-color: #ffe082"  # amarillo suave

    # Resaltar toda la columna objetivo
    estilos[columna_objetivo] = "background-color: #c8e6c9"  # verde suave

    # Si es la celda de intersección fila+columna
    if x["Designación"] == perfil:
        estilos[columna_objetivo] = "background-color: #ff7043; color: white"  # naranja fuerte

    return estilos

styled_df = df_perfiles.style.apply(
    resaltar_fila_y_columna,
    perfil=perfil_nombre,
    columna_objetivo="Sx (cm³)",
    axis=1
).format(precision=2)
st.write("### Características Mecánicas del Acero")
st.dataframe(styled_df, width="stretch")

# ==========================
# Tabla de equivalencias W ↔ H
# ==========================
equivalencias = pd.DataFrame({
    "Perfil Americano W": ["W6 x 20", "W6 x 21", "W6 x 25", "W4 x 13"],
    "Designación Alternativa": ["6WX20", "6WX21", "6WX25", "4WX13"],
    "Perfil Equivalente H": ["6H 20 lb/pie", "6H 21 lb/pie", "6H 25 lb/pie", "4H 13 lb/pie"]
})

# Normalizar designaciones
designacion_elegida_norm = perfil_recomendado["Designación"].strip().upper()
equivalencias["Perfil Americano W norm"] = equivalencias["Perfil Americano W"].str.upper().str.strip()

# Verificar coincidencia
if designacion_elegida_norm in equivalencias["Perfil Americano W norm"].values:
    idx_match = equivalencias.index[equivalencias["Perfil Americano W norm"] == designacion_elegida_norm][0]
else:
    idx_match = None

# Función de resaltado
def resaltar_equivalencia(s):
    estilo = [""] * len(s)
    if idx_match is not None and s.name == idx_match:
        estilo = ["background-color: #ffcc80; color: black"] * len(s)  # naranja claro
    return estilo

# Mostrar tabla sin la columna auxiliar
styled_equivalencias = (
    equivalencias.drop(columns=["Perfil Americano W norm"])
    .style.apply(resaltar_equivalencia, axis=1)
)

st.write("### Tabla de Equivalencias W ↔ H")
st.dataframe(styled_equivalencias, width="stretch")