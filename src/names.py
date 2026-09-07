"""
Names and mode definitions for a 5-qubit linear chain chip.

Topology A — Linear Chain: Q1—Q2—Q3—Q4—Q5
Each qubit has its own readout resonator. Couplers connect nearest neighbors.
"""

from qdesignoptimizer.utils.names_design_variables import *
from qdesignoptimizer.utils.names_parameters import *
from qdesignoptimizer.utils.names_qiskit_components import *

"""These * imports allow you to use all generic function generators
for design variables and qiskit component names."""


# ── Chip name ────────────────────────────────────────────────────────────
CHIP_NAME = "five_qubit_linear"

# ── Group / qubit numbering ──────────────────────────────────────────────
NBR_1 = 1
NBR_2 = 2
NBR_3 = 3
NBR_4 = 4
NBR_5 = 5

ALL_GROUPS = [NBR_1, NBR_2, NBR_3, NBR_4, NBR_5]

# ── Mode identifiers ────────────────────────────────────────────────────
# Qubits
QUBIT_1 = mode(QUBIT, identifier=NBR_1)
QUBIT_2 = mode(QUBIT, identifier=NBR_2)
QUBIT_3 = mode(QUBIT, identifier=NBR_3)
QUBIT_4 = mode(QUBIT, identifier=NBR_4)
QUBIT_5 = mode(QUBIT, identifier=NBR_5)

ALL_QUBITS = [QUBIT_1, QUBIT_2, QUBIT_3, QUBIT_4, QUBIT_5]

# Resonators (one per qubit)
RESONATOR_1 = mode(RESONATOR, identifier=NBR_1)
RESONATOR_2 = mode(RESONATOR, identifier=NBR_2)
RESONATOR_3 = mode(RESONATOR, identifier=NBR_3)
RESONATOR_4 = mode(RESONATOR, identifier=NBR_4)
RESONATOR_5 = mode(RESONATOR, identifier=NBR_5)

ALL_RESONATORS = [RESONATOR_1, RESONATOR_2, RESONATOR_3, RESONATOR_4, RESONATOR_5]

# Couplers (nearest-neighbor in linear chain)
COUPLER_12 = mode(COUPLER, identifier="1to2")
COUPLER_23 = mode(COUPLER, identifier="2to3")
COUPLER_34 = mode(COUPLER, identifier="3to4")
COUPLER_45 = mode(COUPLER, identifier="4to5")

ALL_COUPLERS = [COUPLER_12, COUPLER_23, COUPLER_34, COUPLER_45]

# Coupling edges: list of (qubit_a, qubit_b, coupler) tuples
COUPLING_EDGES = [
    (QUBIT_1, QUBIT_2, COUPLER_12),
    (QUBIT_2, QUBIT_3, COUPLER_23),
    (QUBIT_3, QUBIT_4, COUPLER_34),
    (QUBIT_4, QUBIT_5, COUPLER_45),
]


def qubit_for_group(group: int) -> str:
    """Return the qubit mode name for a group number (1-5)."""
    return ALL_QUBITS[group - 1]


def resonator_for_group(group: int) -> str:
    """Return the resonator mode name for a group number (1-5)."""
    return ALL_RESONATORS[group - 1]
