"""
Physical chip layout for a 5-qubit linear chain.

Topology A — Linear Chain: Q1—Q2—Q3—Q4—Q5
Qubits are arranged vertically, evenly spaced along the y-axis.
Each qubit has a readout resonator coupled to a shared feedline
via a CoupledLineTee. Nearest-neighbor couplers connect adjacent qubits.

Uses TransmonPocket as the qubit component.
"""

import names as n
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

# CPW geometry (50-ohm impedance)
LINE_50_OHM_WIDTH = "16.51um"
LINE_50_OHM_GAP = "10um"

# Resonator geometry
RESONATOR_WIDTH = "20um"
RESONATOR_GAP = "20um"

# Routing
BEND_RADIUS = "99um"

# ── Chip footprint ───────────────────────────────────────────────────────
chip_type = ChipType(
    size_x="14mm",
    size_y="14mm",
    size_z="-300um",
    material="silicon",
)

# ── Design Rule Constants (DRC) ──────────────────────────────────────────
MIN_QUBIT_SPACING_UM = 1500    # Minimum center-to-center qubit spacing
MIN_TRACE_WIDTH_UM = 10        # Minimum CPW center conductor width
MIN_TRACE_GAP_UM = 6           # Minimum CPW gap
EDGE_KEEPOUT_UM = 500          # Keep-out zone from chip edge
MIN_COUPLER_SEPARATION_UM = 200  # Minimum parallel CPW separation

# ── Qubit placement (linear chain along y-axis) ─────────────────────────

QUBIT_POSITIONS = {
    n.NBR_1: {"pos_x": "-2.0mm", "pos_y": "-4.0mm", "orientation": "0"},
    n.NBR_2: {"pos_x": "-2.0mm", "pos_y": "-2.0mm", "orientation": "180"},
    n.NBR_3: {"pos_x": "-2.0mm", "pos_y": "0.0mm",  "orientation": "0"},
    n.NBR_4: {"pos_x": "-2.0mm", "pos_y": "2.0mm",  "orientation": "180"},
    n.NBR_5: {"pos_x": "-2.0mm", "pos_y": "4.0mm",  "orientation": "0"},
}

# ── Resonator tee positions (feedline bus along the right side) ──────────
TEE_POSITIONS = {
    n.NBR_1: {"pos_x": "2.0mm", "pos_y": "-4.0mm", "orientation": "-90"},
    n.NBR_2: {"pos_x": "2.0mm", "pos_y": "-2.0mm", "orientation": "-90"},
    n.NBR_3: {"pos_x": "2.0mm", "pos_y": "0.0mm",  "orientation": "-90"},
    n.NBR_4: {"pos_x": "2.0mm", "pos_y": "2.0mm",  "orientation": "-90"},
    n.NBR_5: {"pos_x": "2.0mm", "pos_y": "4.0mm",  "orientation": "-90"},
}


# ═══════════════════════════════════════════════════════════════════════════
# COMPONENT BUILDERS
# ═══════════════════════════════════════════════════════════════════════════

def add_transmon_plus_resonator(design: DesignPlanar, group: int):
    """Place one transmon qubit + its readout resonator + tee coupling.

    Each qubit has two connection pads:
      - 'readout': connects to the resonator (top/bottom)
      - 'coupler': connects to the nearest-neighbor coupler
    """
    nbr_idx = group - 1
    qubit = n.qubit_for_group(group)
    resonator = n.resonator_for_group(group)
    pos = QUBIT_POSITIONS[group]
    tee_pos = TEE_POSITIONS[group]

    # ── Transmon (TransmonPocket) ─────────────────────────────────────
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

    # ── Coupled Line Tee (resonator → feedline coupling) ──────────────
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

    # ── Resonator (RouteMeander from qubit to tee) ────────────────────
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
    """Route a coupler (RouteMeander) between two qubits' 'coupler' pads."""
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
    """Add all 4 nearest-neighbor couplers for the linear chain."""
    for qubit_a, qubit_b, coupler in n.COUPLING_EDGES:
        add_coupler(design, qubit_a, qubit_b, coupler)


def add_feedline_interconnects(design: DesignPlanar):
    """Connect the tee junctions with feedline segments (shared bus)."""
    for i in range(len(n.ALL_GROUPS) - 1):
        group_a = n.ALL_GROUPS[i]
        group_b = n.ALL_GROUPS[i + 1]

        pins = dict(
            start_pin=dict(component=n.name_tee(group_a), pin="prime_start"),
            end_pin=dict(component=n.name_tee(group_b), pin="prime_end"),
        )

        options_rpf = dict(
            fillet="49um",
            hfss_wire_bonds=False,
            trace_width=LINE_50_OHM_WIDTH,
            trace_gap=LINE_50_OHM_GAP,
            pin_inputs=pins,
        )

        RoutePathfinder(
            design,
            n.name_tee_to_tee(group_a, group_b),
            options=options_rpf,
        )


