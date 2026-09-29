# Validation and ablation

## Evidence boundaries

This project distinguishes five claims:

1. The local import and install tools execute correctly.
2. A model following the workflow makes appropriate source/value/activation decisions.
3. Removing a component causes a meaningful change on the same inputs.
4. A host discovers and invokes the skill without the user naming it.
5. A method learned from real saved material improves the user's next real task.

Passing an earlier layer does not prove a later layer. Synthetic scenarios are labeled synthetic. Repeated draws from one scenario are not additional real users or real failures. A safe alternative decision is not a harmful error merely because its wording differs.

## Local deterministic checks

```sh
python3 -m unittest discover -s tests -v
```

These tests use disposable directories and original synthetic reading. They cover import → read → assess through the CLI, duplicate imports, changed content, stale judgments, independent source identities, incomplete data, batch validation before writes and installation backups outside discovery directories.

## Model comparisons

See [the runnable model harness](../evals/README.md) for frozen inputs, arms, commands, checker controls and actual results. The initial comparison uses baseline, complete workflow, removal of value selection and removal of the natural-invocation requirement. Models receive the same synthetic scenarios; inputs do not contain private saved articles or user histories.

The checker verifies structured decisions, not the truth of a real-world user benefit. Decisions and reasons also need independent semantic review. A supplied fixture saying a trial passed tests orchestration of that evidence; it does not constitute that trial having run.

## Release interpretation

The source adapter contract and local-export workflow can be tested without private platform access. Platform-specific live acquisition still requires the account owner to sign in and grant the chosen scope. Failed authentication is a collection failure, never an empty collection.

For a learned skill to become active, its own real baseline/experiment, step removal, natural invocation, cross-task and negative-control evidence must satisfy the installed workflow. Publishing this toolkit does not activate a learned method or assert end-to-end personal effectiveness.
