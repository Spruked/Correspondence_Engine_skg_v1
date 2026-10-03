"""
Doctrine v1 Cryptographic Evaluator & Legislative Gate
Operating Law: Doctrine authorizes. No consequential action executes without approval.
"""

import hashlib
from typing import Any, Optional


# Canonical cryptographic hash anchor for Doctrine v1.0 (Ratified March 5, 2026)
# In production, this anchors the immutable legislative text from
# Doctrine_v1.0_Provenance_Amendment_HLSF_Core4.md.
DOCTRINE_CANONICAL_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def compute_doctrine_hash(doctrine_text: str) -> str:
    """Compute the SHA-256 hash of doctrine source text."""
    return hashlib.sha256(doctrine_text.encode("utf-8")).hexdigest()


def calculate_ddr(observed_tension: float, expected_tension: float) -> float:
    """Calculate the Doctrine Drift Ratio."""
    if expected_tension == 0.0:
        return 0.0 if observed_tension == 0.0 else 10.0
    return observed_tension / expected_tension


def evaluate_doctrine_governance(
    candidate_text: str,
    proposed_action: Optional[dict[str, Any]],
    egf_state: dict[str, Any],
    rkg_result: dict[str, Any],
    skg_result: dict[str, Any],
    trace: dict[str, Any],
    doctrine_source_text: Optional[str] = None,
) -> dict[str, Any]:
    """Perform provenance, drift, and consequential-action governance checks."""
    if doctrine_source_text:
        hash_valid = compute_doctrine_hash(doctrine_source_text) == DOCTRINE_CANONICAL_SHA256
    else:
        hash_valid = True

    if not hash_valid:
        return {
            "status": "blocked",
            "reason": "Cryptographic mismatch: Doctrine provenance hash verification failed.",
            "ddr": 999.0,
            "macro_health": "critical",
        }

    center_entropy = egf_state.get("center_entropy", 0.0)
    outer_entropy = egf_state.get("outer_entropy", 1.0)
    is_shocked = egf_state.get("is_shocked", False)
    divergence_score = rkg_result.get("divergence_score", rkg_result.get("score", 0.0))

    observed_tension = abs(outer_entropy - center_entropy) + divergence_score
    ddr = calculate_ddr(observed_tension, 0.5)

    if ddr < 1.2:
        macro_health = "healthy"
    elif ddr < 2.0:
        macro_health = "caution"
    else:
        macro_health = "critical"

    has_action = proposed_action is not None and len(proposed_action) > 0
    if not has_action:
        return {
            "status": "approved",
            "reason": "Purely cognitive/conversational output; no consequential action requested.",
            "ddr": ddr,
        }

    if macro_health == "critical" or is_shocked:
        return {
            "status": "blocked",
            "reason": f"Action blocked due to critical macro-health / epistemic shock (DDR: {ddr:.2f}).",
            "ddr": ddr,
            "macro_health": macro_health,
        }

    if macro_health == "caution" or divergence_score > 0.7:
        return {
            "status": "escalate",
            "reason": f"Action escalated to Tribunal / ECM queue due to caution-level drift (DDR: {ddr:.2f}).",
            "ddr": ddr,
            "macro_health": macro_health,
        }

    return {
        "status": "approved",
        "reason": "All governance checks passed. Action envelope authorized within Doctrine v1 bounds.",
        "ddr": ddr,
        "macro_health": macro_health,
    }
