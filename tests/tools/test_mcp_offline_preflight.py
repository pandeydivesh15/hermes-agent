"""Automatic MCP admission must not send package metadata to advisory APIs."""

from unittest.mock import Mock

import pytest


@pytest.mark.asyncio
async def test_mcp_preflight_uses_cached_verdict_without_network(monkeypatch):
    from tools import mcp_tool, osv_check

    network = Mock(side_effect=AssertionError("online advisory lookup ran"))
    monkeypatch.setattr(osv_check, "_query_osv", network)
    monkeypatch.setattr(
        osv_check, "_cache_get", lambda key, **kw: (False, None),
    )
    assert await mcp_tool._preflight_stdio_command(
        "example", "uvx", ["example-package==1.0.0"],
    ) == ("uvx", ["example-package==1.0.0"])
    network.assert_not_called()


@pytest.mark.asyncio
async def test_mcp_preflight_preserves_cached_malware_block(monkeypatch):
    from tools import mcp_tool, osv_check

    monkeypatch.setattr(
        osv_check, "_cache_get",
        lambda key, **kw: (True, "BLOCKED: known malware"),
    )
    with pytest.raises(ValueError, match="known malware"):
        await mcp_tool._preflight_stdio_command("example", "uvx", ["bad-pkg"])


def test_expired_malware_block_survives_restart(tmp_path, monkeypatch):
    import json
    from tools import osv_check

    cache_file = tmp_path / "osv.json"
    cache_file.write_text(json.dumps({"version": 1, "entries": {
        "PyPI|bad-pkg|1.0": {
            "expiry": 1, "result": "BLOCKED: known malware",
        },
    }}))
    monkeypatch.setattr(osv_check, "_disk_cache_path", lambda: cache_file)
    monkeypatch.setattr(osv_check, "_cache", {})
    monkeypatch.setattr(osv_check, "_disk_cache_loaded", False)
    assert osv_check.check_cached_package_for_malware(
        "uvx", ["bad-pkg==1.0"],
    ) == "BLOCKED: known malware"


def test_explicit_audit_refreshes_local_malware_verdict(monkeypatch):
    from hermes_cli import security_audit
    from tools import osv_check

    component = security_audit.Component("bad-pkg", "1.0", "PyPI", "mcp")
    monkeypatch.setattr(security_audit, "_http_json", lambda *a: {
        "results": [{"vulns": [{"id": "MAL-2026-test"}]}],
    })
    store = Mock()
    monkeypatch.setattr(osv_check, "_cache_put", store)
    security_audit._osv_query_batch([component])
    key, verdict = store.call_args.args
    assert key == ("PyPI", "bad-pkg", "1.0")
    assert "MAL-2026-test" in verdict


def test_failed_online_refresh_keeps_expired_malware_block(monkeypatch):
    from tools import osv_check

    monkeypatch.setattr(osv_check, "_disk_cache_loaded", True)
    monkeypatch.setattr(osv_check, "_cache", {
        ("PyPI", "bad-pkg", "1.0"): (1, "BLOCKED: known malware"),
    })
    monkeypatch.setattr(
        osv_check, "_query_osv", Mock(side_effect=OSError("offline")),
    )
    assert osv_check.check_package_for_malware("uvx", ["bad-pkg==1.0"]) is None
    assert osv_check.check_cached_package_for_malware(
        "uvx", ["bad-pkg==1.0"],
    ) == "BLOCKED: known malware"
