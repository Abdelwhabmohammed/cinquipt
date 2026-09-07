"""
Physical chip layout for a 5-qubit star/hub topology.

Topology B — Star: Q3 at center, Q1/Q2 below-left/right, Q4/Q5 above-left/right.
All couplers radiate from Q3 to the 4 peripheral qubits.

Uses TransmonPocket as the qubit component.
"""

import names_star as n
from qiskit_metal.designs.design_planar import DesignPlanar
from qiskit_metal.qlibrary.couplers.coupled_line_tee import CoupledLineTee
from qiskit_metal.qlibrary.qubits.transmon_pocket import TransmonPocket
from qiskit_metal.qlibrary.terminations.launchpad_wb import LaunchpadWirebond
from qiskit_metal.qlibrary.terminations.open_to_ground import OpenToGround
from qiskit_metal.qlibrary.tlines.meandered import RouteMeander
from qiskit_metal.qlibrary.tlines.pathfinder import RoutePathfinder

from qdesignoptimizer.utils.chip_generation import ChipType
from qdesignoptimizer.utils.utils import sum_expression

# ═══════════════════════════════════════════════════════════════════════════
# DESIGN CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

LINE_50_OHM_WIDTH = "16.51um"
LINE_50_OHM_GAP = "10um"
RESONATOR_WIDTH = "20um"
RESONATOR_GAP = "20um"
BEND_RADIUS = "99um"

# Star topology uses a 12×12 mm chip (more compact, qubits radiate from center)
chip_type = ChipType(
    size_x="12mm",
    size_y="12mm",
    size_z="-300um",
    material="silicon",
)

# ── Qubit placement (star / cross pattern) ───────────────────────────────
# Q3 at center (0,0); Q1, Q2 below; Q4, Q5 above
# Peripheral qubits at ~2.5mm from center in a cross pattern
QUBIT_POSITIONS = {
    n.NBR_1: {"pos_x": "-2.5mm", "pos_y": "-2.5mm", "orientation": "0"},    # bottom-left
    n.NBR_2: {"pos_x": "2.5mm",  "pos_y": "-2.5mm", "orientation": "180"},   # bottom-right
    n.NBR_3: {"pos_x": "0.0mm",  "pos_y": "0.0mm",  "orientation": "0"},     # center (hub)
    n.NBR_4: {"pos_x": "-2.5mm", "pos_y": "2.5mm",  "orientation": "0"},     # top-left
    n.NBR_5: {"pos_x": "2.5mm",  "pos_y": "2.5mm",  "orientation": "180"},   # top-right
}

# Resonator tees arranged around the periphery
TEE_POSITIONS = {
    n.NBR_1: {"pos_x": "-4.5mm", "pos_y": "-2.5mm", "orientation": "0"},
    n.NBR_2: {"pos_x": "4.5mm",  "pos_y": "-2.5mm", "orientation": "180"},
    n.NBR_3: {"pos_x": "0.0mm",  "pos_y": "-4.0mm", "orientation": "-90"},   # hub res below
    n.NBR_4: {"pos_x": "-4.5mm", "pos_y": "2.5mm",  "orientation": "0"},
    n.NBR_5: {"pos_x": "4.5mm",  "pos_y": "2.5mm",  "orientation": "180"},
}


# ═══════════════════════════════════════════════════════════════════════════
# COMPONENT BUILDERS
# ═══════════════════════════════════════════════════════════════════════════

