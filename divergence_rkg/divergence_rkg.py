import networkx as nx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances
from typing import Any, Dict, List, Optional

from app.core.context_packet import ContextPacket
from app.core.enums import GlyphStage
from app.memory.a_priori_vault import APrioriVault
from app.memory.a_posteriori_vault import APosterioriVault
from app.memory.reflection_vault import ReflectionVault
from app.memory.prior_decision_index import PriorDecisionIndex
from app.telemetry.glyph_trace import GlyphTrace


def _extract_texts(vault_data: Any) -> List[str]:
    """Pull string content out of whatever a vault returns."""
    texts = []
    if isinstance(vault_data, dict):
        for v in vault_data.values():
            if isinstance(v, str):
                texts.append(v)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, str):
                        texts.append(item)
                    elif isinstance(item, dict):
                        texts.append(str(item.get("content", item.get("text", ""))))
    elif isinstance(vault_data, list):
        for item in vault_data:
            if isinstance(item, str):
                texts.append(item)
            elif isinstance(item, dict):
                texts.append(str(item.get("content", item.get("text", ""))))
    return [t for t in texts if t.strip()]


class DivergenceRKG:
    """
    Relational Knowledge Graph that scores semantic divergence of a verdict
    against established vault memory. High divergence triggers recursion.

    Thresholds:
        score < 0.2  → stable, submit
        score < 0.5  → marginal, attempt vault justification
        score >= 0.5 → divergent, trigger recursion
    """

    def __init__(self, a_priori: APrioriVault, a_posteriori: APosterioriVault,
                 reflection: ReflectionVault, decision_index: PriorDecisionIndex,
                 trace: GlyphTrace = None):
        self.rkg = nx.DiGraph()
        self.vectorizer = TfidfVectorizer()
        self.trace = trace or GlyphTrace()

        self._vault_texts: Dict[str, List[str]] = {
            "a_priori": _extract_texts(a_priori.get_priors()),
            "a_posteriori": _extract_texts(a_posteriori.retrieve()),
            "reflection": _extract_texts({"reflection": reflection.fetch_related()}),
            "empirical_priors": _extract_texts(
                {"recent": [str(d) for d in decision_index.recent(20)]}
            ),
        }
        self._all_vault_docs: List[str] = sum(self._vault_texts.values(), [])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate_verdict(
        self,
        verdict_text: str,
        supporting_evidence: List[str] = None,
        harmonized: Dict[str, Any] = None,
        context: ContextPacket = None,
        max_recursions: int = 2,
    ) -> Dict[str, Any]:
        self._build_rkg(verdict_text, supporting_evidence or [])
        score = self.compute_divergence_score(verdict_text, supporting_evidence or [])

        if score < 0.2:
            return {"action": "submit", "score": score, "status": "stable"}

        if score < 0.5:
            justification = self._vault_justify(verdict_text)
            if justification["strength"] > 0.7:
                return {
                    "action": "submit_justified",
                    "score": score,
                    "justification": justification,
                }
            return self._trigger_recursion(
                verdict_text, supporting_evidence, harmonized, context, max_recursions
            )

        return self._trigger_recursion(
            verdict_text, supporting_evidence, harmonized, context, max_recursions
        )

    def compute_divergence_score(
        self, verdict_text: str, supporting_evidence: List[str] = None
    ) -> float:
        evidence = supporting_evidence or []
        all_texts = [verdict_text] + evidence + self._all_vault_docs

        if len(set(all_texts)) < 2:
            return 0.0

        self.vectorizer = TfidfVectorizer()
        self.vectorizer.fit(all_texts)

        verdict_emb = self.vectorizer.transform([verdict_text]).toarray()[0]
        vault_embs = [
            self.vectorizer.transform([t]).toarray()[0]
            for t in self._all_vault_docs
        ]

        if vault_embs:
            avg_vault_sim = float(
                1 - np.mean(cosine_distances([verdict_emb], vault_embs)[0])
            )
        else:
            avg_vault_sim = 0.5

        if evidence:
            evidence_embs = [self.vectorizer.transform([e]).toarray()[0] for e in evidence]
            avg_evidence_sim = float(
                1 - np.mean(cosine_distances([verdict_emb], evidence_embs)[0])
            )
        else:
            avg_evidence_sim = 1.0

        score = float(1 - (0.6 * avg_vault_sim + 0.4 * avg_evidence_sim))
        score = max(0.0, min(1.0, score))

        self.trace.record(
            "egf_convergence_update",
            {"stage": "divergence_score", "score": score, "verdict": verdict_text[:60]},
        )
        return score

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_rkg(self, verdict_text: str, evidence: List[str]) -> None:
        self.rkg.clear()
        self.rkg.add_node("verdict", text=verdict_text, type="verdict")
        for vault_type, entries in self._vault_texts.items():
            for i, entry in enumerate(entries):
                node_id = f"{vault_type}_{i}"
                self.rkg.add_node(node_id, text=entry, type=vault_type)
                self.rkg.add_edge("verdict", node_id, relation="evaluates_against")
        for i, ev in enumerate(evidence):
            node_id = f"evidence_{i}"
            self.rkg.add_node(node_id, text=ev, type="evidence")
            self.rkg.add_edge("verdict", node_id, relation="supported_by")

    def _vault_justify(self, verdict_text: str) -> Dict[str, Any]:
        supports = list(self.rkg.successors("verdict"))
        vault_supports = [
            n for n in supports if self.rkg.nodes[n]["type"] in self._vault_texts
        ]
        if not vault_supports:
            return {"strength": 0.0, "sources": []}

        strengths = [
            1.0 - self.compute_divergence_score(
                verdict_text, [self.rkg.nodes[n]["text"]]
            )
            for n in vault_supports
        ]
        return {
            "strength": float(np.mean(strengths)),
            "sources": [self.rkg.nodes[n]["text"][:60] for n in vault_supports[:3]],
        }

    def _trigger_recursion(
        self,
        verdict_text: str,
        supporting_evidence: Optional[List[str]],
        harmonized: Optional[Dict[str, Any]],
        context: Optional[ContextPacket],
        remaining: int,
    ) -> Dict[str, Any]:
        if remaining <= 0:
            self.trace.record(
                GlyphStage.EGF_CONVERGENCE_UPDATE,
                {"stage": "divergence_flag", "status": "unresolved", "verdict": verdict_text[:60]},
            )
            return {"action": "flag_ambiguous", "status": "needs_review", "score": 1.0}

        if harmonized is not None:
            harmonized.setdefault("flags", []).append(
                f"divergence_review:score_above_threshold"
            )

        from app.recursion.recursive_review import RecursiveReview
        reviewer = RecursiveReview()
        reviewed = reviewer.recheck(harmonized or {}, context.__dict__ if context else {})
        new_verdict = reviewed.get("selected", {}).get("text", verdict_text)

        return self.evaluate_verdict(
            verdict_text=new_verdict,
            supporting_evidence=supporting_evidence,
            harmonized=reviewed,
            context=context,
            max_recursions=remaining - 1,
        )
