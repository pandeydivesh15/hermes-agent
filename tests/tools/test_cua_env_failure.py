"""Credential-filter failures must prevent driver subprocess launches."""

from unittest.mock import Mock

import pytest


@pytest.mark.parametrize("entrypoint", ["probe", "permissions"])
def test_filter_failure_prevents_child_launch(monkeypatch, entrypoint):
    from tools.computer_use import cua_backend, permissions
    from tools.environments import local

    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-audit-key")

    def fail_filter(env):
        raise RuntimeError("credential filter unavailable")

    monkeypatch.setattr(local, "_sanitize_subprocess_env", fail_filter)
    run = Mock()
    monkeypatch.setattr(cua_backend.subprocess, "run", run)
    launch = (
        lambda: cua_backend._run_driver("cua-driver", "doctor", timeout=1)
    ) if entrypoint == "probe" else (
        lambda: permissions._run("cua-driver", "doctor", timeout=1)
    )
    with pytest.raises(RuntimeError, match="credential filter unavailable"):
        launch()
    run.assert_not_called()


def test_cua_telemetry_opt_in_is_overridden(monkeypatch):
    from tools.computer_use import cua_backend

    monkeypatch.setattr(
        cua_backend, "_computer_use_cfg", lambda: {"cua_telemetry": True},
    )
    env = cua_backend.cua_driver_child_env({
        "CUA_DRIVER_RS_TELEMETRY_ENABLED": "1",
    })
    assert env["CUA_DRIVER_RS_TELEMETRY_ENABLED"] == "0"
