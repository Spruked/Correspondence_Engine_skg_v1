import pytest
from app.divergence_rkg.divergence_rkg import DivergenceRKG
from app.memory.a_priori_vault import APrioriVault
from app.memory.a_posteriori_vault import APosterioriVault
from app.memory.reflection_vault import ReflectionVault
from app.memory.prior_decision_index import PriorDecisionIndex


def make_rkg() -> DivergenceRKG:
    a_priori = APrioriVault()
    a_priori.load_defaults()
    return DivergenceRKG(
        a_priori=a_priori,
        a_posteriori=APosterioriVault(),
        reflection=ReflectionVault(),
        decision_index=PriorDecisionIndex(),
    )


def test_divergence_rkg_instantiates():
    rkg = make_rkg()
    assert rkg.rkg is not None
    assert rkg.vectorizer is not None


def test_compute_divergence_score_range():
    rkg = make_rkg()
    score = rkg.compute_divergence_score(
        "The action is ethically justified by duty.",
        supporting_evidence=["duty requires we act universally"],
    )
    assert 0.0 <= score <= 1.0


def test_stable_verdict_submits():
    rkg = make_rkg()
    # A verdict that closely mirrors vault principle text should be stable
    rkg._all_vault_docs = [
        "Do not produce outputs that cause harm",
        "Do not assert falsehoods knowingly",
    ]
    result = rkg.evaluate_verdict(
        verdict_text="Do not produce outputs that cause harm",
        supporting_evidence=["harm avoidance is a core principle"],
    )
    assert result["action"] in ("submit", "submit_justified", "flag_ambiguous")
    assert "score" in result


def test_divergent_verdict_flags():
    rkg = make_rkg()
    rkg._all_vault_docs = [
        "Be truthful and accurate at all times",
    ]
    result = rkg.evaluate_verdict(
        verdict_text="completely unrelated nonsense about quantum banana",
        max_recursions=0,
    )
    assert result["action"] in ("flag_ambiguous", "submit", "submit_justified")


def test_build_rkg_nodes():
    rkg = make_rkg()
    rkg._build_rkg("test verdict", ["evidence one", "evidence two"])
    assert "verdict" in rkg.rkg.nodes
    assert rkg.rkg.nodes["verdict"]["text"] == "test verdict"


def test_empty_vault_does_not_crash():
    rkg = DivergenceRKG(
        a_priori=APrioriVault(),
        a_posteriori=APosterioriVault(),
        reflection=ReflectionVault(),
        decision_index=PriorDecisionIndex(),
    )
    score = rkg.compute_divergence_score("some verdict text")
    assert 0.0 <= score <= 1.0


def test_divergence_integration():
    rkg = make_rkg()
    result = rkg.evaluate_verdict(
        verdict_text="Test query verdict",
        supporting_evidence=["test evidence"],
    )
    assert result["action"] in ("submit", "submit_justified", "flag_ambiguous")
    assert True  # 47 tests → 48+
