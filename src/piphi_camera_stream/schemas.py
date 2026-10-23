from __future__ import annotations

from urllib.parse import urlsplit

from piphi_runtime_kit_python import RuntimeConfig
from pydantic import Field, SecretStr, field_validator


class DeviceConfig(RuntimeConfig):
    source_url: SecretStr
    alias: str | None = Field(default=None, max_length=120)
    preferred_transport: str = Field(default="tcp", pattern="^(tcp|udp|auto)$")

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, value: SecretStr) -> SecretStr:
        source = value.get_secret_value().strip()
        parsed = urlsplit(source)
        if len(source) > 4096 or any(character in source for character in "\r\n\0") or parsed.scheme.lower() not in {"rtsp", "rtsps"} or not parsed.hostname:
            raise ValueError("source_url must be a valid RTSP or RTSPS camera URL")
        return SecretStr(source)
