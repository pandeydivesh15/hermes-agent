"""Configured collectors cannot enable telemetry exports in this fork."""

import pytest


def test_otlp_configuration_cannot_enable_export():
    from agent.monitoring import otlp_exporter

    config = {"monitoring": {"export": {"otlp": {
        "enabled": True, "endpoint": "https://collector.example/v1/traces",
    }}}}
    assert otlp_exporter.is_enabled(config) is False
    with pytest.raises(otlp_exporter.OTLPUnavailable, match="disabled"):
        otlp_exporter.build_exporter(config)
