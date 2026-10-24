from __future__ import annotations

import json
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

from .models import RepoRaw, SecurityReport

logger = logging.getLogger(__name__)

SCANNER_TIMEOUT = 120
CLONE_TIMEOUT = 180

_CRITICAL_WORDS = {"CRITICAL", "ERROR", "BLOCKER"}
_HIGH_WORDS = {"HIGH", "WARNING", "MAJOR"}
_MEDIUM_WORDS = {"MEDIUM", "MODERATE", "MINOR"}


def _which(binary: str) -> bool:
    return shutil.which(binary) is not None


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=SCANNER_TIMEOUT, check=False
        )
    except subprocess.TimeoutExpired:
        logger.warning("Сканер %s превысил таймаут %ss", cmd[0], SCANNER_TIMEOUT)
    except (OSError, ValueError) as exc:
        logger.warning("Сканер %s не запустился: %s", cmd[0], exc)
    return None


def _json_of(proc: subprocess.CompletedProcess | None):
    if proc is None:
        return None
    for text in (proc.stdout, proc.stdout.strip()):
        if not text:
            continue
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            continue
    return None


def parse_semgrep(data) -> tuple[int, int, int]:
    """Возвращает (всего, critical, high)."""
    if not isinstance(data, dict):
        return 0, 0, 0
    results = data.get("results") or []
    critical = high = 0
    for item in results:
        severity = str((item.get("extra") or {}).get("severity", "")).upper()
        if severity in _CRITICAL_WORDS:
            critical += 1
        elif severity in _HIGH_WORDS:
            high += 1
    return len(results), critical, high


def parse_bandit(data) -> tuple[int, int, int]:
    if not isinstance(data, dict):
        return 0, 0, 0
    results = data.get("results") or []
    critical = high = 0
    for item in results:
        severity = str(item.get("issue_severity", "")).upper()
        if severity in _CRITICAL_WORDS:
            critical += 1
        elif severity in _HIGH_WORDS:
            high += 1
    return len(results), critical, high


def parse_gitleaks(data) -> tuple[int, int, int]:
    leaks = data if isinstance(data, list) else (data or {}).get("findings", []) if isinstance(data, dict) else []
    leaks = [item for item in leaks if isinstance(item, dict)]
    # утёкший секрет = high по умолчанию, если сам gitleaks не указал иное
    critical = 0
    high = 0
    for item in leaks:
        level = str(item.get("Severity") or item.get("severity") or "high").upper()
        if level in _CRITICAL_WORDS:
            critical += 1
        else:
            high += 1
    return len(leaks), critical, high


def parse_osv(data) -> tuple[int, int, int]:
    if not isinstance(data, dict):
        return 0, 0, 0
    total = critical = high = 0
    for result in data.get("results") or []:
        for package in result.get("packages") or []:
            vulns = package.get("vulnerabilities") or []
            total += len(vulns)
            for vuln in vulns:
                severity = str(vuln.get("database_specific", {}).get("severity", "")).upper()
                if severity in _CRITICAL_WORDS:
                    critical += 1
                elif severity in _HIGH_WORDS:
                    high += 1
    return total, critical, high


def _has_python_files(path: Path) -> bool:
    return any(path.rglob("*.py"))


def _has_lock_files(path: Path) -> bool:
    masks = ("requirements*.txt", "*.lock", "poetry.lock", "uv.lock", "Pipfile.lock", "package-lock.json")
    return any(any(path.rglob(mask)) for mask in masks)


def scan_directory(path: Path) -> tuple[SecurityReport, dict]:
    """Запускает доступные сканеры в уже склонированной директории."""
    raw: dict = {}
    findings = {"semgrep": 0, "bandit": 0, "gitleaks": 0}
    critical = high = 0
    skipped: list[str] = []

    if _which("semgrep"):
        proc = _run(["semgrep", "--config=auto", "--json", "--quiet", "--error"], path)
        data = _json_of(proc)
        raw["semgrep"] = data
        total, crit, hi = parse_semgrep(data)
        findings["semgrep"], critical, high = total, critical + crit, high + hi
    else:
        skipped.append("semgrep")

    if _which("bandit") and _has_python_files(path):
        proc = _run(["bandit", "-r", ".", "-f", "json", "-q"], path)
        data = _json_of(proc)
        raw["bandit"] = data
        total, crit, hi = parse_bandit(data)
        findings["bandit"], critical, high = total, critical + crit, high + hi
    elif not _which("bandit"):
        skipped.append("bandit")

    if _which("gitleaks"):
        proc = _run(
            ["gitleaks", "detect", "--no-git", "--report-format=json", "--report-path=/dev/stdout", "--exit-code=0"],
            path,
        )
        data = _json_of(proc)
        raw["gitleaks"] = data
        total, crit, hi = parse_gitleaks(data)
        findings["gitleaks"], critical, high = total, critical + crit, high + hi
    else:
        skipped.append("gitleaks")

    if _which("osv-scanner") and _has_lock_files(path):
        proc = _run(["osv-scanner", "--format", "json", "-r", "."], path)
        data = _json_of(proc)
        raw["osv"] = data
        total, crit, hi = parse_osv(data)
        critical, high = critical + crit, high + hi
        findings["osv"] = total
    elif not _which("osv-scanner"):
        skipped.append("osv-scanner")

    report = SecurityReport(
        semgrep_findings=findings["semgrep"],
        bandit_findings=findings["bandit"],
        gitleaks_findings=findings["gitleaks"],
        critical_count=critical,
        high_count=high,
        passed=critical == 0 and high == 0,
        details=_details(findings, critical, high, skipped),
    )
    return report, raw


def _details(findings: dict[str, int], critical: int, high: int, skipped: list[str]) -> str:
    parts = [f"{name}: {count}" for name, count in findings.items()]
    text = "Находки — " + ", ".join(parts) + f"; critical={critical}, high={high}"
    if skipped:
        text += f". Не запускались: {', '.join(skipped)}"
    return text


def _clone(full_name: str, dest: Path) -> bool:
    cmd = ["git", "clone", "--depth", "1", "--quiet", f"https://github.com/{full_name}.git", str(dest)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=CLONE_TIMEOUT, check=False)
    except subprocess.TimeoutExpired:
        logger.warning("Security: клон %s превысил таймаут", full_name)
        return False
    if proc.returncode != 0:
        logger.warning("Security: клон %s не удался: %s", full_name, proc.stderr.strip()[:200])
        return False
    return True


def security_scan(repo: RepoRaw, cache=None) -> SecurityReport:
    """Клон во временную директорию + статический анализ. Ошибки не валят пайплайн."""
    if cache is not None:
        cached = cache.get_raw(repo.full_name)
        if cached is not None:
            logger.info("Security: %s взят из кэша сканеров", repo.full_name)
            return SecurityReport.model_validate(cached)

    tmp = Path(tempfile.mkdtemp(prefix="scout-"))
    target = tmp / "repo"
    try:
        if not _clone(repo.full_name, target):
            return SecurityReport(details="Клон не удался — репозиторий не проверен", passed=True)
        report, raw = scan_directory(target)
        if cache is not None:
            cache.set_raw(repo.full_name, report.model_dump(), raw)
        return report
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
