# Correspondence Engine SKG v1

Copyright (c) 2026 Spruked. All rights reserved.

This repository is proprietary and confidential. Use, copying, modification,
distribution, deployment, and commercial exploitation require prior written
permission. See [LICENSE](LICENSE) for the complete terms.

## Ownership model

Doctrine is the root-level constitutional authority for this repository.
The Correspondence Engine is the epistemic machinery that Doctrine constrains.
Divergence RKG provides post-cognitive quality control, and runtime code coordinates the governed stages.

```text
Doctrine
  |-- constrains EGF observation
  |-- constrains RKG divergence review
  |-- constrains SKG canonicalization
  |-- constrains runtime orchestration
  `-- authorizes or blocks consequential execution

EGF -> RKG -> SKG -> Doctrine -> execution decision
```

Doctrine is not owned by `correspondence_engine/`. No SKG, EGF, RKG, or runtime component may bypass
`doctrine.evaluator` before a consequential action such as a file mutation, system mutation, external send,
credential use, deployment, payment, or irreversible operation.

## Repository structure

```text
doctrine/                 Root governance and action-authority layer
correspondence_engine/    Epistemic and correspondence machinery
  Epistemic_Gravity_Field EGF observation layer
  skg                     Structured knowledge graph and AUI engine
divergence_rkg/           Divergence and quality-control layer
runtime/                  Master orchestration area
tests/                    Cross-stage validation scripts
Doctrine_*.md             Canonical doctrine source/reference
```

## Four-stage governed pipeline

1. **EGF** observes candidate text and returns field diagnostics.
2. **RKG** evaluates semantic divergence and quality-control risk.
3. **SKG** canonicalizes evidence into claims, atoms, vectors, and a judgment.
4. **Doctrine** verifies provenance, computes DDR, and returns `approved`, `escalate`, or `blocked`.

The evaluator does not execute actions. It returns an authorization decision for the execution layer.
Dangerous or consequential actions remain non-executing until the returned status is explicitly `approved`.

## Validation

Run the four-stage safe/dangerous action test from the repository root:

```powershell
python .\tests\test_four_stage_pipeline.py
```

The test exercises EGF and SKG locally, evaluates RKG divergence, and submits both action envelopes to the
Doctrine gate. The dangerous case is required to return `blocked`; the test never performs the proposed action.

Compile and whitespace checks:

```powershell
python -m compileall -q doctrine correspondence_engine tests
git diff --check
```

## Authority boundary

`doctrine/evaluator.py` is the current legislative gate. Its canonical hash constant remains a declared anchor
until the repository's ratified doctrine document is bound to a verified production hash. That boundary must be
resolved before treating the evaluator as production-grade cryptographic provenance enforcement.
