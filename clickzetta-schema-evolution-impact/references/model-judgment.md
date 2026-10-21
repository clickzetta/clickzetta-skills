# Optional Semantic Judgment

Models interpret supplied evidence; they do not discover database facts or authorize changes.

## Availability and Routing

1. Use queries/rules first; call a model only for unresolved semantic work. A no-model/no-external-data request takes precedence.
2. Discover already exposed tools/gateway models or configured clients without reading/printing credentials. Installed SDK or configured order alone is not service availability.
3. Prefer configured, available TypeSafe/Jev. If absent, skip it. On temporary failure use bounded environment-supported retry, then try configured low-cost Flash-class alternatives. Confirm actual model IDs from current capabilities.
4. Do not ask again solely because Jev is absent. Do not provision credentials, install clients, buy service, launch subagents, bypass external-data restrictions, or silently upgrade to an expensive model.
5. If models are unavailable, continue rules/current-agent evidence analysis and route unresolved items to human confirmation. Missing model access is not missing database data.

Cache judgments by evidence/question/model version. Unknown engine rules cannot be guessed into existence by switching models. Conflicting model conclusions require evidence review.

## State and Two Rounds

Use consumer + column + branch/expression as the unit. Include complete relevant SQL/CTEs, source schemas, root/direct identity, candidate expression IDs/locations, evidence completeness/version, and change scope.

Round 1 asks independent facts:
- origin: raw_only / raw_mixed / other / unknown;
- millisecond conversion, duration, offset;
- target participation in JOIN/selection/window keys;
- unchanged direct projection, separately from declared output type.

Round 2 supplies checked round-1 results, the explicit migration plan, and authoritative engine rules, then classifies execution_failure / silent_result_change / unaffected / insufficient_evidence.

Questions in one System One call are independent: a later question does not automatically receive another answer. Batch independent facts; combine them in code or a subsequent round.

## TypeSafe/Jev Example

Verify current [Python SDK](https://docs.typesafe.ai/sdk/python), [Noul](https://docs.typesafe.ai/primitives/noul), [State](https://docs.typesafe.ai/concepts/state), [Confidence](https://docs.typesafe.ai/confidence), and [Models](https://docs.typesafe.ai/models) documentation when integrating.

```python
from typesafe_sdk import Choice, Noul

def inspect_column(client, state, model_id):
    return client.system_one(
        model=model_id,
        state=state,
        questions={
            "origin": Choice(
                instructions=(
                    "Trace the target output to root_object through aliases, "
                    "CTEs and positional UNION branches. Use supplied SQL only."
                ),
                criteria={
                    "raw_only": "Every branch originates in the root target column.",
                    "raw_mixed": "Some branches use it; other branches use other sources.",
                    "other": "Other sources or other fields generate this output.",
                    "unknown": "Definitions or source schemas are insufficient.",
                },
            ),
            "ms_conversion": Noul(instructions=(
                "Is the target-origin column interpreted as milliseconds and "
                "converted to seconds, e.g. divided by 1000? Exclude other "
                "sources' same-named fields and unrelated numeric scaling."
            )),
            "ms_duration": Noul(instructions=(
                "Is a difference involving the target-origin column interpreted "
                "as integer milliseconds, e.g. divided by 3600000?"
            )),
            "passthrough": Noul(instructions=(
                "Is this branch's output only a direct input-column reference "
                "or rename? Exclude casts, arithmetic, formatting, concatenation "
                "and aggregation. This does not establish UNION common type."
            )),
        },
    )
```

Noul returns P(yes), read from response.nouls[id].noul; it has no separate confidence. Never use bool(p). After checking required evidence, starting thresholds might be >=0.95 yes, <=0.05 no, otherwise review. These are not validated domain thresholds: calibrate on labeled SQL and retain unknown for missing evidence.

Choice exposes choice, probabilities, and confidence through response.choices[id]. Record the actual response.model and fix a tested model ID for reproducibility. Confidence summarizes a distribution; it is not evidence completeness or an engineering correctness guarantee.

## Low-cost Fallback Contract

Use the same evidence and two-round questions through the provider's supported structured-output interface, not the TypeSafe SDK payload.

Return individual allowed values, not prose:
- origin: raw_only / raw_mixed / other / unknown;
- ms_conversion, ms_duration, passthrough: yes / no / unknown;
- impact in round 2: the four impact labels above;
- evidence_ids: IDs from supplied candidates only;
- missing_evidence: explicit gaps;
- probabilities: null unless the interface supplies a validated probability contract.

Validate JSON shape, enums, and candidate references. Allow one repair attempt for invalid output; otherwise unknown. A model's self-reported certainty is not Jev's Noul or TypeSafe confidence. Do not invent probabilities to satisfy a uniform schema.

Generate candidate fragments deterministically or with an SQL parser. A Choice can select a candidate ID (with "none"/"insufficient" options), followed by a support-verification question. Do not ask Noul to produce free-text quotes.

## Recording and Evaluation

Log provider/model, evidence/question hashes and versions, real requests/retries/successes/errors, categories and actual returned probabilities. One request with ten questions is one request. Rule fallback and mocks are not model calls.

Evaluate complete anonymized/synthetic SQL and counterexamples before sending authorized business evidence. Assess providers and languages separately; do not assume equivalent probability calibration or transplant Jev thresholds to Flash. See [acceptance](acceptance.md). No model client is bundled or automatically configured by this skill.
