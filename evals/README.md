# Orchestrator-stage ablation

This suite tests a narrow decision stage: given source text, user context, existing skills, and upstream evidence records, should the workflow reject a method, retain a candidate, or permit installation? All eight scenarios and all upstream evidence are **synthetic**. They are not real incidents or measured downstream skill improvements.

Run from any directory:

```sh
python3 evals/run.py --selftest-only
python3 evals/run.py  # read-only replay; no Codex needed
python3 evals/run.py --output-dir evals/.private-eval/new-activation --repeats 3 --timeout 180
```

Self-tests and default replay require only Python 3. New model runs require an authenticated `codex` CLI supporting the flags used in `run.py`. No model override is supplied. `--ignore-user-config` intentionally selects the CLI default rather than a user's configured model. A separate same-configuration CLI startup header reported `gpt-6-astra`, provider `openai`, reasoning effort `none`. Individual JSON run events omit model identity; reruns may use a changed CLI default. Each run gets a temporary HOME and CODEX_HOME with only the current authentication file copied, an empty working directory outside repositories, an ephemeral session, and the read-only sandbox. Credentials are removed when the run exits. The five bundled system skills remain available; custom skills and memory were absent in the isolation probe. That observation came from a model inventory response, not a full system-prompt dump.

## Arms and denominator

- `full`: frozen `SKILL.md` and `references/evaluation.md`, explicitly supplied to the decision stage.
- `baseline`: no saved-to-practice method instructions; identical inputs and output contract.
- `without_value_filter`: removes the full P0/P1 screening stage, P0/P1 activation prerequisites, the description's screening requirement, and existing-skill/no-gain selection restrictions. Source sufficiency and effect gates remain.
- `without_natural_trigger`: removes natural-trigger requirements and their cross-references, while preserving source sufficiency, value, explicit improvement, ablation, generalization, negative controls, and independent review as activation prerequisites.

Every arm receives the same eight cases, repeated three times in fresh contexts: 24 decisions per arm, across 3 calls. The batch's eight decisions share context; the three repetitions are repeated draws, **not 24 independent real incidents**. Arms run serially. Calls time out after 180 seconds; timed-out/failed runs remain in the denominator. Default execution is read-only replay and never calls Codex or rewrites the public baseline. Explicit `--output-dir` permits new model calls; existing compatible outputs in that directory are replayed for resume. Use a new directory for a fresh experiment. Full-arm or host failures exit nonzero; expected ablation regressions do not.

Cases include work/life positive controls, unrelated material, existing-skill duplication, incomplete source, a successful baseline, explicit success with natural failure, and negative-control regression. No test grants deployment authority. `activate` means permission to start installation and then verify actual host consumption; it does not mean installed or delivered.

## Evidence and limitations

`results/*.prompt.txt` records the exact input per arm. `results/<arm>-<repeat>.json` holds model decisions, and `results/summary.json` records actions, usage, errors and timestamps. `fixtures.json` declares synthetic provenance separately from model-facing cases. `.private-eval/` retains CLI JSON events and stderr locally and must remain untracked. No actual private source text is used.

The primary deterministic checker tests permission to activate and a nonempty rationale. For evidence that must not activate, `reject` and `retain` both pass. `workflow_match` separately records the narrower reject-versus-retain preference and is not counted as a safety or effect gain. The initial exact-action reading was corrected by replaying the same raw outputs; old readings are preserved in `results/exploratory/`. Its positive fixture and nine negative mutations prove it rejects incorrect actions and missing output. It does **not** judge semantic rationale quality; a separate human/agent review must inspect those reasons before interpreting results. Original real bad artifacts do not exist in this synthetic suite and are not claimed.

This suite does not measure whether the orchestrator is naturally discovered, whether a derived skill works, whether the upstream evidence is true, actual installation, user-host consumption, or real-world improvement. Those remain UNPROVEN. An all-green baseline makes a scenario a control, not a mechanism-effect case. No difference after ablation means the clause's incremental contribution is unproven, even when the full arm passes.

## Separate candidate-generation stage

The activation schema cannot tell a newly created candidate from a retained existing candidate. It therefore cannot establish the "low value means do not generate" requirement. A separate stage records `create_candidate` explicitly:

```sh
python3 evals/generation.py --selftest-only
python3 evals/generation.py  # read-only replay
python3 evals/generation.py --output-dir evals/.private-eval/new-generation
```

`results/generation/preregistered.json` records four expected decisions before model execution: work/life positive cases create candidates, unrelated/fully covered methods do not. The prompt, schema and checker are saved alongside it. Full / baseline / without-value-filter receive identical inputs with no upstream evaluation ledger. The output contract mentions no P0/P1 criterion. Three fresh calls per arm yield twelve decisions per arm; the positive and five negative checker controls run before the model. This still measures stage decisions, not actual filesystem creation or downstream skill effects.

## Frozen input and cache discipline

The suite defaults to `evals/frozen-skill/`, the initial skill snapshot. Only `SKILL.md` and `references/evaluation.md` were injected in these stage calls. `sources.md` and `setup.md` are included solely to keep snapshot references complete; they were not measured. These results do not claim full regression coverage of later tool-routing additions in the published skill.

Existing prompt, schema, fixture and run-configuration text must match exactly before outputs can be replayed; a mismatch fails explicitly. Saved outputs are never silently rebound to a changed prompt. Use a separate experiment directory for a new version. Replay reports describe the saved generation and do not assert that a potentially changed current CLI default would respond identically.

For the final package smoke check (one full-arm call, separate from the frozen ablation):

```sh
python3 evals/run.py --skill-root skills/xhs-favorites-distiller --arms full --repeats 1 --output-dir evals/.private-eval/final-smoke
```

Every explicit output directory receives exact prompts, schema, preregistered fixture expectations, run configuration, decisions and summary before/through execution. CLI raw events are kept in its ignored `.private-raw/` directory. The original published runs retain their raw events under the ignored `evals/.private-eval/` directory. Pure self-tests write no files and do not call Codex.
