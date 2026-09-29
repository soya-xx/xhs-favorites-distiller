# Local authenticated collection run · 2026-09-16

## Result

PASS for the collection-to-assessment path on one local Codex installation using an authenticated Xiaohongshu session in ego lite. This is a bounded manual Agent run, not an unattended scheduler test.

- Observed the first 10 collection cards; opened 2 technical notes.
- Read all 3 images of one note. The second note was only partially read and explicitly imported with `complete: false`.
- Ran the installed `inbox.py` against the private data directory: ingest, get, assess, get, repeated ingest, pending.
- Imported 2 records and verified 2/2 decisions by reading them back. One was skipped because no concrete P0/P1 workflow change was established; the incomplete note was recorded as needing evidence.
- Reimport returned 0 inserted, 0 updated, 2 unchanged. Neither assessed record reappeared in the pending queue.
- Created and activated 0 derived skills. No favorites were changed and no recurring task was created.

The login-required state was observed before the user signed in; it was not treated as an empty collection. After sign-in the same source became readable.

## Evidence boundary

Raw notes, account identifiers, URLs containing session parameters, and local execution logs remain private. This report records the observed scope and counts; it is not a publicly reproducible dataset or an independent effect evaluation. Public synthetic fixtures remain available for reproducing local-tool checks.

Real downstream improvement, derived-skill ablation, unattended collection, and WeChat ingestion remain UNPROVEN by this run. The release remains experimental.
