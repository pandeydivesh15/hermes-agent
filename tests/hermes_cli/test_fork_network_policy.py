"""Fork policy must override user opt-ins before network activity."""

from unittest.mock import Mock

import pytest


def test_passive_updates_do_not_probe_checkout(monkeypatch, tmp_path):
    from hermes_cli import source_check

    probe = Mock(side_effect=AssertionError("passive probe ran"))
    monkeypatch.setattr(source_check, "_read_checkout", probe)
    monkeypatch.setattr(
        source_check, "_unsupported_reason", lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "hermes_cli.config.require_readable_config_before_write",
        lambda *a: {"updates": {"check": True}},
    )
    result = source_check.check_for_updates(
        install_root=tmp_path, home=tmp_path, passive=True, force=True,
    )
    assert result["reason"] == "disabled"
    probe.assert_not_called()


def test_shared_metrics_opt_in_cannot_enable_transmission(monkeypatch):
    from hermes_cli.observability.shared_metrics_send_config import (
        resolve_send_config,
    )
    from hermes_cli.observability import shared_metrics_sender

    config = {"telemetry": {"shared_metrics": {
        "enabled": True, "send": True,
        "endpoint": "https://override.example/metrics",
    }}}
    assert resolve_send_config(config).send is False
    network = Mock(side_effect=AssertionError("telemetry request ran"))
    monkeypatch.setattr(
        shared_metrics_sender.urllib.request, "urlopen", network,
    )
    with pytest.raises(RuntimeError, match="disabled in this fork"):
        shared_metrics_sender._post(
            "https://override.example/metrics", b"{}", timeout=1,
        )
    network.assert_not_called()
