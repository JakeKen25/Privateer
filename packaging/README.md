# Windows release packaging

The GitHub Actions workflow in `.github/workflows/windows-release.yml` builds
the end-user Windows package. A manual workflow run saves the ZIP as a workflow
artifact. Changing `RELEASE_VERSION` on the `Codex` branch creates or updates
that version's prerelease and attaches the ZIP. Pushing a matching version tag
also builds and attaches the package.

`RELEASE_VERSION` and any pushed tag must match
`privateer.version.__version__`. Update the package version,
`RELEASE_VERSION`, and the heading and archive name in
`END_USER_INSTALL.txt` before making a new release.

To build the same package locally from the repository root:

```powershell
python -m pip install "pyinstaller>=6.0,<7"
.\packaging\build_windows_release.ps1 -PythonExe python
```

The resulting archive is written to `release/`. It contains the standalone
application, its private runtime, `VERSION.txt`, and the end-user `INSTALL.txt`.
It intentionally excludes the source tree, tests, examples, and developer
documentation.
