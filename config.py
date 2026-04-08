import os
from pathlib import Path

ENV_FILE = Path.cwd() / ".env"

def _default_download_root() -> Path:
    if os.name == "nt":
        return Path.home() / "Downloads" / "nogifes"
    return Path("/mnt/data/downloads/nogifes")

def _load_env_values(env_file: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not env_file.exists():
        return values

    for line in env_file.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#"):
            continue
        if raw.startswith("export "):
            raw = raw[7:].strip()
        if "=" not in raw:
            continue

        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]

        values[key] = value

    return values

ENV_VALUES = _load_env_values(ENV_FILE)

API_BASE_URL = ENV_VALUES.get("NOGIFES_API_BASE_URL", "https://v1api.nogifes.jp").rstrip("/")
STATIC_BASE_URL = ENV_VALUES.get("NOGIFES_STATIC_BASE_URL", "https://v1static.nogifes.jp").rstrip("/")
DOWNLOAD_ROOT = Path(ENV_VALUES.get("NOGIFES_DOWNLOAD_ROOT", str(_default_download_root()))).expanduser()
