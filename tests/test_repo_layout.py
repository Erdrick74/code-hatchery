from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_scripts_pass_shell_syntax_check() -> None:
    scripts = [
        ROOT / "install.sh",
        ROOT / "uninstall.sh",
        ROOT / "scripts" / "code-hatchery",
        ROOT / "scripts" / "code-hatchery-gui-gtk.py",
        ROOT / "scripts" / "code-hatchery.cli",
        ROOT / "scripts" / "create-project.sh",
    ]
    subprocess.run(["bash", "-n", *map(str, scripts)], check=True)


def test_python_github_ready_template_exists() -> None:
    template = ROOT / "templates" / "python-github-ready"
    assert template.is_dir()
    assert (template / "pyproject.toml").is_file()
    assert (template / "LICENSE").is_file()
