# Project workflow

The user requires all completed changes to this project to be committed and pushed
to GitHub so previous versions remain available for reverting.

- Repository: https://github.com/JakeKen25/RTW3_Privateer
- Continue development on the existing Codex branch unless the user requests another branch.
- Read the current remote branch before changing it and preserve unrelated work.
- Make descriptive commits for completed changes, run relevant checks, and push.
- Preserve history: do not force-push or rewrite published commits. Use revert commits for rollbacks.
- Verify the remote commit after pushing and report its link and any validation limitations.
- If pushing is blocked, retain the local changes and clearly report that GitHub is not yet updated.
- Never commit installed game data, live saves, credentials, virtual environments, or build caches.
