import streamlit as st
import math
import statistics
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
from pathlib import Path

# =====================================================
#   TODAS TUS FUNCIONES Y CLASES ORIGINALES – SIN CAMBIOS
# =====================================================

G = 9.81
EPS = 1e-12

def deg_to_rad(angle_deg: float) -> float:
    return math.radians(angle_deg)

def validate_positive(value: float, name: str) -> None:
    if value is None or value <= 0:
        raise ValueError(f"{name} debe ser un número positivo.")

def validate_nonnegative(value: float, name: str) -> None:
    if value is None or value < 0:
        raise ValueError(f"{name} no puede ser negativo.")

def validate_range(value: float, name: str, minimum: float, maximum: float) -> None:
    if value < minimum or value > maximum:
        raise ValueError(f"{name} debe estar entre {minimum} y {maximum}.")

def mean(values: List[float]) -> float:
    if not values:
        raise ValueError("No hay datos para calcular el promedio.")
    return statistics.mean(values)

@dataclass
class CalcResult:
    area: str
    case_name: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    notes: List[str]
    def to_jsonable(self) -> Dict[str, Any]:
        return asdict(self)

# =========================
# Relleno Detrítico
# =========================

class DetricoCalculator:
    @staticmethod
    def rankine_ka(phi_deg: float) -> float:
        validate_range(phi_deg, "Ángulo φ", 0, 89.9)
        phi = deg_to_rad(phi_deg)
        return math.tan(math.radians(45) - phi/2)**2

    @staticmethod
    def rankine_kp(phi_deg: float) -> float:
        validate_range(phi_deg, "Ángulo φ", 0, 89.9)
        phi = deg_to_rad(phi_deg)
        return math.tan(math.radians(45) + phi/2)**2

    @staticmethod
    def lateral_pressure(ka: float, gamma: float, H: float) -> float:
        validate_positive(ka,"Ka")
        validate_positive(gamma,"γ")
        validate_positive(H,"H")
        return ka * gamma * H

    @staticmethod
    def resultant_thrust(ka: float, gamma: float, H: float) -> float:
        validate_positive(ka,"Ka")
        validate_positive(gamma,"γ")
        validate_positive(H,"H")
        return 0.5 * ka * gamma * H**2

    @staticmethod
    def marston_vertical_stress(gamma, B, H, K, mu):
        validate_positive(gamma,"γ")
        validate_positive(B,"B")
        validate_positive(H,"H")
        validate_positive(K,"K")
        validate_positive(mu,"μ")
        exponent = -2*K*mu*H/B
        return (gamma*B / (2*K*mu)) * (1 - math.exp(exponent))

    @staticmethod
    def svakugan_vertical_stress(gamma,H,B,K,mu):
        validate_positive(gamma,"γ")
        validate_positive(H,"H")
        validate_positive(B,"B")
        validate_positive(K,"K")
        validate_positive(mu,"μ")
        exponent = -2*K*mu*H/B
        return gamma*H*math.exp(exponent)

    @staticmethod
    def hazen_permeability(D10_mm: float) -> float:
        validate_positive(D10_mm,"D10")
        return 200 * D10_mm**2

    @staticmethod
    def usbm_permeability(VR: float, X: float) -> float:
        validate_positive(VR,"VR")
        validate_positive(X,"X")
        return math.exp(11.391 + 2.853 * math.log(VR * X))

    @staticmethod
    def crf_required_ucs_yu_counter(gamma_mn_m3, H):
        validate_positive(gamma_mn_m3,"γ")
        validate_positive(H,"H")
        return 2.5 * gamma_mn_m3 * H

    @staticmethod
    def mitchell_wedge_ucs(gamma,B,H,D,phi):
        validate_positive(gamma,"γ")
        validate_positive(B,"B")
        validate_positive(H,"H")
        validate_nonnegative(D,"D")
        validate_range(phi,"φ",0,89.9)

        alpha = 45 + phi/2
        tan_alpha = math.tan(deg_to_rad(alpha))
        D_max = H / max(tan_alpha, EPS)
        D_eff = min(D, D_max)

        num = gamma*B*(H - (D_eff/2)*tan_alpha)
        den = (H - (D_eff/2)*tan_alpha) + B*tan_alpha
        if abs(den)<EPS: raise ZeroDivisionError("Denominador nulo")
        return num/den

    @staticmethod
    def potvin_phi_zero_ucs(gamma,B,H,D):
        validate_positive(gamma,"γ")
        validate_positive(B,"B")
        validate_positive(H,"H")
        validate_nonnegative(D,"D")
        denom = 2*H + 2*B - D
        if abs(denom)<EPS: raise ZeroDivisionError("Denominador nulo")
        return gamma*B*(2*H - D)/denom

    @staticmethod
    def roof_beam_ucs(gamma,L,t,fs=1.5):
        validate_positive(gamma,"γ")
        validate_positive(L,"L")
        validate_positive(t,"t")
        validate_positive(fs,"FS")
        return (3*gamma*L**2/(4*t**2))*fs

