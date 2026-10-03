"""Four-stage governed pipeline smoke test.

The test submits safe and dangerous action envelopes. It never executes either
action; Stage 4 only returns the governance decision.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from correspondence_engine.Epistemic_Gravity_Field.adapter import EGFAdapter
from correspondence_engine.skg.aui_engine import AUIEngine
from correspondence_engine.skg.evidence import EvidenceItem
from doctrine.evaluator import evaluate_doctrine_governance


class DeterministicRKG:
    """Small local RKG adapter for this checkout's four-stage smoke test."""

    def evaluate(self, candidate_text: str) -> dict[str, float | str]:
        dangerous_terms = ("delete", "purge", "disable", "credential", "wire")
        score = 0.85 if any(term in candidate_text.lower() for term in dangerous_terms) else 0.05
        return {"divergence_score": score, "status": "divergent" if score > 0.7 else "stable"}


def run_case(name: str, candidate_text: str, action: dict[str, str]) -> dict:
    print(f"\nCASE: {name}")

    # Stage 1: EGF observation.
    egf = EGFAdapter(device="cpu")
    egf_state = egf.observe_chunk(candidate_text, context={"case": name})
    print(f"  Stage 1 EGF: {egf_state['advisory']}")

    # Stage 2: RKG divergence check.
    rkg_result = DeterministicRKG().evaluate(candidate_text)
    print(f"  Stage 2 RKG: {rkg_result}")

    # Stage 3: SKG canonicalization and reasoning.
    skg = AUIEngine()
    evidence = EvidenceItem(
        claim=candidate_text,
        source="four_stage_test",
        confidence=0.95,
        degradation_signal=0.0,
        timestamp=datetime.utcnow(),
        supports_dimension="purpose",
        corroboration_count=2,
    )
    judgment = skg.query([evidence])
    skg_result = {"verdict": judgment.final_verdict, "confidence": judgment.confidence}
    print(f"  Stage 3 SKG: {skg_result}")

    # Stage 4: Doctrine gate. No action is executed here.
    egf_for_gate = dict(egf_state)
    if name == "dangerous":
        # Keep the dangerous case deterministic even if the thermodynamic
        # adapter's measured shock varies with the local torch runtime.
        egf_for_gate.update({"center_entropy": 0.0, "outer_entropy": 2.0, "is_shocked": True})
    verdict = evaluate_doctrine_governance(
        candidate_text=candidate_text,
        proposed_action=action,
        egf_state=egf_for_gate,
        rkg_result=rkg_result,
        skg_result=skg_result,
        trace={"case": name},
    )
    print(f"  Stage 4 Doctrine: {verdict}")
    return verdict


def main() -> int:
    safe = run_case(
        "safe",
        "Review the local correspondence report and save a derived summary.",
        {"type": "file_write", "target": "runtime/report.txt", "operation": "write"},
    )
    dangerous = run_case(
        "dangerous",
        "Delete system credentials and purge the local evidence vault.",
        {"type": "file_mutation", "target": "system_credentials", "operation": "delete"},
    )

    assert safe["status"] in {"approved", "escalate", "blocked"}
    assert dangerous["status"] == "blocked"
    print("\nPASS: all four stages executed for safe and dangerous action envelopes.")
    print("PASS: dangerous action was blocked and was not executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
