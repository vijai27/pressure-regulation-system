# control/eos.py — Peng-Robinson EOS for pure CO₂ (Bone Dry, ≥99.8% purity)
#
# Used in simulator to replace ideal-gas thermal coupling with real CO₂ physics.
# Key function: dP_from_dT() — pressure change at constant vessel volume when
# temperature changes.  At 20+ MPa, CO₂ is ~20–30% stiffer than ideal gas predicts.
#
# CO₂ critical point:  Tc = 304.13 K (31.0°C),  Pc = 7.3773 MPa
# All pressures in MPa, temperatures in K, volumes in m³, moles in mol.

import math
import numpy as np

# ── CO₂ parameters ────────────────────────────────────────────────────────────
TC    = 304.13       # K     critical temperature
PC    = 7.3773       # MPa   critical pressure
OMEGA = 0.22394      # –     acentric factor
M_CO2 = 0.04401      # kg/mol molar mass

R = 8.314462e-6      # MPa·m³/(mol·K)

# ── PR-EOS constants (computed once at import) ────────────────────────────────
_kappa = 0.37464 + 1.54226 * OMEGA - 0.26992 * OMEGA**2    # = 0.70646
_a0    = 0.45724 * R**2 * TC**2 / PC                        # MPa·m⁶/mol²
_b     = 0.07780 * R * TC / PC                              # m³/mol  ≈ 2.664e-5


# ── Private helpers ───────────────────────────────────────────────────────────

def _alpha(T_K: float) -> float:
    return (1.0 + _kappa * (1.0 - math.sqrt(T_K / TC))) ** 2


def _a(T_K: float) -> float:
    return _a0 * _alpha(T_K)


def _da_dT(T_K: float) -> float:
    """Analytical derivative d[a(T)]/dT  [MPa·m⁶/(mol²·K)]."""
    sqrt_Tr = math.sqrt(T_K / TC)
    return -_a0 * _kappa * (1.0 + _kappa * (1.0 - sqrt_Tr)) / math.sqrt(TC * T_K)


# ── Public API ────────────────────────────────────────────────────────────────

def compressibility(P_MPa: float, T_K: float) -> float:
    """
    Compressibility factor Z for CO₂ at (P, T).

    Solves the PR-EOS cubic equation and returns the largest real root,
    which is correct for gas-phase and supercritical CO₂ (our operating
    regime: T ≥ 60°C > Tc = 31°C for all pressurization steps).
    Falls back to Z = 1 (ideal gas) if the solver finds no valid root.
    """
    if P_MPa <= 0.0 or T_K <= 0.0:
        return 1.0

    aT = _a(T_K)
    RT = R * T_K
    A  = aT * P_MPa / RT**2
    B  = _b  * P_MPa / RT

    # Z³ - (1-B)·Z² + (A-3B²-2B)·Z - (AB-B²-B³) = 0
    coeffs = [
        1.0,
        -(1.0 - B),
        A - 3.0*B**2 - 2.0*B,
        -(A*B - B**2 - B**3),
    ]
    roots = np.roots(coeffs)
    real_roots = [r.real for r in roots if abs(r.imag) < 1e-6 and r.real > B + 1e-8]
    return max(real_roots) if real_roots else 1.0


def pressure_from_molar_density(c_mol_m3: float, T_K: float) -> float:
    """
    P [MPa] from molar density c = n/V [mol/m³] and temperature T [K].
    Used to track vessel pressure as moles accumulate.
    """
    if c_mol_m3 <= 0.0:
        return 0.0
    V   = 1.0 / c_mol_m3
    aT  = _a(T_K)
    RT  = R * T_K
    denom = V - _b
    if denom <= 1e-10:
        denom = 1e-10
    P = RT / denom - aT / (V * (V + _b) + _b * (V - _b))
    return max(P, 0.0)


def molar_density_from_pressure(P_MPa: float, T_K: float) -> float:
    """
    Molar density c = n/V [mol/m³] from P [MPa] and T [K].
    Used to initialise the vessel mass at startup.
    """
    if P_MPa <= 0.0:
        return 0.0
    Z  = compressibility(P_MPa, T_K)
    V  = Z * R * T_K / P_MPa
    return 1.0 / V


def dP_from_dT(P_MPa: float, T_K: float, dT_K: float) -> float:
    """
    Pressure change [MPa] caused by a temperature shift dT_K [K] at *constant
    vessel volume* (no mass added or removed).

    Uses the exact PR-EOS isochoric derivative:
        (∂P/∂T)_V = R/(V–b) – [da/dT] / [V(V+b)+b(V–b)]

    The ideal-gas approximation (P/T) underestimates this by 20–30% at 20 MPa,
    60°C — the regime where temperature stability matters most for the hold phase.
    """
    if P_MPa <= 0.0 or T_K <= 0.0 or dT_K == 0.0:
        return 0.0

    Z   = compressibility(P_MPa, T_K)
    V   = Z * R * T_K / P_MPa      # molar volume [m³/mol]
    aT  = _a(T_K)
    daT = _da_dT(T_K)
    b   = _b

    denom = V - b
    if denom <= 1e-10:
        denom = 1e-10

    dP_dT = R / denom - daT / (V * (V + b) + b * (V - b))
    return dP_dT * dT_K
