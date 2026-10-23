# Piphi Camera Stream

Generated PiPhi integration runtime.

## Run locally

```bash
pdm install -G dev
pdm run uvicorn piphi_camera_stream.main:app --reload --port 8090
pdm run pytest
pdm run python scripts/validate.py
```

The runtime listens on port `8090` by default and exposes the common PiPhi runtime route contract:

- `GET /health`
- `GET /diagnostics`
- `POST /discover`
- `POST /config`
- `POST /config/sync`
- `POST /deconfigure`
- `POST /deconfigure/{config_id}`
- `GET /state`
- `GET /contract`
- `GET /entities`
- `GET /events`
- `POST /events/device/{config_id}/example`
- `POST /telemetry/example`
- `POST /telemetry/device/{config_id}/example`
- `POST /command`

For pull-capable integrations, register one real upstream reader with
`starter.state.provide(...)`. For polling and webhook updates, call
`starter.state.publish(...)`. Do not parse refresh query parameters or construct
receipts in integration code; the Runtime Kit owns that protocol.

## Manifest

`manifest.json` is a starter manifest. Before publishing, update:

- `image`
- `version`
- capabilities and commands
- config fields and identity fields
- entity metadata

## Docker

```bash
docker build -t ghcr.io/piphi-io/piphi-camera-stream:0.1.0 .
docker run --rm -p 8090:8090 ghcr.io/piphi-io/piphi-camera-stream:0.1.0
```
