"""
Master Runtime Orchestrator
Operating Law: EGF observes, RKG checks, SKG canonizes, Doctrine authorizes.
"""

import sys
import os
from typing import Dict, Any, Optional

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from egf.adapter import EGFAdapter
from divergence_rkg.divergence_rkg import DivergenceRKG
from correspondence_engine.skg.aui_engine import AUIEngine
from doctrine.evaluator import evaluate_doctrine_governance


class MasterRuntime:
    def __init__(self, device: str = "cpu"):
        print("Initializing Master Cognitive Operating System...")
        self.egf = EGFAdapter(device=device)
        self.rkg = DivergenceRKG()
        self.skg_engine = AUIEngine()  # Canonical evidence/claim/atom manager
        
    def process_candidate(
        self, 
        prompt: str, 
        candidate_text: str, 
        proposed_action: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Executes the 4-stage governed pipeline on a completed thought chunk / candidate text.
        """
        trace = {"prompt": prompt, "candidate_text": candidate_text}

        # -------------------------------------------------------------
        # STAGE 1: EGF Observation (Thermodynamic filtering)
        # -------------------------------------------------------------
        egf_state = self.egf.observe_chunk(
            chunk_text=candidate_text,
            context={"prompt": prompt, "phase": "candidate_evaluation"}
        )

        # -------------------------------------------------------------
        # STAGE 2: RKG Divergence Check (Quality Control & Risk)
        # -------------------------------------------------------------
        # Using RKG to check for divergence, memory conflicts, or drift
        rkg_result = self.rkg.evaluate(
            candidate_text, 
            reference_vault=getattr(self.skg_engine, "vault", None)
        )

        # -------------------------------------------------------------
        # STAGE 3: SKG Canonicalization (Evidence -> Claim -> Atom)
        # -------------------------------------------------------------
        # SKG remains the sole owner of canonical correspondence evaluation
        skg_result = self.skg_engine.query([{
            "text": candidate_text,
            "source": "llm_candidate",
            "metadata": {"prompt": prompt}
        }])

        # -------------------------------------------------------------
        # STAGE 4: Doctrine Authorization (Hard Governance Gate)
        # -------------------------------------------------------------
        # No consequential action executes unless Doctrine approves.
        governance_verdict = evaluate_doctrine_governance(
            candidate_text=candidate_text,
            proposed_action=proposed_action,
            egf_state=egf_state,
            rkg_result=rkg_result,
            skg_result=skg_result,
            trace=trace
        )

        return {
            "egf_state": egf_state,
            "rkg_result": rkg_result,
            "skg_result": skg_result,
            "governance_verdict": governance_verdict
        }


# --- Smoke Test ---
if __name__ == "__main__":
    runtime = MasterRuntime(device="cpu")
    
    test_prompt = "Should we update system credentials and purge temporary files?"
    test_candidate = "The system should delete temporary cache files because they are obsolete."
    test_action = {
        "type": "file_mutation",
        "target": "C:/temp/cache_01.tmp",
        "operation": "delete"
    }

    print("\nRunning Master Runtime Pipeline Test...")
    result = runtime.process_candidate(
        prompt=test_prompt,
        candidate_text=test_candidate,
        proposed_action=test_action
    )

    print("\n--- Pipeline Execution Results ---")
    print(f"EGF Advisory:        {result['egf_state']['advisory']}")
    print(f"RKG Divergence:      {result['rkg_result']}")
    print(f"Doctrine Status:     {result['governance_verdict'].get('status', 'blocked')}")
    print("==================================================")