def add_transmon_plus_resonator(design: DesignPlanar, group: int):
    """Place one transmon qubit + its readout resonator + tee coupling."""
    qubit = n.qubit_for_group(group)
    resonator = n.resonator_for_group(group)
    pos = QUBIT_POSITIONS[group]
    tee_pos = TEE_POSITIONS[group]

    transmon_options = dict(
        pos_x=pos["pos_x"],
        pos_y=pos["pos_y"],
        orientation=pos["orientation"],
        pad_gap="30um",
        inductor_width="20um",
        pad_width=n.design_var_width(qubit),
        pad_height="90um",
        pocket_width="650um",
        pocket_height="650um",
        connection_pads=dict(
            readout=dict(
                loc_W=0,
                loc_H=+1,
                pad_gap="120um",
                pad_gap_w="0um",
                pad_width=n.design_var_coupl_length(resonator, qubit),
                pad_height="40um",
                cpw_width=RESONATOR_WIDTH,
                cpw_gap=RESONATOR_GAP,
                cpw_extend="300um",
                pocket_extent="5um",
            ),
            coupler=dict(
                loc_W=0,
                loc_H=-1,
                pad_gap="100um",
                pad_gap_w="0um",
                pad_width="40um",
                pad_height="170um",
                cpw_width=RESONATOR_WIDTH,
                cpw_gap=RESONATOR_GAP,
                cpw_extend="0.0um",
                pocket_extent="5um",
            ),
        ),
        gds_cell_name=f"Manhattan_{group}",
        hfss_inductance=n.design_var_lj(qubit),
        hfss_capacitance=n.design_var_cj(qubit),
    )

    qub = TransmonPocket(design, n.name_mode(qubit), options=transmon_options)

    cltee_options = dict(
        pos_x=tee_pos["pos_x"],
        pos_y=tee_pos["pos_y"],
        orientation=tee_pos["orientation"],
        second_width=RESONATOR_WIDTH,
        second_gap=RESONATOR_GAP,
        prime_width=LINE_50_OHM_WIDTH,
        prime_gap=LINE_50_OHM_GAP,
        coupling_space=n.design_var_length(f"{resonator}_capacitance"),
        fillet=BEND_RADIUS,
        coupling_length=n.design_var_coupl_length(resonator, "tee"),
    )

    cltee = CoupledLineTee(design, n.name_tee(group), options=cltee_options)

    resonator_options = dict(
        pin_inputs=dict(
            start_pin=dict(component=qub.name, pin="readout"),
            end_pin=dict(component=cltee.name, pin="second_end"),
        ),
        fillet=BEND_RADIUS,
        hfss_wire_bonds=True,
        total_length=n.design_var_length(resonator),
        lead=dict(start_straight="600um", end_straight="100um"),
        trace_width=RESONATOR_WIDTH,
        trace_gap=RESONATOR_GAP,
        meander=dict(spacing="200um"),
    )

    RouteMeander(design, n.name_mode(resonator), options=resonator_options)


def add_coupler(design: DesignPlanar, qubit_a_mode, qubit_b_mode, coupler_mode):
    """Route a coupler between two qubits' 'coupler' pads."""
    coupler_options = dict(
        pin_inputs=dict(
            start_pin=dict(component=n.name_mode(qubit_a_mode), pin="coupler"),
            end_pin=dict(component=n.name_mode(qubit_b_mode), pin="coupler"),
        ),
        fillet=BEND_RADIUS,
        hfss_wire_bonds=True,
        total_length=n.design_var_length(coupler_mode),
        lead=dict(start_straight="200um", end_straight="200um"),
        trace_width=RESONATOR_WIDTH,
        trace_gap=RESONATOR_GAP,
        meander=dict(spacing="200um"),
    )

    RouteMeander(design, n.name_mode(coupler_mode), options=coupler_options)


def add_all_couplers(design: DesignPlanar):
    """Add all 4 star-topology couplers (all radiate from Q3 hub)."""
    for qubit_a, qubit_b, coupler in n.COUPLING_EDGES:
        add_coupler(design, qubit_a, qubit_b, coupler)


