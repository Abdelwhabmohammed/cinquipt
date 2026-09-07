"""
Parameter sweep over qubit pitch/spacing for the 5-qubit linear chain.

Sweeps the center-to-center distance between adjacent qubits and computes
a cost function based on total coupler length and maximum single coupler
length (proxy for weakest coherence path).

"""

import json
import math
import copy
from typing import Dict, List, Tuple

import numpy as np

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

import design as d
import design_rules as dr


# ═══════════════════════════════════════════════════════════════════════════
# COST FUNCTION
# ═══════════════════════════════════════════════════════════════════════════

def compute_layout_cost(
    qubit_positions: dict,
    coupling_edges: list,
    penalty_weight: float = 2.0,
) -> dict:
    """Compute a layout cost metric for a given qubit placement.

    Cost = total_coupler_length + penalty_weight * max_single_coupler_length

    The total coupler length is summed over all coupling edges.
    The maximum single coupler length is a proxy for the weakest coherence
    path — longer resonator/coupler lines have more loss.

    Args:
        qubit_positions: dict of {group: {"pos_x": ..., "pos_y": ...}}
        coupling_edges: list of (qubit_a_mode, qubit_b_mode, coupler_mode)
        penalty_weight: weight for the max-length penalty term

    Returns:
        dict with 'total_length_um', 'max_length_um', 'cost', and per-edge lengths
    """
    positions_um = {}
    for g, pos in qubit_positions.items():
        x = dr._parse_position_mm(pos["pos_x"])
        y = dr._parse_position_mm(pos["pos_y"])
        positions_um[g] = (x, y)

    edge_lengths = []
    group_pairs = [(1, 2), (2, 3), (3, 4), (4, 5)]

    for (g_a, g_b) in group_pairs:
        dist = dr._distance_um(positions_um[g_a], positions_um[g_b])
        edge_lengths.append(dist)

    total_length = sum(edge_lengths)
    max_length = max(edge_lengths) if edge_lengths else 0.0
    cost = total_length + penalty_weight * max_length

    return {
        "total_length_um": total_length,
        "max_length_um": max_length,
        "cost": cost,
        "edge_lengths_um": edge_lengths,
    }


# ═══════════════════════════════════════════════════════════════════════════
# PARAMETER SWEEP
# ═══════════════════════════════════════════════════════════════════════════

def generate_positions_for_pitch(
    pitch_um: float,
    base_x_mm: float = -2.0,
) -> dict:
    """Generate qubit positions for a given pitch (center-to-center spacing).

    Qubits are evenly spaced along y-axis, centered at y=0.
    """
    n_qubits = 5
    # Total span = (n-1) * pitch
    y_start = -(n_qubits - 1) * pitch_um / 2.0

    orientations = ["0", "180", "0", "180", "0"]

    positions = {}
    for i in range(n_qubits):
        g = i + 1
        y = y_start + i * pitch_um
        positions[g] = {
            "pos_x": f"{base_x_mm}mm",
            "pos_y": f"{y / 1000.0}mm",
            "orientation": orientations[i],
        }
    return positions


def sweep_qubit_pitch(
    pitch_range_um: Tuple[float, float] = (1600.0, 3500.0),
    n_steps: int = 20,
    penalty_weight: float = 2.0,
    chip_size_x_mm: float = 14.0,
    chip_size_y_mm: float = 14.0,
) -> dict:
    """Sweep qubit pitch and compute cost + DRC status at each point.

    Args:
        pitch_range_um: (min_pitch, max_pitch) in micrometers
        n_steps: number of sweep points
        penalty_weight: weight for max-length penalty in cost function
        chip_size_x_mm: chip width for DRC
        chip_size_y_mm: chip height for DRC

    Returns:
        dict with arrays: pitches, costs, total_lengths, max_lengths,
        drc_pass, n_violations
    """
    pitches = np.linspace(pitch_range_um[0], pitch_range_um[1], n_steps)
    costs = []
    total_lengths = []
    max_lengths = []
    drc_pass = []
    n_violations = []

    for pitch in pitches:
        positions = generate_positions_for_pitch(pitch)
        result = compute_layout_cost(positions, [], penalty_weight)
        costs.append(result["cost"])
        total_lengths.append(result["total_length_um"])
        max_lengths.append(result["max_length_um"])

        violations = dr.run_drc(positions, chip_size_x_mm, chip_size_y_mm)
        drc_pass.append(len(violations) == 0)
        n_violations.append(len(violations))

    return {
        "pitches_um": pitches,
        "costs": np.array(costs),
        "total_lengths_um": np.array(total_lengths),
        "max_lengths_um": np.array(max_lengths),
        "drc_pass": np.array(drc_pass),
        "n_violations": np.array(n_violations),
    }


# ═══════════════════════════════════════════════════════════════════════════
# VISUALIZATION
# ═══════════════════════════════════════════════════════════════════════════

def plot_sweep_results(sweep_data: dict, save_path: str = None) -> None:
    """Plot the parameter sweep results: cost vs. pitch with DRC overlay.

    Produces a 2×1 figure:
      - Top: Cost, total length, max length vs. pitch
      - Bottom: DRC pass/fail indicator
    """
    if not HAS_MPL:
        print("matplotlib not available, skipping plot.")
        return

    pitches = sweep_data["pitches_um"]
    costs = sweep_data["costs"]
    totals = sweep_data["total_lengths_um"]
    maxes = sweep_data["max_lengths_um"]
    drc = sweep_data["drc_pass"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True,
                                    gridspec_kw={"height_ratios": [3, 1]})

    # Top panel: cost metrics
    ax1.plot(pitches, costs, "b-o", label="Total Cost", linewidth=2, markersize=4)
    ax1.plot(pitches, totals, "g--s", label="Total Coupler Length (um)",
             linewidth=1.5, markersize=3)
    ax1.plot(pitches, maxes, "r--^", label="Max Single Coupler (um)",
             linewidth=1.5, markersize=3)
    ax1.set_ylabel("Cost / Length (um)")
    ax1.set_title("5-Qubit Linear Chain: Layout Cost vs. Qubit Pitch")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Bottom panel: DRC status
    colors = ["green" if p else "red" for p in drc]
    ax2.bar(pitches, [1] * len(pitches), width=(pitches[1] - pitches[0]) * 0.8,
            color=colors, alpha=0.7)
    ax2.set_ylabel("DRC")
    ax2.set_xlabel("Qubit Pitch (um)")
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(["FAIL", "PASS"])
    ax2.set_ylim(0, 1.2)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Sweep plot saved to: {save_path}")

    plt.show()


if __name__ == "__main__":
    # Run a demo sweep
    print("Running qubit pitch sweep...")
    data = sweep_qubit_pitch()
    print(f"Optimal pitch: {data['pitches_um'][np.argmin(data['costs'])]:.0f} um")
    print(f"Minimum cost: {np.min(data['costs']):.0f}")
    plot_sweep_results(data, save_path="out/pitch_sweep_linear.png")
