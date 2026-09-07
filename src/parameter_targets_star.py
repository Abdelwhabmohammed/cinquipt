"""
Target quantum parameters for the 5-qubit star/hub chip.
Same frequency targets as the linear chain — the physics targets
are topology-independent; only the layout differs.
"""

import names_star as n

from qdesignoptimizer.utils.names_parameters import (
    param,
    param_capacitance,
    param_nonlin,
)

PARAM_TARGETS = {
    # ── Qubit frequencies (staggered 4.0 – 5.2 GHz) ─────────────────────
    param(n.QUBIT_1, n.FREQ): 4.0e9,
    param(n.QUBIT_2, n.FREQ): 4.3e9,
    param(n.QUBIT_3, n.FREQ): 4.6e9,
    param(n.QUBIT_4, n.FREQ): 4.9e9,
    param(n.QUBIT_5, n.FREQ): 5.2e9,

    # ── Resonator frequencies (staggered 6.0 – 7.2 GHz) ─────────────────
    param(n.RESONATOR_1, n.FREQ): 6.0e9,
    param(n.RESONATOR_2, n.FREQ): 6.3e9,
    param(n.RESONATOR_3, n.FREQ): 6.6e9,
    param(n.RESONATOR_4, n.FREQ): 6.9e9,
    param(n.RESONATOR_5, n.FREQ): 7.2e9,

    # ── Coupler frequencies (star: 4 couplers from hub Q3) ───────────────
    param(n.COUPLER_13, n.FREQ): 8.5e9,
    param(n.COUPLER_23, n.FREQ): 8.7e9,
    param(n.COUPLER_34, n.FREQ): 8.9e9,
    param(n.COUPLER_35, n.FREQ): 9.1e9,

    # ── Qubit anharmonicities (self-Kerr, 200–220 MHz) ───────────────────
    param_nonlin(n.QUBIT_1, n.QUBIT_1): 220e6,
    param_nonlin(n.QUBIT_2, n.QUBIT_2): 215e6,
    param_nonlin(n.QUBIT_3, n.QUBIT_3): 210e6,
    param_nonlin(n.QUBIT_4, n.QUBIT_4): 205e6,
    param_nonlin(n.QUBIT_5, n.QUBIT_5): 200e6,

    # ── Qubit-resonator dispersive shift (chi ≈ 1 MHz) ───────────────────
    param_nonlin(n.QUBIT_1, n.RESONATOR_1): 1.0e6,
    param_nonlin(n.QUBIT_2, n.RESONATOR_2): 1.0e6,
    param_nonlin(n.QUBIT_3, n.RESONATOR_3): 1.0e6,
    param_nonlin(n.QUBIT_4, n.RESONATOR_4): 1.0e6,
    param_nonlin(n.QUBIT_5, n.RESONATOR_5): 1.0e6,

    # ── Resonator decay rate (kappa ≈ 1 MHz) ─────────────────────────────
    param(n.RESONATOR_1, n.KAPPA): 1.0e6,
    param(n.RESONATOR_2, n.KAPPA): 1.0e6,
    param(n.RESONATOR_3, n.KAPPA): 1.0e6,
    param(n.RESONATOR_4, n.KAPPA): 1.0e6,
    param(n.RESONATOR_5, n.KAPPA): 1.0e6,

    # ── Charge-line limited T1 (≥ 20 ms) ─────────────────────────────────
    param(n.QUBIT_1, n.CHARGE_LINE_LIMITED_T1): 20e-3,
    param(n.QUBIT_2, n.CHARGE_LINE_LIMITED_T1): 20e-3,
    param(n.QUBIT_3, n.CHARGE_LINE_LIMITED_T1): 20e-3,
    param(n.QUBIT_4, n.CHARGE_LINE_LIMITED_T1): 20e-3,
    param(n.QUBIT_5, n.CHARGE_LINE_LIMITED_T1): 20e-3,

    # ── Resonator-feedline capacitance ────────────────────────────────────
    param_capacitance("prime_cpw_name_tee_1_", "second_cpw_name_tee_1_"): -3,
    param_capacitance("prime_cpw_name_tee_2_", "second_cpw_name_tee_2_"): -3,
    param_capacitance("prime_cpw_name_tee_3_", "second_cpw_name_tee_3_"): -3,
    param_capacitance("prime_cpw_name_tee_4_", "second_cpw_name_tee_4_"): -3,
    param_capacitance("prime_cpw_name_tee_5_", "second_cpw_name_tee_5_"): -3,
}
