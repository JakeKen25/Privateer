# Project workflow

The user requires all completed changes to this project to be committed and pushed
to GitHub so previous versions remain available for reverting.

- Repository: https://github.com/JakeKen25/Privateer
- Continue development on `develop` unless the user requests another branch.
- Keep `main` limited to tested release commits. Promote changes from `develop`
  to `main` only when the user requests a stable publication.
- Read the current remote branch before changing it and preserve unrelated work.
- Make descriptive commits for completed changes, run relevant checks, and push.
- Preserve history: do not force-push or rewrite published commits. Use revert commits for rollbacks.
- Verify the remote commit after pushing and report its link and any validation limitations.
- If pushing is blocked, retain the local changes and clearly report that GitHub is not yet updated.
- Never commit installed game data, live saves, credentials, virtual environments, or build caches.

## Wiki maintenance

All changes to Privateer must be reflected in the project wiki:
https://github.com/JakeKen25/Privateer/wiki

- Update the affected wiki pages as part of the same task, including behavior,
  controls, workflows, limitations, fixes, and validation status.
- The wiki is the primary end-user manual. Manager pages describe the current
  published release for new users. Keep development logs, test counts, raw save
  fields and research history in repository guides, not user-facing pages.
  Include only limitations and changes that affect users; preserve screenshots.
- Verify the published wiki updates before reporting a change complete. If wiki
  publication is blocked, retain the prepared edits and explicitly report the gap.
- Record internal-only changes in repository documentation, not the user wiki.
