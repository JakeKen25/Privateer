from pathlib import Path

import privateer


ROOT = Path(__file__).parents[1]


def test_end_user_instructions_cover_portable_install_and_save_safety():
    instructions = (ROOT / "packaging" / "END_USER_INSTALL.txt").read_text(encoding="utf-8")
    for expected in (
        f"PRIVATEER {privateer.__version__}",
        "No separate Python installation is required",
        "Do not move only",
        "Close Rule the Waves 3",
        "Use Validate",
        "Save As",
        "%APPDATA%\\Privateer",
    ):
        assert expected in instructions


def test_release_workflow_builds_only_the_portable_archive():
    workflow = (ROOT / ".github" / "workflows" / "windows-release.yml").read_text(encoding="utf-8")
    build = (ROOT / "packaging" / "build_windows_release.ps1").read_text(encoding="utf-8")
    assert 'tags:\n      - "v*"' in workflow
    assert '"packaging/RELEASE_VERSION"' in workflow
    assert '- "main"' in workflow
    assert '"packaging/RELEASE_CHANNEL"' in workflow
    assert '"packaging/RELEASE_NOTES.md"' in workflow
    assert "gh release create" in workflow
    assert 'if ($isBeta)' in workflow
    assert '--prerelease' in workflow
    assert "--notes-file" in workflow
    assert "--prerelease=false" in workflow
    assert "refs/heads/main" in workflow
    assert "refs/heads/Codex" not in workflow
    assert "release/Privateer-*-Windows-x64.zip" in workflow
    assert "END_USER_INSTALL.txt" in build
    assert "--onedir" in build
    assert "--windowed" in build
