from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from fastapi.encoders import jsonable_encoder

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from backend import main as api  # noqa: E402

OUTPUT_DIRECTORY = REPOSITORY_ROOT / "api"
AREAS = ("All", "Rural", "Urban")
CATEGORIES = (
    "All",
    "Higher Secondary",
    "Primary",
    "Secondary",
    "Upper Primary",
)


def _slug(value: str) -> str:
    return value.lower().replace(" ", "-")


def _write_json(relative_path: Path, payload: Any) -> None:
    destination = OUTPUT_DIRECTORY / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(jsonable_encoder(payload), indent=2) + "\n",
        encoding="utf-8",
    )


def build_static_api() -> int:
    _write_json(Path("health.json"), api.health())
    _write_json(Path("dashboard.json"), api.dashboard_data())

    endpoint_count = 2
    for area in AREAS:
        for category in CATEGORIES:
            filter_path = Path(_slug(area)) / f"{_slug(category)}.json"
            _write_json(Path("summary") / filter_path, api.summary(area, category))
            _write_json(Path("questions") / filter_path, api.questions(area, category))
            _write_json(Path("groups") / filter_path, api.groups(area, category))
            endpoint_count += 3

            for question_id in range(1, 6):
                _write_json(
                    Path("questions")
                    / str(question_id)
                    / filter_path,
                    api.question(question_id, area, category),
                )
                endpoint_count += 1

    return endpoint_count


if __name__ == "__main__":
    print(f"Generated {build_static_api()} static API JSON files in {OUTPUT_DIRECTORY}")
