import tkinter as tk
from tkinter import messagebox
import math
import pandas as pd
import tksheet

# -----------------------------
# Datos de perfiles Omega
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
df_t = df.set_index("Perfil").T  # transpuesta

# -----------------------------
# Diccionarios de Kt y Kf
# -----------------------------
opciones_Kt = {
    1: "Materiales solidificados como anhidrita o concreto fluido",
    2: "Cuñas de madera",
    3: "Relleno a mano"
}
opciones_Kf = {
    1: "Arenisca",
    2: "Lutita arenosa",
    3: "Lutita",
    4: "Roca muy deformada",
    5: "Carbón",
    6: "Carbón + Lutita + roca deformada"
}

# -----------------------------
# Ventanas emergentes de ayuda
# -----------------------------
def mostrar_info_kt():
    texto = "\n".join([f"{k}: {v}" for k, v in opciones_Kt.items()])
    messagebox.showinfo("Coeficientes Kt", texto)

def mostrar_info_kf():
    texto = "\n".join([f"{k}: {v}" for k, v in opciones_Kf.items()])
    messagebox.showinfo("Coeficientes Kf", texto)

# -----------------------------
# Función de cálculo
# -----------------------------
def calcular():
    try:
        H = float(entry_H.get())
        m = float(entry_m.get())
        Kt = int(var_Kt.get())
        Kf = int(var_Kf.get())

        # Cálculos
        K = -78 + (0.666 * (H / 10)) + (4.3 * m * Kt) + (7.7 * math.sqrt(10 * Kf))
        Kp = -58 + (0.039 * H) + (3.7 * m * Kt) + (6.6 * math.sqrt(10 * Kf))
        Y = 3.5 + 0.23 * K
        relacion = Kp / K if K != 0 else 0

        # Mostrar resultados
        lbl_res.config(text=(
            f"Convergencia final (K): {K:.2f} %\n"
            f"Expansión del suelo-roca (K′): {Kp:.2f} %\n"
            f"Cierre de los lados (Y): {Y:.2f} %\n"
            f"Relación K′/K: {relacion:.2f}"
        ))

        # Selección de perfil recomendado
        if relacion < 0.7:
            recomendado = "Ω N-29"
            perfil = "Ω N-29 (26 a 29 Kg/m)"
        else:
            recomendado = "Ω N-36"
            perfil = "Ω N-36 (30 a 36 Kg/m)"

        # Mostrar resultado en cuadro resaltado
        lbl_perfil.config(text=f"Perfil recomendado: {perfil}", bg="lightgreen")

        # Limpiar colores anteriores
        sheet.highlight_cells(row="all", column="all", bg="white")

        # Resaltar columna recomendada
        col_index = list(df_t.columns).index(recomendado)
        sheet.highlight_cells(row="all", column=col_index, bg="lightgreen")

    except Exception as e:
        lbl_perfil.config(text=f"Error: {e}", bg="red")

# -----------------------------
# Función Refresh (limpia entradas y resultados)
# -----------------------------
def refresh_inputs():
    entry_H.delete(0, tk.END)
    entry_m.delete(0, tk.END)
    var_Kt.set("1")   # valor por defecto
    var_Kf.set("1")   # valor por defecto
    lbl_res.config(text="")
    lbl_perfil.config(text="", bg=root.cget("bg"))

# -----------------------------
# Interfaz Tkinter
# -----------------------------
root = tk.Tk()
root.title("Diseño de Cimbras Cedentes (Ω)")
root.geometry("670x710")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill="x")

# Entradas
tk.Label(frame, text="Profundidad de la mina (H) [m]:").grid(row=0, column=0, sticky="w")
entry_H = tk.Entry(frame, width=10)
entry_H.insert(0, "370")
entry_H.grid(row=0, column=1)

tk.Label(frame, text="Espesor del manto (m) [m]:").grid(row=1, column=0, sticky="w")
entry_m = tk.Entry(frame, width=10)
entry_m.insert(0, "10")
entry_m.grid(row=1, column=1)

# Selector Kt + Botón ?
tk.Label(frame, text="Coeficiente Kt:").grid(row=2, column=0, sticky="w")
var_Kt = tk.StringVar(value="1")
menu_Kt = tk.OptionMenu(frame, var_Kt, *opciones_Kt.keys())
menu_Kt.config(width=8, font=("Arial", 10, "bold"), bg="lightgray")
menu_Kt.grid(row=2, column=1)

btn_info_kt = tk.Button(frame, text="?", command=mostrar_info_kt, width=2, bg="lightblue")
btn_info_kt.grid(row=2, column=2, padx=5)

# Selector Kf + Botón ?
tk.Label(frame, text="Coeficiente Kf:").grid(row=3, column=0, sticky="w")
var_Kf = tk.StringVar(value="1")
menu_Kf = tk.OptionMenu(frame, var_Kf, *opciones_Kf.keys())
menu_Kf.config(width=8, font=("Arial", 10, "bold"), bg="lightgray")
menu_Kf.grid(row=3, column=1)

btn_info_kf = tk.Button(frame, text="?", command=mostrar_info_kf, width=2, bg="lightblue")
btn_info_kf.grid(row=3, column=2, padx=5)

# Botón Calcular y Refresh en la misma fila
btn = tk.Button(frame, text="Calcular", command=calcular, bg="lightblue", font=("Arial", 11, "bold"))
btn.grid(row=4, column=0, pady=10)

refresh_button = tk.Button(frame, text="Refresh Datos", command=refresh_inputs, font=("Arial", 11), bg="lightgrey")
refresh_button.grid(row=4, column=1, padx=10, pady=10)

# Resultados (espacio fijo para que no empuje la tabla)
lbl_res = tk.Label(frame, text="", justify="left", fg="blue", width=50, height=5, anchor="w")
lbl_res.grid(row=5, column=0, columnspan=3, sticky="w")

# Respuesta en cuadro resaltado (espacio fijo también)
lbl_perfil = tk.Label(frame, text="", font=("Arial", 12, "bold"), pady=5, width=50, height=2)
lbl_perfil.grid(row=6, column=0, columnspan=3, sticky="we", pady=10)

# -----------------------------
# Tabla con tksheet
# -----------------------------
sheet_frame = tk.Frame(root)
sheet_frame.pack(fill="both", expand=True, padx=10, pady=10)

sheet = tksheet.Sheet(
    sheet_frame,
    data=df_t.round(2).values.tolist(),
    headers=df_t.columns.tolist(),
    row_index=df_t.index.tolist()
)
sheet.enable_bindings(("single_select", "column_select", "row_select",
                       "row_width_resize", "column_width_resize",
                       "copy", "cut", "paste"))
sheet.pack(fill="both", expand=True)

sheet.index_align = "w"
sheet.set_index_width(250)  # ancho índice
sheet.set_column_widths([100] * len(df_t.columns))

root.mainloop()