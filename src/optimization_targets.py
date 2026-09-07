"""
Optimization targets for the 5-qubit linear chain chip.

Maps each physical quantum parameter to the design variable that controls it,
with proportionality functions encoding the underlying physics.
"""

from typing import List

import names as n
import numpy as np

from qdesignoptimizer.design_analysis_types import OptTarget
from qdesignoptimizer.utils.optimization_targets import (
    get_opt_target_res_kappa_via_coupl_length,
    get_opt_targets_qb_res_transmission,
)


def get_opt_target_res_kappa_feedline(group: int) -> list[OptTarget]:
    """Get kappa optimization target for a resonator's feedline coupling."""
    resonator = n.resonator_for_group(group)
    target = get_opt_target_res_kappa_via_coupl_length(
        resonator=resonator, resonator_coupled_identifier="tee"
    )
    return [target]


def get_opt_targets_5qubits_resonator_coupler(
    groups: List[int],
    opt_target_qubit_freq=False,
    opt_target_qubit_anharm=False,
    opt_target_resonator_freq=False,
    opt_target_resonator_kappa=False,
    opt_target_resonator_qubit_chi=False,
    use_simple_resonator_qubit_chi_relation=False,
    opt_target_coupler_freq=False,
) -> List[OptTarget]:
    """Get optimization targets for the full 5-qubit-resonator system with couplers.

    Args:
        groups: List of qubit-resonator pair numbers (1-5).
        opt_target_qubit_freq: Optimize qubit frequency via Lj.
        opt_target_qubit_anharm: Optimize qubit anharmonicity via pad width.
        opt_target_resonator_freq: Optimize resonator frequency via length.
        opt_target_resonator_kappa: Optimize resonator kappa via coupling length.
        opt_target_resonator_qubit_chi: Optimize qubit-resonator chi.
        use_simple_resonator_qubit_chi_relation: Use simplified chi model.
        opt_target_coupler_freq: Optimize coupler frequency via length.
    """
    opt_targets = []

    # ── Coupler frequency targets (one per coupling edge) ────────────
    if opt_target_coupler_freq:
        for _, _, coupler_mode in n.COUPLING_EDGES:
            opt_target_coupler = OptTarget(
                target_param_type=n.FREQ,
                involved_modes=[coupler_mode],
                design_var=n.design_var_length(coupler_mode),
                design_var_constraint={
                    "larger_than": "50um",
                    "smaller_than": "10000um",
                },
                prop_to=lambda p, v, cm=coupler_mode: 1
                / v[n.design_var_length(cm)],
                independent_target=True,
            )
            opt_targets.append(opt_target_coupler)

    # ── Per-qubit targets (frequency, anharmonicity, resonator, chi, kappa) ─
    for group in groups:
        qubit = n.qubit_for_group(group)
        resonator = n.resonator_for_group(group)

        opt_targets.extend(
            get_opt_targets_qb_res_transmission(
                qubit,
                resonator,
                resonator_coupled_identifier="tee",
                opt_target_qubit_freq=opt_target_qubit_freq,
                opt_target_qubit_anharm=opt_target_qubit_anharm,
                opt_target_resonator_freq=opt_target_resonator_freq,
                opt_target_resonator_kappa=opt_target_resonator_kappa,
                opt_target_resonator_qubit_chi=opt_target_resonator_qubit_chi,
                use_simple_resonator_qubit_chi_relation=use_simple_resonator_qubit_chi_relation,
                design_var_constraint_qubit_width={
                    "larger_than": "1um",
                    "smaller_than": "900um",
                },
                design_var_constraint_res_coupl_length={
                    "larger_than": "1um",
                    "smaller_than": "1500um",
                },
            )
        )

    return opt_targets


def get_opt_target_qubit_T1_limit_via_charge_posx(group: int) -> OptTarget:
    """T1 limit from charge-line proximity (proportional to distance^3)."""
    qubit = n.qubit_for_group(group)
    return OptTarget(
        target_param_type=n.CHARGE_LINE_LIMITED_T1,
        involved_modes=[qubit],
        design_var=n.design_var_cl_pos_x(qubit),
        design_var_constraint={"larger_than": "-1000um", "smaller_than": "-5um"},
        prop_to=lambda p, v, q=qubit: -v[n.design_var_cl_pos_x(q)] ** 3,
        independent_target=True,
    )


def get_opt_targets_qb_charge_line(
    group: int, qb_T1_limit: bool = True
) -> List[OptTarget]:
    opt_targets = []
    if qb_T1_limit:
        opt_targets.append(get_opt_target_qubit_T1_limit_via_charge_posx(group))
    return opt_targets


def get_opt_target_capacitance(group: int) -> List[OptTarget]:
    """Capacitance optimization target for a resonator tee junction."""
    resonator = n.resonator_for_group(group)
    return [
        OptTarget(
            target_param_type=n.CAPACITANCE,
            involved_modes=[
                f"prime_cpw_name_tee_{group}_",
                f"second_cpw_name_tee_{group}_",
            ],
            design_var=n.design_var_length(f"{resonator}_capacitance"),
            design_var_constraint={"larger_than": "1um", "smaller_than": "500um"},
            prop_to=lambda p, v, r=resonator: 1
            / np.sqrt(v[n.design_var_length(f"{r}_capacitance")]),
            independent_target=True,
        )
    ]
