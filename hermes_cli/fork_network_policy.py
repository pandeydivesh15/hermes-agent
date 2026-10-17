"""Source-level fork policy; configuration cannot enable optional egress."""

from typing import Final

OPTIONAL_NETWORK_ALLOWED: Final = False


def require_optional_network(feature: str) -> None:
    """Refuse retained upstream transports before they acquire credentials."""
    if not OPTIONAL_NETWORK_ALLOWED:
        raise RuntimeError(f"{feature} network access is disabled in this fork")
