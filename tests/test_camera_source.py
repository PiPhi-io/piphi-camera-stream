from __future__ import annotations

import httpx
import pytest

from piphi_camera_stream.main import app
from piphi_camera_stream.schemas import DeviceConfig
from piphi_camera_stream.state import apply_config, registry


@pytest.mark.anyio
async def test_camera_integration_owns_secret_and_exposes_only_private_source_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PIPHI_INTEGRATION_INTERNAL_TOKEN", "runtime-token")
    monkeypatch.setenv("PIPHI_CONTAINER_ID", "camera-container")
    registry.entries.clear()
    registry.state_snapshots.clear()
    await apply_config(DeviceConfig(id="front-door", config_id="front-door", source_url="rtsps://user:top-secret@camera.local/live", alias="Front door", preferred_transport="tcp"))
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        entities = await client.get("/entities")
        state = await client.get("/state")
        unauthorized = await client.get("/v1/cameras/front-door/source")
        source = await client.get(
            "/v1/cameras/front-door/source",
            headers={
                "X-PiPhi-Integration-Token": "runtime-token",
                "X-Container-Id": "camera-container",
            },
        )
    assert "camera_stream" in entities.json()["entities"][0]["capabilities"]
    assert entities.json()["capabilities"]["camera_stream"]["camera"]["contract_version"] == "camera.media.v1"
    assert "top-secret" not in state.text and "camera.local" not in state.text
    assert unauthorized.status_code == 401
    assert source.json()["source_url"] == "rtsps://user:top-secret@camera.local/live"
    assert source.json()["audience"] == "core-sidecar"


@pytest.mark.anyio
async def test_camera_source_fails_closed_without_runtime_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PIPHI_INTEGRATION_INTERNAL_TOKEN", raising=False)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/v1/cameras/front-door/source")
    assert response.status_code == 503


def test_camera_config_rejects_browser_urls_and_control_characters() -> None:
    with pytest.raises(ValueError, match="RTSP"):
        DeviceConfig(id="camera", source_url="https://camera.local/image.jpg")
    with pytest.raises(ValueError, match="RTSP"):
        DeviceConfig(id="camera", source_url="rtsp://camera.local/live\nspoof")


def test_camera_config_rejects_malformed_inline_credentials() -> None:
    with pytest.raises(ValueError, match="username:password@"):
        DeviceConfig(
            id="camera",
            source_url="rtsps://username@passwordcamera.local:322/stream0",
        )


def test_camera_config_accepts_inline_credentials() -> None:
    config = DeviceConfig(
        id="camera",
        source_url="rtsps://username:password@camera.local:322/stream0",
    )

    assert config.source_url.get_secret_value().startswith("rtsps://username:password@")
