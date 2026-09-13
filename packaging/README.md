# Windows release packaging

The GitHub Actions workflow in `.github/workflows/windows-release.yml` builds
the end-user Windows package. A manual workflow run saves the ZIP as a workflow
artifact. Pushing a version tag such as `v0.9.0` also creates a GitHub Release
and attaches the ZIP.

The tag must match `privateer.version.__version__`. Update the version and the
heading and archive name in `END_USER_INSTALL.txt` before making a new release.

To build the same package locally from the repository root:

```powershell
python -m pip install "pyinstaller>=6.0,<7"
.\packaging\build_windows_release.ps1 -PythonExe python
```

The resulting archive is written to `release/`. It contains the standalone
application, its private runtime, `VERSION.txt`, and the end-user `INSTALL.txt`.
It intentionally excludes the source tree, tests, examples, and developer
documentation.
