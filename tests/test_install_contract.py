from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[1]


def _manifest() -> dict:
    return json.loads((ROOT / "manifest.json").read_text())


def test_rtsp_camera_uses_manual_setup_without_device_discovery() -> None:
    manifest = _manifest()

    assert manifest["onboarding"] == {"mode": "manual"}
    assert manifest["marketplace"]["category"] == "security"
    assert "discovery" not in manifest["runtime"]["linux"]
    assert "discover" not in manifest["api"]["endpoints"]


def test_rtsp_camera_auto_installs_the_shared_webrtc_service() -> None:
    manifest = _manifest()

    assert manifest["requires"]["services"] == [
        {
            "id": "piphi.service.webrtc-sidecar",
            "kind": "platform_service",
            "version_range": ">=0.2.1,<0.3.0",
            "recommended_version": "0.2.1",
            "required": True,
            "shared": True,
            "auto_install": True,
            "reason": "Provides low-latency WebRTC playback for configured RTSP cameras.",
        }
    ]


def test_core_allocates_the_runtime_host_port() -> None:
    manifest = _manifest()

    assert manifest["runtime"]["linux"]["container"]["ports"] == [
        {"container": 8090}
    ]
