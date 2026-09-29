# Design decisions

The agent with the user's context owns value, priority and activation decisions. Code handles stable identities, data revisions, atomic imports and installation. An independent reviewer can challenge conclusions but does not silently become the user's decision maker.

The normal work path only sees relevant installed skills. Collection, candidate creation and evaluation happen during an explicit or authorized scheduled run. No browser-monitoring daemon, global prompt rewriting or per-delivery acknowledgement system is needed.

One reading item is not one skill. A useful candidate needs a concrete recurring failure, a changed action and an observable result; related sources should improve one existing method. Unverified candidates stay outside the host's discovery directory.

## Prior art

- [Codex skills](https://developers.openai.com/codex/skills/): concise descriptions and on-demand instructions. Installation and natural invocation are separate evidence.
- [Readwise Reader API](https://readwise.io/reader_api): stable document identities and incremental pagination. These API capabilities must not be assumed for private social-media collections.
- [Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices): task-specific examples, predefined criteria and paired comparisons. This project additionally separates method effectiveness from natural invocation.

The local inbox compares stored values directly. It keeps the current note revision and current assessment; it does not assign semantic priority or install skills. A source revision invalidates its previous assessment, while unchanged imports cost no new model evaluation.

The public repository contains original code, instructions and synthetic examples. Private source text, account URLs, personal profiles, authentication material and unfiltered CLI logs stay outside public artifacts.
