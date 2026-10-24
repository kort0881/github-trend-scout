"""Единоразовый backfill архива из уже опубликованных выпусков.

Запуск: .venv/bin/python -m tools.backfill_archive
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.archive import ARCHIVE_NAME, Archive  # noqa: E402
from src.models import ScoredRepo  # noqa: E402


def main() -> int:
    output = ROOT / "output"
    archive = Archive(output / ARCHIVE_NAME)
    added = 0
    for release in sorted(p for p in output.iterdir() if p.is_dir()):
        analysis = release / "analysis.json"
        if not analysis.exists():
            continue
        try:
            items = [ScoredRepo.model_validate(item) for item in json.loads(analysis.read_text(encoding="utf-8"))]
        except Exception as exc:  # noqa: BLE001
            print(f"пропуск {release.name}: {exc}")
            continue
        before = len(archive)
        archive.add_release(release.name, items)
        added += len(archive) - before
        print(f"{release.name}: {len(items)} записей")
    archive.save()
    print(f"итого добавлено {added}, в архиве {len(archive)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
