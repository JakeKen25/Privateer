# Installing and running Privateer

Privateer runs from source on Python 3.11 or newer. It has no third-party
runtime dependencies: the desktop interface uses Tkinter, which is included in
the standard Windows and macOS Python installers.

> **Before editing a game:** close Rule the Waves 3 and make sure you know the
> location of the complete save-slot folder. Select the folder containing the
> `.bcs`, `.des`, and associated save files—not an individual file. Privateer
> creates a backup before an in-place save by default, but testing changes in a separate
> slot with **Save As** is still recommended.

## Windows installation

1. Install a 64-bit version of [Python](https://www.python.org/downloads/) that
   is version 3.11 or newer. In the installer:
   - enable **Add python.exe to PATH**;
   - leave **tcl/tk and IDLE** enabled so the desktop interface is available.
2. Download or clone this repository and open PowerShell in its root directory
   (the directory containing `pyproject.toml`).
3. Create and activate an isolated environment:

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, either use Command Prompt with
   `.venv\Scripts\activate.bat`, or run the virtual-environment Python directly
   in the commands below.
4. Install Privateer:

   ```powershell
   python -m pip install .
   ```
5. Start the desktop application:

   ```powershell
   privateer
   ```

   Alternatively, without activating the environment:

   ```powershell
   .\.venv\Scripts\python.exe -m privateer
   ```

## macOS or Linux installation

Python must include Tk support. On macOS, the python.org installer includes it.
Linux distribution packages commonly call it `python3-tk`; for example, on
Debian or Ubuntu it can be installed with `sudo apt install python3-tk`.

From the repository root, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
privateer
```

If the `privateer` launcher is not on `PATH`, use:

```bash
python -m privateer
```

## Loading and validating a save

In the desktop application:

1. Select **Browse…**.
2. Choose the complete RTW3 save-slot folder.
3. Confirm the displayed player nation and nation list.
4. Select **Validate** before making or saving changes.
5. Prefer **Save As…** for the first edited copy. **Save** validates the result
   and creates a retained backup before replacing edited files unless backup
   creation has been disabled in **Settings**. Settings can also place retained
   backups in a selected directory.

Validation can also be run without opening the GUI:

```bash
privateer "/path/to/save/Game7" --validate
```

On Windows, an example is:

```powershell
privateer "C:\Games\Rule the Waves 3\SaveGames\Game7" --validate
```

The command exits with status `0` for a valid save and `1` when critical
validation errors are found.

## Running the tests

Development tests require pytest, which is not needed to run Privateer:

```bash
python -m pip install pytest
python -m pytest -q
```

## Updating or uninstalling

After downloading a newer source version, activate the environment and run:

```bash
python -m pip install --upgrade .
```

To uninstall:

```bash
python -m pip uninstall privateer-rtw3
```

The `.venv` directory can then be deleted. This does not remove or change save
folders created by Privateer.

## Troubleshooting

- **`python` or `py` is not recognized:** reinstall Python and enable the PATH
  option, or invoke Python using its full path.
- **`No module named tkinter`:** install a Python build with Tcl/Tk support. On
  Windows, modify the Python installation and enable **tcl/tk and IDLE**; on
  Linux, install the distribution's `python3-tk` package.
- **No `.bcs` main save was found:** choose the save-slot directory rather than
  the parent `SaveGames` directory or an individual file.
- **The save is refused:** read the complete validation report. Privateer will
  not knowingly write a save with unresolved ship designs, conflicting IDs, or
  other critical integrity errors.
- **Unsupported save structure:** keep the original files unchanged and report
  the RTW3 version and anonymized section layout. Do not attempt to work around
  this warning with manual search-and-replace edits.
