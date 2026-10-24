from __future__ import annotations

import base64
import logging
import time
from datetime import date, timedelta

import requests

from .config import Config
from .models import RepoRaw

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
README_LIMIT = 4000

# github-trending-repos-api принимает только фиксированные окна
_DURATION_WINDOWS = {"1w": 7, "1m": 30, "3m": 90, "6m": 180, "1y": 365}


def pick_duration(days: int) -> str:
    """Ближайшее доступное окно обёртки, не меньшее чем days."""
    for name, span in _DURATION_WINDOWS.items():
        if span >= days:
            return name
    return "1y"


class GitHubClient:
    def __init__(self, token: str | None = None, timeout: int = 20, retries: int = 3):
        self.token = token
        self.timeout = timeout
        self.retries = retries

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "github-trend-scout"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get(self, path: str, params: dict | None = None) -> dict | list | None:
        url = path if path.startswith("http") else f"{GITHUB_API}{path}"
        delay = 60
        for attempt in range(1, self.retries + 1):
            try:
                resp = requests.get(url, params=params, headers=self._headers(), timeout=self.timeout)
            except requests.RequestException as exc:
                logger.warning("GitHub: сететевая ошибка (%s), попытка %s/%s", exc, attempt, self.retries)
                if attempt == self.retries:
                    return None
                time.sleep(min(delay, 5))
                continue

            if resp.status_code == 200:
                return resp.json()
            if resp.status_code in (403, 429):
                reset = resp.headers.get("X-RateLimit-Reset")
                logger.warning(
                    "GitHub rate-limit/403 на %s (reset=%s), backoff %ss, попытка %s/%s",
                    path, reset, delay, attempt, self.retries,
                )
                if attempt == self.retries:
                    return None
                time.sleep(delay)
                delay *= 2
                continue
            if resp.status_code == 404:
                return None
            logger.warning("GitHub API %s -> HTTP %s", path, resp.status_code)
            if attempt == self.retries:
                return None
            time.sleep(min(delay, 10))
        return None

    def repo_details(self, full_name: str) -> dict | None:
        data = self.get(f"/repos/{full_name}")
        return data if isinstance(data, dict) else None

    def readme_excerpt(self, full_name: str) -> str | None:
        data = self.get(f"/repos/{full_name}/readme")
        if not isinstance(data, dict):
            return None
        content = data.get("content")
        encoding = data.get("encoding")
        if not content:
            return None
        try:
            if encoding == "base64":
                raw = base64.b64decode(content)
            else:
                raw = requests.get(data.get("download_url", ""), timeout=self.timeout).content
            return raw.decode("utf-8", errors="replace")[:README_LIMIT]
        except Exception as exc:  # noqa: BLE001
            logger.warning("README %s не распакован: %s", full_name, exc)
            return None


def _candidates(config: Config) -> list[str]:
    """Имена кандидатов из github-trending-repos-api (обёртка над Search API)."""
    from github_trending_cli import trending

    duration = pick_duration(max(config.lookback_days * 2, 1))
    limit = max(config.candidate_limit, 30)
    try:
        repos = trending(duration=duration, limit=limit, token=config.github_token)
        logger.info("Ingestion: обёртка вернула %s кандидатов (окно %s)", len(repos), duration)
        return [r.full_name for r in repos]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Обёртка github-trending-repos-api упала (%s) — пробую Search API напрямую", exc)
        client = GitHubClient(config.github_token)
        since = (date.today() - timedelta(days=max(config.lookback_days * 2, 1))).isoformat()
        data = client.get(
            "/search/repositories",
            params={"q": f"created:>={since}", "sort": "stars", "order": "desc", "per_page": min(limit, 100)},
        )
        items = (data or {}).get("items", []) if isinstance(data, dict) else []
        return [item["full_name"] for item in items if item.get("full_name")]


def _to_raw(full_name: str, details: dict, readme: str | None) -> RepoRaw | None:
    try:
        lic = details.get("license") or {}
        return RepoRaw(
            full_name=details.get("full_name") or full_name,
            html_url=details.get("html_url") or f"https://github.com/{full_name}",
            description=details.get("description"),
            stars=int(details.get("stargazers_count") or 0),
            forks=int(details.get("forks_count") or 0),
            language=details.get("language"),
            license=(lic.get("spdx_id") or lic.get("name")) if isinstance(lic, dict) else None,
            created_at=details.get("created_at"),
            pushed_at=details.get("pushed_at") or details.get("updated_at"),
            topics=list(details.get("topics") or []),
            readme_excerpt=readme,
            archived=bool(details.get("archived")),
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Не удалось собрать RepoRaw для %s: %s", full_name, exc)
        return None


def ingest(config: Config, client: GitHubClient | None = None) -> list[RepoRaw]:
    client = client or GitHubClient(config.github_token)
    names = _candidates(config)
    logger.info("Ingestion: кандидатов получено %s", len(names))

    result: list[RepoRaw] = []
    for full_name in names:
        details = client.repo_details(full_name)
        if not details:
            logger.warning("Ingestion: нет метаданных по %s, пропуск", full_name)
            continue
        raw = _to_raw(full_name, details, client.readme_excerpt(full_name))
        if raw is not None:
            result.append(raw)
    logger.info("Ingestion: собрано валидных RepoRaw %s", len(result))
    return result
