import streamlit as st
import math
import pandas as pd

st.title("Diseño de Cimbras Cedentes (Ω)")

st.markdown("### Parámetros de entrada")

# Entradas numéricas
H = st.number_input("Profundidad de la mina (H) [m]", min_value=0.0, value=370.0, step=10.0)
m = st.number_input("Espesor del manto o zona de perturbación (m) [m]", min_value=0.0, value=10.0, step=1.0)

# Diccionario de Kt
opciones_Kt = {
    "Materiales solidificados como anhidrita o concreto fluido": 1,
    "Cuñas de madera": 2,
    "Relleno a mano": 3
}
Kt_texto = st.selectbox("Coeficiente Kt - Tipo de Cimbra en Nervaduras Laterales", list(opciones_Kt.keys()))
Kt = opciones_Kt[Kt_texto]

# Diccionario de Kf
opciones_Kf = {
    "Arenisca": 1,
    "Lutita arenosa": 2,
    "Lutita": 3,
    "Roca muy deformada": 4,
    "Carbón": 5,
    "Carbón + Lutita + roca deformada": 6
}
Kf_texto = st.selectbox("Coeficiente Kf - Tipo de Macizo Rocoso del Techo", list(opciones_Kf.keys()))
Kf = opciones_Kf[Kf_texto]

# Cálculos corregidos
K = -78 + (0.666 * (H / 10)) + (4.3 * m * Kt) + (7.7 * math.sqrt(10 * Kf))
Kp = -58 + (0.039 * (H)) + (3.7 * m * Kt) + (6.6 * math.sqrt(10 * Kf))
Y = 3.5 + 0.23 * K
relacion = Kp / K if K != 0 else 0

# Mostrar resultados
st.markdown("### Resultados")
st.write(f"**Convergencia final (K):** {K:.2f} %")
st.write(f"**Expansión del suelo-roca (K′):** {Kp:.2f} %")
st.write(f"**Cierre de los lados (Y):** {Y:.2f} %")
st.write(f"**Relación K′/K:** {relacion:.2f}")

# Selección de perfil recomendado
if relacion < 0.7:
    perfil = "Ω N-29 (26 a 29 Kg/m)"
else:
    perfil = "Ω N-36 (30 a 36 Kg/m)"

st.success(f"Perfil recomendado: **{perfil}**")

# -----------------------------
# Tabla de perfiles Omega
# -----------------------------
data = {
    "Perfil": ["Ω N-16.5", "Ω N-21", "Ω N-29", "Ω N-36"],
    "Peso (kg/m)": [16.5, 21, 29, 36],
    "Área (cm²)": [21, 27, 37, 46],
    "Altura total A (mm)": [106, 127, 150, 171],
    "Ancho patín b (mm)": [31, 35, 44, 51],
    "Altura alma H (mm)": [90, 108, 124, 138],
    "Espesor alma g (mm)": [44, 54, 58, 67],
    "Espesor patín c (mm)": [13, 12, 16, 17],
    "Sxx (cm³)": [40, 61, 94, 136],
    "Syy (cm³)": [42, 64, 103, 148],
  
}
df = pd.DataFrame(data)

# Transponer la tabla: que los perfiles sean columnas
df_t = df.set_index("Perfil").T

# Determinar perfiles recomendados
if relacion < 0.7:
    perfiles_recomendados = ["Ω N-29"]
else:
    perfiles_recomendados = ["Ω N-36"]

# Función de estilo para resaltar columnas en lugar de filas
def resaltar_col(col):
    return ['background-color: lightgreen' if col.name in perfiles_recomendados else '' for _ in col]

st.markdown("### Tabla Completa de Perfiles Omega (Transpuesta)")
st.dataframe(
    df_t.style
        .apply(resaltar_col, axis=0)
        .format(precision=2)  # 👉 Limita a 2 decimales
)