"""Remote webhook payloads require encrypted transport."""

import pytest

from agent.outbound_webhooks import iter_configured_targets


@pytest.mark.parametrize("url", [
    "http://example.com/hook",
    "http://127.0.0.1.example.com/hook",
    "http://localhost@example.com/hook",
])
def test_remote_plaintext_target_is_rejected(url):
    config = {"hooks": {"outbound": [{
        "url": url, "events": ["pre_tool_call"],
    }]}}
    assert iter_configured_targets(config) == []


@pytest.mark.parametrize("url", [
    "https://example.com/hook",
    "http://127.0.0.1:8080/hook",
    "http://[::1]:8080/hook",
    "http://localhost:8080/hook",
])
def test_encrypted_or_loopback_target_is_accepted(url):
    config = {"hooks": {"outbound": [{
        "url": url, "events": ["pre_tool_call"],
    }]}}
    assert len(iter_configured_targets(config)) == 1