def add_launch_pads(design: DesignPlanar):
    """Add feedline launch pads for the star topology."""
    launch_options_base = dict(
        chip="main",
        trace_width=LINE_50_OHM_WIDTH,
        trace_gap=LINE_50_OHM_GAP,
        lead_length="30um",
        pad_gap="125um",
        pad_width="260um",
        pad_height="260um",
    )

    # Bottom launch pad (for hub resonator feedline)
    bot_opts = dict(**launch_options_base)
    bot_opts["pos_x"] = "0.0mm"
    bot_opts["pos_y"] = "-5.5mm"
    bot_opts["orientation"] = "90"
    LaunchpadWirebond(design, n.name_lp(0), options=bot_opts)

    # Top launch pad
    top_opts = dict(**launch_options_base)
    top_opts["pos_x"] = "0.0mm"
    top_opts["pos_y"] = "5.5mm"
    top_opts["orientation"] = "270"
    LaunchpadWirebond(design, n.name_lp(1), options=top_opts)


def add_chargeline(design: DesignPlanar, group: int):
    """Add a charge line for each qubit in the star topology."""
    qubit = n.qubit_for_group(group)
    lp_nbr = group + 1
    pos = QUBIT_POSITIONS[group]

    # Place charge line launch pad on the chip edges
    cl_x = "-5.5mm" if float(pos["pos_x"].replace("mm", "")) <= 0 else "5.5mm"
    cl_orient = "0" if float(pos["pos_x"].replace("mm", "")) <= 0 else "180"

    launch_options = dict(
        chip="main",
        trace_width=LINE_50_OHM_WIDTH,
        trace_gap=LINE_50_OHM_GAP,
        lead_length="30um",
        pad_gap="125um",
        pad_width="260um",
        pad_height="260um",
        pos_x=cl_x,
        pos_y=pos["pos_y"],
        orientation=cl_orient,
    )
    LaunchpadWirebond(design, n.name_lp(lp_nbr), options=launch_options)

    x_cl_offset = "-2350um" if float(pos["pos_x"].replace("mm", "")) <= 0 else "2350um"
    x_cl_absolute = sum_expression(
        [design.variables[n.design_var_cl_pos_x(qubit)], x_cl_offset]
    )
    y_cl_absolute = sum_expression(
        [design.variables[n.design_var_cl_pos_y(qubit)], pos["pos_y"]]
    )

    otg_options = dict(
        pos_x=x_cl_absolute,
        pos_y=y_cl_absolute,
        orientation=cl_orient,
        width=LINE_50_OHM_WIDTH,
        gap=LINE_50_OHM_GAP,
        termination_gap=LINE_50_OHM_GAP,
    )
    OpenToGround(design, n.name_id("otg_" + qubit), options=otg_options)

    pins = dict(
        start_pin=dict(component=n.name_lp(lp_nbr), pin="tie"),
        end_pin=dict(component=n.name_id("otg_" + qubit), pin="open"),
    )
    options_chargeline = dict(
        fillet="90um",
        hfss_wire_bonds=True,
        trace_width=LINE_50_OHM_WIDTH,
        trace_gap=LINE_50_OHM_GAP,
        pin_inputs=pins,
        step_size="20um",
        lead=dict(start_straight="100um", end_straight="1600um"),
    )
    RoutePathfinder(design, n.name_charge_line(group), options=options_chargeline)


def CoupledLineTee_mesh_names(comp_names):
    return [f"prime_cpw_{comp_names}", f"second_cpw_{comp_names}"]


def render_qiskit_metal_design(design, gui, capacitance_or_surface_p_ratio=False):
    """Build and render the complete 5-qubit star chip layout."""
    for group in n.ALL_GROUPS:
        add_transmon_plus_resonator(design, group=group)

    add_all_couplers(design)
    add_launch_pads(design)

    for group in n.ALL_GROUPS:
        add_chargeline(design, group=group)

    if capacitance_or_surface_p_ratio:
        for component in design.components.values():
            if "hfss_wire_bonds" in component.options:
                component.options["hfss_wire_bonds"] = False

    gui.rebuild()
    gui.autoscale()
