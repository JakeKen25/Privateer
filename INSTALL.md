# Installing and running Privateer on Windows

Privateer supports 64-bit Windows 10 and Windows 11, the platforms supported by
Rule the Waves 3. Close Rule the Waves 3 before opening or saving a campaign in
Privateer.

## End-user package

1. Download `Privateer-<version>-Windows-x64.zip` from GitHub Releases.
2. Right-click the ZIP and select **Extract All**.
3. Keep every extracted file in the same folder. Do not move `Privateer.exe` by
   itself, and do not run it from inside the ZIP.
4. Open the extracted folder and run `Privateer.exe`.

The package contains Privateer, its required runtime files, `VERSION.txt`, and a
copy of the end-user instructions in `INSTALL.txt`. A separate Python
installation is not required.

If Windows SmartScreen identifies the unsigned beta as an unrecognized app,
confirm that the archive came from the `JakeKen25/Privateer` GitHub Releases page
before selecting **More info** and **Run anyway**.

## First use

1. Select **Browse**.
2. Choose the complete RTW3 save-slot folder, normally:

   ```text
   C:\Users\<name>\Documents\My Games\Rule the Waves 3\Save\GameX
   ```

   Choose the `GameX` folder containing the `.bcs`, `.des`, and associated save
   files rather than an individual file.
3. Confirm the displayed player nation and nation list.
4. Select **Validate** before making or saving changes.
5. Use **Save As** for the first edited test copy. An in-place **Save** validates
   the result and creates a retained backup by default.

Backup creation and its destination can be changed under **Settings**. Keep a
known-good campaign copy while using beta versions.

## Developer installation from Python source

The source version requires 64-bit Python 3.11 or newer for Windows. Tkinter is
included with the standard Python installer when **tcl/tk and IDLE** is enabled.

1. Install Python from [python.org](https://www.python.org/downloads/windows/).
   Enable **Add python.exe to PATH** and leave **tcl/tk and IDLE** enabled.
2. Clone or download this repository and open PowerShell in the directory that
   contains `pyproject.toml`.
3. Create and activate an isolated environment:

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt with
   `.venv\Scripts\activate.bat` or invoke `.venv\Scripts\python.exe` directly.
4. Install and launch Privateer:

   ```powershell
   python -m pip install .
   privateer
   ```

   You can also launch it directly from the repository:

   ```powershell
   python -m privateer
   ```

5. Confirm the installed version when needed:

   ```powershell
   privateer --version
   ```

## Command-line validation

Validate a save without opening the desktop interface:

```powershell
privateer "C:\Users\<name>\Documents\My Games\Rule the Waves 3\Save\Game7" --validate
```

The command exits with status `0` for a valid save and `1` when critical
validation errors are found.

## Running the tests

Development tests require pytest, which is not needed by the end-user package:

```powershell
python -m pip install pytest
python -m pytest -q
```

The test fixtures are stored under `developmentResources\exampleSaves`.

## Updating

For the end-user package, download the newer Windows ZIP and extract it to a new
folder. Privateer settings remain in `%APPDATA%\Privateer` and carry across
versions.

For a source installation, activate its environment and run:

```powershell
python -m pip install --upgrade .
```

## Uninstalling

Close Privateer and delete its extracted folder. To remove preferences too,
delete `%APPDATA%\Privateer`. Privateer does not remove game saves or backup
folders.

For a Python source installation, run:

```powershell
python -m pip uninstall privateer-rtw3
```

The `.venv` directory can then be deleted.

## Troubleshooting

- **`python` or `py` is not recognized:** reinstall Python and enable the PATH
  option, or invoke Python using its full path.
- **`No module named tkinter`:** modify the Windows Python installation and
  enable **tcl/tk and IDLE**.
- **No `.bcs` main save was found:** choose the complete `GameX` save-slot folder.
- **The save is refused:** read the complete validation report. Privateer will
  not knowingly write a save with unresolved ship designs, conflicting IDs, or
  other critical integrity errors.
- **Unsupported save structure:** keep the original files unchanged and report
  the RTW3 version and anonymized section layout. Do not work around the warning
  with manual search-and-replace edits.