# =========================
# Hidráulico
# =========================

class HidraulicoCalculator:
    @staticmethod
    def solids_volume_fraction(Cw, SGm, SGs):
        validate_range(Cw,"Cw",0,100)
        validate_positive(SGm,"SGm")
        validate_positive(SGs,"SGs")
        Cv = (Cw/100)*(SGm/SGs)
        return Cv*100

    @staticmethod
    def wellman_viscosity(mu, Cv):
        validate_positive(mu,"μ")
        validate_range(Cv,"Cv",0,61.9)
        Cv2 = Cv/100
        return mu*math.exp(-10.4*Cv2) / ((1 - (Cv2/0.62))**8)

    @staticmethod
    def hydraulic_required_ucs_simple(gamma,W,H):
        validate_positive(gamma,"γ")
        validate_positive(W,"W")
        validate_positive(H,"H")
        return (0.36 if W>=H else 0.45) * gamma * H

# =========================
# Pasta
# =========================

class PastaCalculator:
    @staticmethod
    def ucs_required_free_standing(gamma,H,fs=1.0):
        validate_positive(gamma,"γ")
        validate_positive(H,"H")
        validate_positive(fs,"FS")
        return 0.5 * gamma * H * fs

# ==================================================================================
# STREAMLIT INTERFAZ (AQUÍ SOLO CAMBIA EL FRONTEND, TODO EL BACKEND SE CONSERVA)
# ==================================================================================

st.title("Calculadora Completa de Rellenos Mineros")
tabs = st.tabs(["Relleno Detrítico", "Relleno Hidráulico", "Relleno en Pasta"])

# =========================
# TAB 1 – DETRÍTICO
# =========================

with tabs[0]:
    st.header("Cálculos para Relleno Detrítico")

    phi = st.number_input("Ángulo φ (°)", 0.1, 89.9, 35.0)
    gamma = st.number_input("Peso unitario γ (kN/m³)", 1.0, 40.0, 20.0)
    H = st.number_input("Altura H (m)", 0.1, 100.0, 10.0)

    if st.button("Calcular Rankine"):
        ka = DetricoCalculator.rankine_ka(phi)
        kp = DetricoCalculator.rankine_kp(phi)
        P = DetricoCalculator.lateral_pressure(ka, gamma, H)
        E = DetricoCalculator.resultant_thrust(ka, gamma, H)

        st.success("Cálculo completado")
        st.json({
            "Ka": ka,
            "Kp": kp,
            "Presión lateral (kPa)": P,
            "Empuje resultante (kN/m)": E
        })

# =========================
# TAB 2 – HIDRÁULICO
# =========================

with tabs[1]:
    st.header("Cálculos para Relleno Hidráulico")

    Cw = st.number_input("Contenido sólido en peso (Cw%)", 1.0, 80.0, 50.0)
    SGm = st.number_input("SGm pulpa", 1.1, 3.5, 1.5)
    SGs = st.number_input("SGs sólidos", 1.5, 5.0, 2.7)

    if st.button("Calcular Fracción Volumétrica"):
        Cv = HidraulicoCalculator.solids_volume_fraction(Cw, SGm, SGs)
        st.info(f"Cv = {Cv:.2f} %")

# =========================
# TAB 3 – PASTA
# =========================

with tabs[2]:
    st.header("Cálculos para Relleno en Pasta")

    gamma = st.number_input("Peso unitario γ (kN/m³)", 1.0, 40.0, 18.0, key="g_p")
    H = st.number_input("Altura libre (m)", 0.1, 50.0, 10.0, key="H_p")

    if st.button("Calcular UCS mínimo"):
        ucs = PastaCalculator.ucs_required_free_standing(gamma, H)
        st.success(f"UCS requerido = {ucs:.2f} kPa")