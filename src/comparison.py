"""
Topology comparison table for the 5-qubit chip.

Metrics compared:
  - Total routing length (sum of all couplers)
  - Maximum single coupler/resonator length (weakest coherence link)
  - Number of line crossings / airbridges needed
  - DRC violation count
  - Qualitative workload fit (GHZ, QAOA, Trotter)
  - Circuit depth for target workload
"""

from dataclasses import dataclass, field
from typing import List, Optional

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


@dataclass
class TopologyCandidate:
    """Describes one topology candidate for comparison."""
    name: str
    description: str
    coupling_map: str  # e.g., "[[0,1],[1,2],[2,3],[3,4]]"
    n_qubits: int = 5
    n_couplers: int = 4
    n_resonators: int = 5
    total_coupler_length_um: float = 0.0
    max_coupler_length_um: float = 0.0
    total_resonator_length_um: float = 0.0
    max_resonator_length_um: float = 0.0
    n_crossings: int = 0
    n_airbridges: int = 0
    drc_violations: int = 0
    chip_size_mm: str = "14x14"
    target_workload: str = ""
    workload_fit: str = ""  # "excellent" / "good" / "fair" / "poor"
    circuit_depth_estimate: int = 0
    recommendation_notes: str = ""


def build_comparison_table(
    candidates: List[TopologyCandidate],
) -> Optional["pd.DataFrame"]:
    """Build a comparison DataFrame from topology candidates.

    Returns:
        pandas DataFrame with one row per candidate, or None if pandas unavailable.
    """
    if not HAS_PANDAS:
        print("pandas not available. Printing plain text comparison instead.")
        _print_text_comparison(candidates)
        return None

    rows = []
    for c in candidates:
        rows.append({
            "Topology": c.name,
            "Description": c.description,
            "Coupling Map": c.coupling_map,
            "Chip Size (mm)": c.chip_size_mm,
            "# Couplers": c.n_couplers,
            "Total Coupler Length (um)": f"{c.total_coupler_length_um:.0f}",
            "Max Coupler Length (um)": f"{c.max_coupler_length_um:.0f}",
            "Total Resonator Length (um)": f"{c.total_resonator_length_um:.0f}",
            "Max Resonator Length (um)": f"{c.max_resonator_length_um:.0f}",
            "# Crossings": c.n_crossings,
            "# Airbridges": c.n_airbridges,
            "DRC Violations": c.drc_violations,
            "Target Workload": c.target_workload,
            "Workload Fit": c.workload_fit,
            "Est. Circuit Depth": c.circuit_depth_estimate,
            "Notes": c.recommendation_notes,
        })

    df = pd.DataFrame(rows)
    return df


def _print_text_comparison(candidates: List[TopologyCandidate]) -> None:
    """Fallback plain text comparison when pandas is not available."""
    print("=" * 80)
    print("TOPOLOGY COMPARISON TABLE")
    print("=" * 80)
    for c in candidates:
        print(f"\n--- {c.name} ---")
        print(f"  Description:           {c.description}")
        print(f"  Coupling Map:          {c.coupling_map}")
        print(f"  Chip Size:             {c.chip_size_mm}")
        print(f"  # Couplers:            {c.n_couplers}")
        print(f"  Total Coupler Length:   {c.total_coupler_length_um:.0f} um")
        print(f"  Max Coupler Length:     {c.max_coupler_length_um:.0f} um")
        print(f"  Total Resonator Length: {c.total_resonator_length_um:.0f} um")
        print(f"  Max Resonator Length:   {c.max_resonator_length_um:.0f} um")
        print(f"  # Crossings:           {c.n_crossings}")
        print(f"  # Airbridges:          {c.n_airbridges}")
        print(f"  DRC Violations:        {c.drc_violations}")
        print(f"  Target Workload:       {c.target_workload}")
        print(f"  Workload Fit:          {c.workload_fit}")
        print(f"  Est. Circuit Depth:    {c.circuit_depth_estimate}")
        print(f"  Notes:                 {c.recommendation_notes}")
    print("=" * 80)


# ═══════════════════════════════════════════════════════════════════════════
# PRE-BUILT CANDIDATES
# ═══════════════════════════════════════════════════════════════════════════

LINEAR_CHAIN = TopologyCandidate(
    name="Linear Chain",
    description="1D nearest-neighbor: Q1–Q2–Q3–Q4–Q5",
    coupling_map="[[0,1],[1,2],[2,3],[3,4]]",
    n_couplers=4,
    total_coupler_length_um=8000.0,   # 4 × 2000um (estimated)
    max_coupler_length_um=2000.0,
    total_resonator_length_um=33500.0,  # Sum of 5 resonator lengths
    max_resonator_length_um=7500.0,
    n_crossings=0,
    n_airbridges=0,
    drc_violations=0,
    target_workload="QAOA / Trotterized circuits",
    workload_fit="good",
    circuit_depth_estimate=4,  # CNOT depth for 5-qubit GHZ state
    recommendation_notes=(
        "Simplest routing — zero crossings. "
        "Good for circuits with nearest-neighbor gates (QAOA, Trotter). "
        "Poor for all-to-all connectivity (requires SWAP overhead)."
    ),
)

STAR_HUB = TopologyCandidate(
    name="Star / Hub",
    description="Q3 central hub coupled to Q1, Q2, Q4, Q5",
    coupling_map="[[2,0],[2,1],[2,3],[2,4]]",
    n_couplers=4,
    total_coupler_length_um=11300.0,  # 4 × ~2830um (estimated, diagonal routes)
    max_coupler_length_um=2830.0,
    total_resonator_length_um=33500.0,
    max_resonator_length_um=7500.0,
    n_crossings=2,       # Star routing may require 2 crossings
    n_airbridges=2,      # One airbridge per crossing
    drc_violations=0,
    chip_size_mm="12x12",
    target_workload="GHZ state prep / Fan-out circuits",
    workload_fit="excellent",
    circuit_depth_estimate=1,  # Single CNOT layer for 5-qubit GHZ via hub
    recommendation_notes=(
        "Ideal for GHZ prep (depth-1 fan-out from hub). "
        "Higher total routing length; may need 2 airbridges for crossings "
        "(added fab complexity). "
        "Poor for circuits requiring edge-qubit-to-edge-qubit gates."
    ),
)


def make_recommendation(candidates: List[TopologyCandidate]) -> str:
    """Generate a recommendation string based on the comparison."""
    if len(candidates) < 2:
        return "Need at least 2 candidates to compare."

    scores = []
    for c in candidates:
        score = (
            c.total_coupler_length_um / 10000.0 +  # Normalize
            c.max_coupler_length_um / 5000.0 +
            c.n_crossings * 5.0 +
            c.n_airbridges * 3.0 +
            c.drc_violations * 100.0
        )
        scores.append((score, c.name))

    scores.sort()
    best = scores[0][1]

    return (
        f"RECOMMENDATION: Fabricate '{best}' topology.\n"
        f"  Rationale: Lowest combined score considering routing length, "
        f"crossings, and manufacturability.\n"
        f"  Scores: {', '.join(f'{name}={s:.1f}' for s, name in scores)}"
    )


if __name__ == "__main__":
    candidates = [LINEAR_CHAIN, STAR_HUB]
    df = build_comparison_table(candidates)
    if df is not None:
        print(df.to_string(index=False))
    print()
    print(make_recommendation(candidates))