def add_launch_pads(design: DesignPlanar):
    """Add two feedline launch pads (top and bottom of the feedline bus)."""
    launch_options_base = dict(
        chip="main",
        trace_width=LINE_50_OHM_WIDTH,
        trace_gap=LINE_50_OHM_GAP,
        lead_length="30um",
        pad_gap="125um",
        pad_width="260um",
        pad_height="260um",
    )

    # Top launch pad
    top_opts = dict(**launch_options_base)
    top_opts["pos_x"] = "2.0mm"
    top_opts["pos_y"] = "6.5mm"
    top_opts["orientation"] = "270"
    LaunchpadWirebond(design, n.name_lp(0), options=top_opts)

    # Bottom launch pad
    bot_opts = dict(**launch_options_base)
    bot_opts["pos_x"] = "2.0mm"
    bot_opts["pos_y"] = "-6.5mm"
    bot_opts["orientation"] = "90"
    LaunchpadWirebond(design, n.name_lp(1), options=bot_opts)

    # Connect top launch pad to topmost tee
    pins_top = dict(
        start_pin=dict(component=n.name_lp(0), pin="tie"),
        end_pin=dict(component=n.name_tee(n.NBR_5), pin="prime_start"),
    )
    options_top = dict(
        fillet="49um",
        hfss_wire_bonds=False,
        trace_width=LINE_50_OHM_WIDTH,
        trace_gap=LINE_50_OHM_GAP,
        pin_inputs=pins_top,
    )
    RoutePathfinder(design, n.name_lp_to_tee(0, n.NBR_5), options=options_top)

    # Connect bottom launch pad to bottommost tee
    pins_bot = dict(
        start_pin=dict(component=n.name_lp(1), pin="tie"),
        end_pin=dict(component=n.name_tee(n.NBR_1), pin="prime_end"),
    )
    options_bot = dict(
        fillet="49um",
        hfss_wire_bonds=False,
        trace_width=LINE_50_OHM_WIDTH,
        trace_gap=LINE_50_OHM_GAP,
        pin_inputs=pins_bot,
    )
    RoutePathfinder(design, n.name_lp_to_tee(1, n.NBR_1), options=options_bot)


def add_chargeline(design: DesignPlanar, group: int):
    """Add a charge/flux line for drive control of each qubit."""
    qubit = n.qubit_for_group(group)
    lp_nbr = group + 1  # Launch pads 2–6 for charge lines

    pos = QUBIT_POSITIONS[group]

    launch_options = dict(
        chip="main",
        trace_width=LINE_50_OHM_WIDTH,
        trace_gap=LINE_50_OHM_GAP,
        lead_length="30um",
        pad_gap="125um",
        pad_width="260um",
        pad_height="260um",
        pos_x="-6.5mm",
        pos_y=pos["pos_y"],
        orientation="0",
    )
    LaunchpadWirebond(design, n.name_lp(lp_nbr), options=launch_options)

    # Open-to-ground termination near the qubit
    x_cl_offset = "-2350um"
    x_cl_absolute = sum_expression(
        [design.variables[n.design_var_cl_pos_x(qubit)], x_cl_offset]
    )
    y_cl_offset = "0um"
    y_cl_absolute = sum_expression(
        [design.variables[n.design_var_cl_pos_y(qubit)], pos["pos_y"]]
    )

    otg_options = dict(
        pos_x=x_cl_absolute,
        pos_y=y_cl_absolute,
        orientation="0",
        width=LINE_50_OHM_WIDTH,
        gap=LINE_50_OHM_GAP,
        termination_gap=LINE_50_OHM_GAP,
    )
    OpenToGround(design, n.name_id("otg_" + qubit), options=otg_options)

    # Route from launch pad to open-to-ground
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


# ═══════════════════════════════════════════════════════════════════════════
# MESH HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def CoupledLineTee_mesh_names(comp_names):
    """Generate mesh names for finer meshing of CoupledLineTee components."""
    return [f"prime_cpw_{comp_names}", f"second_cpw_{comp_names}"]


# ═══════════════════════════════════════════════════════════════════════════
# MAIN RENDER FUNCTION
# ═══════════════════════════════════════════════════════════════════════════

def render_qiskit_metal_design(design, gui, capacitance_or_surface_p_ratio=False):
    """Build and render the complete 5-qubit linear-chain chip layout."""

    # 1. Place all 5 transmon+resonator units
    for group in n.ALL_GROUPS:
        add_transmon_plus_resonator(design, group=group)

    # 2. Add all 4 nearest-neighbor couplers
    add_all_couplers(design)

    # 3. Connect tees with feedline bus
    add_feedline_interconnects(design)

    # 4. Add readout feedline launch pads
    add_launch_pads(design)

    # 5. Add charge lines for all qubits
    for group in n.ALL_GROUPS:
        add_chargeline(design, group=group)

    # 6. Optionally disable wire bonds (for capacitance simulations)
    if capacitance_or_surface_p_ratio:
        for component in design.components.values():
            if "hfss_wire_bonds" in component.options:
                component.options["hfss_wire_bonds"] = False

    gui.rebuild()
    gui.autoscale()
