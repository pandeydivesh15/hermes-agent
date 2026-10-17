"""Relay configuration and direct transport calls cannot bypass fork policy."""

from unittest.mock import Mock

import pytest


def test_relay_url_override_cannot_enable_connection(monkeypatch):
    from gateway import relay

    monkeypatch.setenv("GATEWAY_RELAY_URL", "wss://override.example/relay")
    assert relay.relay_url() is None
    network = Mock(side_effect=AssertionError("relay request ran"))
    monkeypatch.setattr(relay.urllib.request, "urlopen", network)
    with pytest.raises(RuntimeError, match="disabled in this fork"):
        relay._json_post("https://override.example", "synthetic", {}, 1)
    network.assert_not_called()


@pytest.mark.asyncio
async def test_direct_relay_dial_is_blocked():
    from gateway.relay.ws_transport import WebSocketRelayTransport

    transport = WebSocketRelayTransport(
        "wss://override.example/relay", "telegram", "synthetic-bot",
    )
    with pytest.raises(RuntimeError, match="disabled in this fork"):
        await transport._dial_and_start()
