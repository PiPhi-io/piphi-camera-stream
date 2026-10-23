from __future__ import annotations

from piphi_camera_stream.contract import COMMANDS, REQUIRED_ENDPOINTS
from piphi_camera_stream.main import app


def test_runtime_implements_contract_routes() -> None:
    routes = set(app.openapi()["paths"])
    for path in [
        "/health",
        "/diagnostics",
        "/discover",
        "/config",
        "/config/sync",
        "/deconfigure",
        "/deconfigure/{config_id}",
        "/ui-config",
        "/entities",
        "/state",
        "/contract",
        "/events",
        "/events/device/{config_id}/example",
        "/telemetry/example",
        "/telemetry/device/{config_id}/example",
        "/command",
        "/v1/cameras/{config_id}/source",
    ]:
        assert path in routes

    assert REQUIRED_ENDPOINTS == ["health", "entities", "command", "config", "ui_config"]
    assert "refresh" in COMMANDS
