# Contributing to Privateer

Privateer welcomes suggestions, bug reports, file-format research, and proposed
code changes. The project owner currently retains sole publishing and merge
authority.

## Suggest an idea or report a problem

Open a GitHub issue and use the relevant template. Explain the expected behavior,
what happened instead, and the Rule the Waves 3 version involved. Remove personal
information from logs and examples. Never upload a live campaign or installed
game data unless the project owner specifically asks for an anonymized excerpt.

## Propose a code change

1. Fork the repository.
2. Create a focused `feature/<name>` or `fix/<name>` branch from `develop`.
3. Make the change and add focused tests or repeatable format evidence where
   appropriate.
4. Run `python -m pytest -q` on Windows.
5. Open a pull request into `develop` and complete the pull-request checklist.

Do not target `main`. The owner reviews proposed changes and decides whether and
when to merge them. A submitted pull request does not grant permission to publish
a release or change the stable branch.

## Repository safety

- Do not commit live save folders, installed game files, credentials, personal
  data, virtual environments, build caches, or generated release archives.
- Preserve unknown RTW3 fields and file formatting unless their meaning and
  replacement behavior are validated.
- Keep changes narrowly scoped and document format assumptions.
- Follow [BRANCHING.md](BRANCHING.md) for the development and release flow.
