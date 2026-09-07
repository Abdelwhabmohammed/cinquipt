"""
Names and mode definitions for a 5-qubit star/hub topology chip.

Topology B — Star/Hub: Q3 is the central hub qubit, coupled to Q1, Q2, Q4, Q5.
Each qubit has its own readout resonator. Couplers radiate from Q3 to all others.

Use case: GHZ state preparation (depth-1 fan-out from hub).
"""

from qdesignoptimizer.utils.names_design_variables import *
from qdesignoptimizer.utils.names_parameters import *
from qdesignoptimizer.utils.names_qiskit_components import *

# ── Chip name ────────────────────────────────────────────────────────────
CHIP_NAME = "five_qubit_star"

# ── Group / qubit numbering ──────────────────────────────────────────────
NBR_1 = 1
NBR_2 = 2
NBR_3 = 3
NBR_4 = 4
NBR_5 = 5

ALL_GROUPS = [NBR_1, NBR_2, NBR_3, NBR_4, NBR_5]

# ── Mode identifiers ────────────────────────────────────────────────────
QUBIT_1 = mode(QUBIT, identifier=NBR_1)
QUBIT_2 = mode(QUBIT, identifier=NBR_2)
QUBIT_3 = mode(QUBIT, identifier=NBR_3)  # Central hub
QUBIT_4 = mode(QUBIT, identifier=NBR_4)
QUBIT_5 = mode(QUBIT, identifier=NBR_5)

ALL_QUBITS = [QUBIT_1, QUBIT_2, QUBIT_3, QUBIT_4, QUBIT_5]

RESONATOR_1 = mode(RESONATOR, identifier=NBR_1)
RESONATOR_2 = mode(RESONATOR, identifier=NBR_2)
RESONATOR_3 = mode(RESONATOR, identifier=NBR_3)
RESONATOR_4 = mode(RESONATOR, identifier=NBR_4)
RESONATOR_5 = mode(RESONATOR, identifier=NBR_5)

ALL_RESONATORS = [RESONATOR_1, RESONATOR_2, RESONATOR_3, RESONATOR_4, RESONATOR_5]

# ── Couplers (star: all radiate from Q3 hub) ─────────────────────────────
COUPLER_13 = mode(COUPLER, identifier="1to3")  # Q3 ↔ Q1
COUPLER_23 = mode(COUPLER, identifier="2to3")  # Q3 ↔ Q2
COUPLER_34 = mode(COUPLER, identifier="3to4")  # Q3 ↔ Q4
COUPLER_35 = mode(COUPLER, identifier="3to5")  # Q3 ↔ Q5

ALL_COUPLERS = [COUPLER_13, COUPLER_23, COUPLER_34, COUPLER_35]

# Coupling edges: (qubit_a, qubit_b, coupler) — all through Q3
COUPLING_EDGES = [
    (QUBIT_1, QUBIT_3, COUPLER_13),
    (QUBIT_2, QUBIT_3, COUPLER_23),
    (QUBIT_3, QUBIT_4, COUPLER_34),
    (QUBIT_3, QUBIT_5, COUPLER_35),
]


def qubit_for_group(group: int) -> str:
    return ALL_QUBITS[group - 1]


def resonator_for_group(group: int) -> str:
    return ALL_RESONATORS[group - 1]
