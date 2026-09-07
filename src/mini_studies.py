"""
HFSS mini-study configurations for the 5-qubit linear chain chip.

Defines which components to include in each simulation subsystem,
port configurations, junction setups, and convergence criteria.
"""

from typing import Optional

import names as n
import numpy as np
import parameter_targets as pt

from qdesignoptimizer.design_analysis_types import MiniStudy, SurfaceProperties
from qdesignoptimizer.sim_capacitance_matrix import (
    CapacitanceMatrixStudy,
    ModeDecayIntoChargeLineStudy,
    ResonatorDecayIntoWaveguideStudy,
)
from qdesignoptimizer.utils.names_design_variables import junction_setup
from qdesignoptimizer.utils.names_parameters import FREQ, param

CONVERGENCE = dict(nbr_passes=7, delta_f=0.03)


def get_mini_study_qb_res(
    group: int, surface_properties: Optional[SurfaceProperties] = None
):
    """Single qubit + resonator eigenmode study (lightweight)."""
    qubit = n.qubit_for_group(group)
    resonator = n.resonator_for_group(group)

    return MiniStudy(
        qiskit_component_names=[
            n.name_mode(qubit),
            n.name_mode(resonator),
            n.name_tee(group),
        ],
        port_list=[
            (n.name_tee(group), "prime_end", 50),
            (n.name_tee(group), "prime_start", 50),
        ],
        open_pins=[],
        modes=[qubit, resonator],
        jj_setup={**junction_setup(qubit)},
        design_name=f"get_mini_study_qb_res_{group}",
        adjustment_rate=1,
        build_fine_mesh=True,
        **CONVERGENCE,
        surface_properties=surface_properties,
    )


def get_mini_study_5qb_resonator_coupler():
    """Full 5-qubit eigenmode study (5 qubits + 5 resonators + 4 couplers = 14 modes).

    WARNING: This is a very heavy simulation. Consider using partitioned
    studies for tractable computation.
    """
    all_comps = []
    all_ports = []
    all_modes = []
    all_jjs = {}

    for group in n.ALL_GROUPS:
        qubit = n.qubit_for_group(group)
        resonator = n.resonator_for_group(group)
        all_comps.extend([
            n.name_mode(qubit),
            n.name_mode(resonator),
            n.name_tee(group),
        ])
        all_ports.extend([
            (n.name_tee(group), "prime_end", 50),
            (n.name_tee(group), "prime_start", 50),
        ])
        all_modes.extend([qubit, resonator])
        all_jjs.update(junction_setup(qubit))

    # Add all coupler components and modes
    for _, _, coupler in n.COUPLING_EDGES:
        all_comps.append(n.name_mode(coupler))
        all_modes.append(coupler)

    # Sort modes by target frequency for correct eigenmode ordering
    all_mode_freq = [pt.PARAM_TARGETS[param(m, FREQ)] for m in all_modes]
    all_modes_sorted = [all_modes[i] for i in np.argsort(all_mode_freq)]

    return MiniStudy(
        qiskit_component_names=all_comps,
        port_list=all_ports,
        open_pins=[],
        modes=all_modes_sorted,
        jj_setup=all_jjs,
        design_name="get_mini_study_5qb_resonator_coupler",
        adjustment_rate=1,
        cos_trunc=8,
        fock_trunc=7,
        build_fine_mesh=False,
        **CONVERGENCE,
    )


def get_mini_study_qb_charge_line(group: int):
    """Capacitance study for charge-line decay (T1 limit)."""
    qubit = n.qubit_for_group(group)
    qiskit_component_names = [
        n.name_mode(qubit),
        n.name_charge_line(group),
    ]
    charge_decay_study = ModeDecayIntoChargeLineStudy(
        mode=qubit,
        mode_freq_GHz=pt.PARAM_TARGETS[param(qubit, FREQ)] / 1e9,
        mode_capacitance_name=[
            "pad_bot_" + n.name_mode(qubit),
            "pad_top_" + n.name_mode(qubit),
        ],
        charge_line_capacitance_name="trace_" + n.name_charge_line(group),
        charge_line_impedance_Ohm=50,
        qiskit_component_names=qiskit_component_names,
        open_pins=[
            (n.name_mode(qubit), "readout"),
            (n.name_mode(qubit), "coupler"),
            (n.name_charge_line(group), "start"),
            (n.name_charge_line(group), "end"),
        ],
        ground_plane_capacitance_name="ground_main_plane",
        nbr_passes=8,
    )
    return MiniStudy(
        qiskit_component_names=qiskit_component_names,
        port_list=[],
        open_pins=[],
        modes=[qubit],
        jj_setup={**junction_setup(n.name_mode(qubit))},
        design_name=f"get_mini_study_qb_charge_line_{group}",
        adjustment_rate=1,
        capacitance_matrix_studies=[charge_decay_study],
        run_capacitance_studies_only=True,
        **CONVERGENCE,
    )


def get_mini_study_res_feedline(group: int):
    """Capacitance study for resonator decay into waveguide (kappa)."""
    resonator = n.resonator_for_group(group)
    qiskit_component_names = [
        n.name_mode(resonator),
        n.name_tee(group),
    ]
    resonator_decay_study = ResonatorDecayIntoWaveguideStudy(
        mode=resonator,
        mode_freq_GHz=pt.PARAM_TARGETS[param(resonator, FREQ)] / 1e9,
        resonator_name=f"second_cpw_name_tee_{group}_",
        waveguide_name=f"prime_cpw_name_tee_{group}_",
        impedance_ohm=50,
        resonator_type="lambda_4",
        qiskit_component_names=qiskit_component_names,
        open_pins=[
            (n.name_mode(resonator), "start"),
            (n.name_mode(resonator), "end"),
            (n.name_tee(group), "prime_end"),
            (n.name_tee(group), "prime_start"),
        ],
        nbr_passes=8,
        render_qiskit_metal_kwargs={"capacitance_or_surface_p_ratio": True},
    )
    return MiniStudy(
        qiskit_component_names=qiskit_component_names,
        port_list=[],
        open_pins=[],
        modes=[resonator],
        jj_setup={},
        design_name=f"get_mini_study_res_feedline_{group}",
        adjustment_rate=1,
        capacitance_matrix_studies=[resonator_decay_study],
        run_capacitance_studies_only=True,
        **CONVERGENCE,
    )


def get_mini_study_resonator_capacitance(group: int):
    """Pure capacitance matrix study for a resonator tee junction."""
    resonator = n.resonator_for_group(group)
    qiskit_component_names = [n.name_mode(resonator), n.name_tee(group)]
    cap_study = CapacitanceMatrixStudy(
        qiskit_component_names=qiskit_component_names,
        open_pins=[
            (n.name_mode(resonator), "end"),
            (n.name_mode(resonator), "start"),
            (n.name_tee(group), "prime_end"),
            (n.name_tee(group), "prime_start"),
        ],
        nbr_passes=8,
        render_qiskit_metal_kwargs={"capacitance_or_surface_p_ratio": True},
    )
    return MiniStudy(
        qiskit_component_names=qiskit_component_names,
        port_list=[],
        open_pins=[],
        modes=[],
        jj_setup={},
        design_name=f"get_mini_study_capacitance_{group}",
        hfss_wire_bond_size=3,
        capacitance_matrix_studies=[cap_study],
        **CONVERGENCE,
    )
