"""Zsh activation selects the runtime and restores the caller's environment."""

import shutil
import subprocess
from pathlib import Path

import pytest

from tests.pm.activation_support import REPO_ROOT, fake_store, sync_checkout


@pytest.mark.platforms("posix")
def test_zsh_bootstrap_ignores_missing_binary_layouts(tmp_path: Path):
    zsh = shutil.which("zsh")
    if zsh is None:
        pytest.skip("zsh is not installed")
    runtime = tmp_path / "runtime with spaces"
    python = runtime / "python-fixture" / "bin" / "python3"
    python.parent.mkdir(parents=True)
    python.touch(mode=0o755)
    script = '''
        export HERMES_RUNTIME_DIR="$1" HERMES_HOME="$2"
        source "$3/scripts/_activation.sh"
        hermes_bootstrap_python "$2"
    '''
    run = subprocess.run(
        [zsh, "-f", "-c", script, "bootstrap-test", str(runtime),
         str(tmp_path / "absent"), str(REPO_ROOT)],
        capture_output=True, text=True, timeout=10, check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert run.stdout.strip() == str(python)


@pytest.mark.platforms("posix")
def test_zsh_activation_and_reactivation_restore_environment(tmp_path: Path):
    zsh = shutil.which("zsh")
    if zsh is None:
        pytest.skip("zsh is not installed")
    root, env = sync_checkout(tmp_path)
    fake_store(tmp_path)
    script = '''
        set -e
        export PYTHONPATH=caller-original VIRTUAL_ENV=caller-venv
        original_path="$PATH"
        original_options=$(setopt)
        source "$1/activate"
        test "$HERMES_PM_ACTIVATE_CANARY" = env-ok
        source "$1/activate"
        deactivate
        test "$PATH" = "$original_path"
        test "$PYTHONPATH" = caller-original
        test "$VIRTUAL_ENV" = caller-venv
        test -z "${HERMES_PM_ACTIVATE_CANARY+set}"
        test -z "${__HERMES_ACTIVATED+set}"
        test "$(setopt)" = "$original_options"
        printf restored
    '''
    run = subprocess.run(
        [zsh, "-f", "-c", script, "activation-test", str(root)],
        cwd=tmp_path, env=env, capture_output=True, text=True,
        timeout=40, check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert run.stdout == "restored"
