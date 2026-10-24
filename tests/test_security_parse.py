from __future__ import annotations

from src.models import SecurityReport
from src.security import _details, parse_bandit, parse_gitleaks, parse_osv, parse_semgrep

SEMGREP = {
    "results": [
        {"extra": {"severity": "ERROR"}},
        {"extra": {"severity": "WARNING"}},
        {"extra": {"severity": "INFO"}},
    ]
}

BANDIT = {
    "results": [
        {"issue_severity": "HIGH"},
        {"issue_severity": "LOW"},
    ]
}

GITLEAKS = [{"Description": "AWS key", "Severity": "high"}]

OSV = {
    "results": [
        {
            "packages": [
                {
                    "vulnerabilities": [
                        {"database_specific": {"severity": "CRITICAL"}},
                        {"database_specific": {"severity": "MODERATE"}},
                    ]
                }
            ]
        }
    ]
}


def test_parse_semgrep_counts_severities():
    # ERROR от semgrep — это high, а не critical: иначе выпуски схлопываются до 2-3 репозиториев
    assert parse_semgrep(SEMGREP) == (3, 0, 1)


def test_parse_bandit_counts_high():
    assert parse_bandit(BANDIT) == (2, 0, 1)


def test_parse_gitleaks_counts_secrets():
    assert parse_gitleaks(GITLEAKS) == (1, 0, 1)


def test_parse_osv_counts_vulns():
    assert parse_osv(OSV) == (2, 1, 0)


def test_parsers_survive_garbage():
    for parser in (parse_semgrep, parse_bandit, parse_gitleaks, parse_osv):
        assert parser(None) == (0, 0, 0)
        assert parser({"unexpected": True}) == (0, 0, 0)


def test_report_passed_only_without_critical_and_high():
    assert SecurityReport(critical_count=0, high_count=0).passed is True
    report = SecurityReport(critical_count=1, passed=False)
    assert report.passed is False


def test_details_mentions_skipped_scanners():
    text = _details({"semgrep": 1, "bandit": 0, "gitleaks": 0}, 0, 0, ["osv-scanner"])
    assert "osv-scanner" in text and "critical=0" in text
