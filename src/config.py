from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DEFAULT_MODEL = "openai/gpt-oss-120b"
DEFAULT_FALLBACKS = ["qwen/qwen3.8-27b", "llama-3.3-70b-versatile"]


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Config:
    groq_api_key: str
    groq_model: str
    groq_fallbacks: list[str]
    github_token: str | None
    max_repos: int
    min_stars: int
    lookback_days: int
    candidate_limit: int
    min_release_repos: int
    root: Path

    @property
    def output_dir(self) -> Path:
        return Path(os.getenv("OUTPUT_DIR", str(self.root / "output")))

    @property
    def data_dir(self) -> Path:
        return Path(os.getenv("DATA_DIR", str(self.root / "data")))

    @property
    def prompts_dir(self) -> Path:
        return self.root / "prompts"


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} должен быть целым числом, получено: {raw!r}") from exc


def load_config() -> Config:
    key = (os.getenv("GROQ_API_KEY") or "").strip()
    if not key:
        raise ConfigError(
            "GROQ_API_KEY не задан. Скопируйте .env.example в .env и впишите ключ "
            "(или добавьте секрет GROQ_API_KEY в настройках репозитория GitHub)."
        )
    raw_fallbacks = (os.getenv("GROQ_FALLBACK_MODELS") or "").strip()
    fallbacks = (
        [m.strip() for m in raw_fallbacks.split(",") if m.strip()]
        if raw_fallbacks
        else list(DEFAULT_FALLBACKS)
    )
    return Config(
        groq_api_key=key,
        groq_model=(os.getenv("GROQ_MODEL") or DEFAULT_MODEL).strip(),
        groq_fallbacks=fallbacks,
        github_token=(os.getenv("GITHUB_TOKEN") or "").strip() or None,
        max_repos=min(_int_env("MAX_REPOS", 10), 10),
        min_stars=_int_env("MIN_STARS", 100),
        lookback_days=_int_env("LOOKBACK_DAYS", 3),
        candidate_limit=_int_env("CANDIDATE_LIMIT", 50),
        min_release_repos=_int_env("MIN_RELEASE_REPOS", 3),
        root=ROOT,
    )
