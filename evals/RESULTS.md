# Stage results — 2026-09-15 UTC

**PASS for the full frozen skill's synthetic activation contract; real-world skill effect remains UNPROVEN.** The full method did not outperform the unassisted baseline on the primary activation outcome. Removing the natural-trigger requirement caused premature permission to install in one repeated scenario.

## Apparatus

Codex CLI 0.153.4, no model override, ignored user configuration, ephemeral read-only sessions, separate temporary HOME/CODEX_HOME and empty repository-external cwd per call. A same-configuration startup header identified gpt-6-astra / openai / reasoning effort none. Five bundled system skills remained; an inventory probe reported no custom skills, saved-to-practice method, memory or personal preferences. The inventory is a model self-report, not a complete system-prompt capture.

Only frozen `SKILL.md` and `references/evaluation.md` were explicitly injected. This is a decision-stage test, not natural discovery of the orchestrator. Source bodies, user pain points, existing skills and upstream evidence are synthetic public fixtures. Their evaluation fields are supplied inputs, not measured skill outcomes. The frozen snapshot predates the final package's local-tool routing changes.

## Activation permission

| Arm | Correct permission decisions | Premature activation | Repetitions |
|---|---:|---:|---:|
| Full frozen method | 24/24 | 0/18 non-activation cases | 3 |
| No-method baseline | 24/24 | 0/18 | 3 |
| Without value filter | 24/24 | 0/18 | 3 |
| Without natural-trigger requirement | 21/24 | 3/18 | 3 |

Each arm has eight scenarios repeated three times in fresh contexts. Decisions within a batch share context, and repetitions are not independent real incidents. All calls completed; no failures or timeouts were excluded.

The difference is confined to `explicit_only`: explicit method use improves the supplied outcome, while natural discovery and unprompted output improvement are false. Full and baseline both withheld activation in 3/3 draws. Removing the natural-trigger requirement permitted it in 3/3 draws. This supports retaining that requirement **within this workflow**; it does not establish superiority to the baseline, actual natural triggering, or downstream user benefit.

The value-filter arm cannot independently establish "do not generate low-value candidates": its output schema describes activation dispositions and does not distinguish new creation from retaining an existing candidate. A separate preregistered generation-stage test covers that dimension.

## Evaluator corrections and exploratory evidence

The initial checker treated `reject` versus `retain` as a failure even when both correctly withheld activation. That was an evaluator error. The final primary criterion accepts both, retaining `workflow_match` only as a descriptive difference. The original readings remain in `results/exploratory/initial-exact-action-summary.json`; all raw decisions were replayed without model reruns to correct this reading.

The first natural-trigger ablation removed whole lines and accidentally removed neighboring guidance. It was replaced with precise phrase edits before drawing a conclusion. Its three outputs, prompt and diff remain in `results/exploratory/`, separately labeled and excluded from the formal table. All three broad-deletion runs had withheld premature activation; they are not hidden or pooled with the corrected arm.

Checker validation: one correct activation artifact and nine incorrect/missing-output controls passed self-test. Eight unit regressions protect checker controls, semantically equivalent non-activation, duplicate output rejection, cache-input mismatch handling, low-value generation rejection, CLI-free self-tests, and correct failure exit codes. Reason semantics need independent review; action JSON alone is not proof of reasoning quality.

## Boundaries

No real incident qualification, second-host baseline, derived-skill generation/effect experiment, actual installation, actual user-host consumption, or offline behavioral improvement was measured. These remain UNPROVEN. No prompt was tuned to force baseline failure; the all-green baseline remains a control result.

## Candidate generation

The preregistered generation stage explicitly asks whether to create a candidate or candidate revision, before evaluation and installation. Four synthetic work/life positive and negative cases were repeated three times per arm.

| Arm | Correct create / do-not-create decisions | Low-value or duplicate candidates created |
|---|---:|---:|
| Full frozen method | 12/12 | 0/6 |
| No-method baseline | 12/12 | 0/6 |
| Without value filter | 12/12 | 0/6 |

All nine calls completed. The full method respects the generation contract, but the value-filter clause has **no demonstrated incremental contribution** on these fixtures. No actual candidate files were created by this stage test. The initial activation-only schema limitation is not retroactively treated as generation evidence.

## Final package smoke

After local-tool/data-directory routing was added, the current published package's actual `SKILL.md` plus `references/evaluation.md` received one full-arm call using the original eight activation fixtures: **8/8** correct decisions. Its exact prompt, output and separate summary are in `results/final-smoke/`. This is a small semantic regression check, not a rerun of the four-arm experiment and not an execution test of the local tools.

## Reproduction

Default `python3 evals/run.py` and `python3 evals/generation.py` replay the saved results read-only, with no Codex dependency. New paid calls require an explicit `--output-dir`; see README. Eight harness unit tests pass, including PATH-without-Codex self-tests and exit-code behavior. Full failures and infrastructure failures return nonzero; expected ablation degradation remains reported without failing the command.
