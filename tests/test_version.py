import subprocess
import re
import sys
import tomllib
from pathlib import Path

import privateer
from privateer.version import display_version


def test_package_and_project_versions_match():
    project = Path(__file__).parents[1]
    metadata = tomllib.loads((project / "pyproject.toml").read_text(encoding="utf-8"))
    assert re.fullmatch(r"\d+(?:\.\d+){2,3}", privateer.__version__)
    assert metadata["project"]["version"] == privateer.__version__


def test_cli_reports_version():
    result = subprocess.run(
        [sys.executable, "-m", "privateer", "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == f"Privateer {display_version()}"

