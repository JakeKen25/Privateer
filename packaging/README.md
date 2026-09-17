# Windows release packaging

The GitHub Actions workflow in `.github/workflows/windows-release.yml` builds
the end-user Windows package. A manual workflow run saves the ZIP as a workflow
artifact. Changing `RELEASE_VERSION` or `RELEASE_CHANNEL` on `main` creates or
updates that version's release and attaches the ZIP. The `stable` channel uses
`v<version>` and the `beta` channel uses `v<version>-beta` as a prerelease.
Pushing a matching channel tag also builds and attaches the package.

`RELEASE_VERSION` and any pushed tag must match
`privateer.version.__version__`. Update the package version,
`RELEASE_VERSION`, `RELEASE_NOTES.md`, and the heading and archive name in
`END_USER_INSTALL.txt` before making a new release.

Release work is prepared and tested on `develop`, then merged into `main`.
Ordinary pushes to `develop` never publish an end-user release.

To build the same package locally from the repository root:

```powershell
python -m pip install "pyinstaller>=6.0,<7"
.\packaging\build_windows_release.ps1 -PythonExe python
```

The resulting archive is written to `release/`. It contains the standalone
application, its private runtime, `VERSION.txt`, and the end-user `INSTALL.txt`.
It intentionally excludes the source tree, tests, examples, and developer
documentation.
