"""
Plot settings for tracking 5-qubit optimization convergence.

Defines plot groups for monitoring frequencies, anharmonicities,
chi values, kappa values, T1 limits, and capacitances across iterations.
"""

import names as n

from qdesignoptimizer.sim_plot_progress import OptPltSet
from qdesignoptimizer.utils.names_parameters import (
    param,
    param_capacitance,
    param_nonlin,
)

# ═══════════════════════════════════════════════════════════════════════════
# SINGLE QUBIT PLOT SETTINGS (for individual qubit-resonator studies)
# ═══════════════════════════════════════════════════════════════════════════

PLOT_SETTINGS_SINGLE_QB = {
    "RES": [
        OptPltSet(
            n.ITERATION, param(n.RESONATOR_1, n.FREQ),
            y_label="RES Freq", unit="GHz",
        ),
        OptPltSet(
            n.ITERATION, param(n.RESONATOR_1, n.KAPPA),
            y_label="RES Kappa", unit="MHz",
        ),
    ],
    "QUBIT": [
        OptPltSet(
            n.ITERATION, param(n.QUBIT_1, n.FREQ),
            y_label="QB Freq", unit="GHz",
        ),
        OptPltSet(
            n.ITERATION, param_nonlin(n.QUBIT_1, n.QUBIT_1),
            y_label="QB Anharm.", unit="MHz",
        ),
    ],
    "COUPLINGS": [
        OptPltSet(
            n.ITERATION, param_nonlin(n.RESONATOR_1, n.QUBIT_1),
            y_label="RES-QB Chi", unit="kHz",
        ),
    ],
}

# ═══════════════════════════════════════════════════════════════════════════
# FULL 5-QUBIT PLOT SETTINGS
# ═══════════════════════════════════════════════════════════════════════════

PLOT_SETTINGS_5QB = {
    "RES FREQ": [
        OptPltSet(
            n.ITERATION,
            [param(r, n.FREQ) for r in n.ALL_RESONATORS],
            y_label="RES Freq", unit="Hz",
        ),
    ],
    "RES KAPPA": [
        OptPltSet(
            n.ITERATION,
            [param(r, n.KAPPA) for r in n.ALL_RESONATORS],
            y_label="RES Kappa", unit="Hz",
        ),
    ],
    "RES KERR": [
        OptPltSet(
            n.ITERATION,
            [param_nonlin(r, r) for r in n.ALL_RESONATORS],
            y_label="RES Kerr", unit="Hz",
        ),
    ],
    "QUBIT FREQ": [
        OptPltSet(
            n.ITERATION,
            [param(q, n.FREQ) for q in n.ALL_QUBITS],
            y_label="QB Freq",
        ),
    ],
    "QUBIT ANHARM": [
        OptPltSet(
            n.ITERATION,
            [param_nonlin(q, q) for q in n.ALL_QUBITS],
            y_label="QB Anharm.",
        ),
    ],
    "QB-RES CHI": [
        OptPltSet(
            n.ITERATION,
            [param_nonlin(q, r) for q, r in zip(n.ALL_QUBITS, n.ALL_RESONATORS)],
            y_label="RES-QB Chi",
        ),
    ],
}

# ═══════════════════════════════════════════════════════════════════════════
# SPECIALIZED PLOT SETTINGS
# ═══════════════════════════════════════════════════════════════════════════

PLOT_SETTINGS_CHARGE_LINE_DECAY = {
    "QUBIT T1": [
        OptPltSet(
            n.ITERATION,
            [param(q, n.CHARGE_LINE_LIMITED_T1) for q in n.ALL_QUBITS],
            y_label="T1 limit", y_scale="log", unit="s",
        ),
    ],
}

PLOT_SETTINGS_RESONATOR_KAPPA = {
    "RESONATOR": [
        OptPltSet(
            n.ITERATION,
            [param(r, n.KAPPA) for r in n.ALL_RESONATORS],
            y_label="RES Kappa", y_scale="log",
        ),
    ],
}

PLOT_SETTINGS_CAPACITANCE = {
    "CAP": [
        OptPltSet(
            n.ITERATION,
            [param_capacitance(f"prime_cpw_name_tee_{g}_", f"second_cpw_name_tee_{g}_")
             for g in n.ALL_GROUPS],
            y_label="Capacitance", unit="fF",
        ),
    ],
}
