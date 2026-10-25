from __future__ import annotations

import json
from pathlib import Path

from piphi_camera_stream.contract import COMMANDS, CONFIG_SCHEMA, REQUIRED_ENDPOINTS
from piphi_camera_stream.main import app


ROOT = Path(__file__).parents[1]


def test_runtime_implements_contract_routes() -> None:
    routes = set(app.openapi()["paths"])
    for path in [
        "/health",
        "/diagnostics",
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

    assert "/discover" not in routes

    assert REQUIRED_ENDPOINTS == ["health", "entities", "command", "config", "ui_config"]
    assert "refresh" in COMMANDS


def test_camera_url_setup_explains_optional_rtsp_credentials() -> None:
    source_url = CONFIG_SCHEMA["schema"]["properties"]["source_url"]
    source_ui = CONFIG_SCHEMA["uiSchema"]["source_url"]

    assert "username and password" in source_url["description"]
    assert "username:password@" in source_ui["placeholder"]
    assert "format" not in source_url
    assert source_url["writeOnly"] is True


def test_camera_stream_depends_on_shared_camera_media_service() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text())

    assert manifest["requires"]["services"] == [
        {
            "id": "piphi.service.webrtc-sidecar",
            "kind": "platform_service",
            "version_range": ">=0.3.0,<0.4.0",
            "recommended_version": "0.3.0",
            "required": True,
            "shared": True,
            "auto_install": True,
            "reason": "Provides shared camera media sessions and low-latency WebRTC playback.",
        }
    ]
