""" Design Rule Check (DRC) for the 5-qubit chip. """

import math
from dataclasses import dataclass
from typing import List, Tuple

import names as n


# ═══════════════════════════════════════════════════════════════════════════
# DESIGN RULE CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class DesignRules:
    """Encapsulates all design rules for the chip."""
    min_qubit_spacing_um: float = 1500.0    # Center-to-center
    min_trace_width_um: float = 10.0        # CPW center conductor
    min_trace_gap_um: float = 6.0           # CPW gap
    edge_keepout_um: float = 500.0          # From chip boundary
    min_coupler_separation_um: float = 200.0  # Parallel CPW separation


@dataclass
class DRCViolation:
    """A single design rule violation."""
    rule: str
    description: str
    severity: str  # "error" or "warning"

    def __str__(self):
        return f"[{self.severity.upper()}] {self.rule}: {self.description}"


DEFAULT_RULES = DesignRules()


# ═══════════════════════════════════════════════════════════════════════════
# DRC FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def _parse_position_mm(pos_str: str) -> float:
    """Parse a position string like '-2.0mm' to a float in um."""
    pos_str = pos_str.strip()
    if pos_str.endswith("mm"):
        return float(pos_str[:-2]) * 1000.0
    elif pos_str.endswith("um"):
        return float(pos_str[:-2])
    else:
        raise ValueError(f"Cannot parse position: {pos_str}")


def _distance_um(pos_a: Tuple[float, float], pos_b: Tuple[float, float]) -> float:
    """Euclidean distance in um between two (x, y) positions."""
    return math.sqrt((pos_a[0] - pos_b[0]) ** 2 + (pos_a[1] - pos_b[1]) ** 2)


def check_qubit_spacing(
    qubit_positions: dict,
    rules: DesignRules = DEFAULT_RULES,
) -> List[DRCViolation]:
    """Check that all qubit pairs have sufficient center-to-center spacing."""
    violations = []
    groups = sorted(qubit_positions.keys())

    positions_um = {}
    for g in groups:
        pos = qubit_positions[g]
        x = _parse_position_mm(pos["pos_x"])
        y = _parse_position_mm(pos["pos_y"])
        positions_um[g] = (x, y)

    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            g_a, g_b = groups[i], groups[j]
            dist = _distance_um(positions_um[g_a], positions_um[g_b])
            if dist < rules.min_qubit_spacing_um:
                violations.append(DRCViolation(
                    rule="MIN_QUBIT_SPACING",
                    description=(
                        f"Q{g_a}–Q{g_b} spacing = {dist:.0f} um "
                        f"< minimum {rules.min_qubit_spacing_um:.0f} um"
                    ),
                    severity="error",
                ))

    return violations


def check_edge_keepout(
    qubit_positions: dict,
    chip_size_x_mm: float,
    chip_size_y_mm: float,
    rules: DesignRules = DEFAULT_RULES,
) -> List[DRCViolation]:
    """Check that all qubits are within the chip boundary minus keep-out."""
    violations = []
    half_x = chip_size_x_mm * 1000.0 / 2.0
    half_y = chip_size_y_mm * 1000.0 / 2.0
    keepout = rules.edge_keepout_um

    for g, pos in qubit_positions.items():
        x = _parse_position_mm(pos["pos_x"])
        y = _parse_position_mm(pos["pos_y"])

        if abs(x) > (half_x - keepout):
            violations.append(DRCViolation(
                rule="EDGE_KEEPOUT",
                description=(
                    f"Q{g} x={x:.0f}um violates edge keep-out "
                    f"(chip half-width={half_x:.0f}um, keepout={keepout:.0f}um)"
                ),
                severity="error",
            ))
        if abs(y) > (half_y - keepout):
            violations.append(DRCViolation(
                rule="EDGE_KEEPOUT",
                description=(
                    f"Q{g} y={y:.0f}um violates edge keep-out "
                    f"(chip half-height={half_y:.0f}um, keepout={keepout:.0f}um)"
                ),
                severity="error",
            ))

    return violations


def run_drc(
    qubit_positions: dict,
    chip_size_x_mm: float = 14.0,
    chip_size_y_mm: float = 14.0,
    rules: DesignRules = DEFAULT_RULES,
) -> List[DRCViolation]:
    """Run all design rule checks and return violations.

    Returns:
        List of DRCViolation objects. Empty list = all checks pass.
    """
    violations = []
    violations.extend(check_qubit_spacing(qubit_positions, rules))
    violations.extend(check_edge_keepout(
        qubit_positions, chip_size_x_mm, chip_size_y_mm, rules
    ))
    return violations


def print_drc_report(violations: List[DRCViolation]) -> None:
    if not violations:
        print("DRC PASSED — no violations found.")
    else:
        print(f"DRC FAILED — {len(violations)} violation(s):")
        for v in violations:
            print(f"  {v}")
