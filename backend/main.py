from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd
from fastapi import FastAPI, Path as ApiPath, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "dashboard-data.json"
DATA_PATH = Path(os.environ.get("DASHBOARD_DATA_PATH", DEFAULT_DATA_PATH))
METRICS = {
    "internet_access": "Internet_Access_Percentage",
    "readiness": "Digital_Readiness_Score",
    "digital_literacy": "Digital_Literacy_Score",
    "technology_adoption": "Technology_Adoption_Index",
}
DISTRIBUTION_METRICS = (
    "internet_access",
    "readiness",
    "computers",
    "smart_classrooms",
)
Area = Literal["All", "Rural", "Urban"]
Category = Literal[
    "All",
    "Higher Secondary",
    "Primary",
    "Secondary",
    "Upper Primary",
]


def _cors_origins() -> list[str]:
    configured = os.environ.get("CORS_ORIGINS")
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    return [
        "https://pranavigamidi.github.io",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:8765",
    ]


app = FastAPI(
    title="Schooling, Connected API",
    description="Read-only API for the five digital education data-analysis questions.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def website() -> FileResponse:
    return FileResponse(DATA_PATH.parent.parent / "index.html")


@lru_cache(maxsize=1)
def _load_dashboard_data() -> dict[str, Any]:
    try:
        with DATA_PATH.open(encoding="utf-8") as dashboard_file:
            data = json.load(dashboard_file)
    except FileNotFoundError as error:
        raise RuntimeError(f"Dashboard data file was not found: {DATA_PATH}") from error
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Dashboard data file is not valid JSON: {DATA_PATH}") from error

    if not isinstance(data.get("records"), list) or not isinstance(
        data.get("question_data"), dict
    ):
        raise RuntimeError(f"Dashboard data has an invalid structure: {DATA_PATH}")
    return data


def _filtered_records(area: Area, category: Category) -> pd.DataFrame:
    records = pd.DataFrame(_load_dashboard_data()["records"])
    if area != "All":
        records = records.loc[records["area"] == area]
    if category != "All":
        records = records.loc[records["category"] == category]
    return records


def _filtered_question_groups(area: Area, category: Category) -> list[dict[str, Any]]:
    groups = _load_dashboard_data()["question_data"]["groups"]
    return [
        group
        for group in groups
        if (area == "All" or group["area"] == area)
        and (category == "All" or group["category"] == category)
    ]


def _grouped_state_category_stats(
    area: Area, category: Category
) -> list[dict[str, Any]]:
    groups = pd.DataFrame(
        _load_dashboard_data()["question_data"]["state_category_stats"]
    )
    if area != "All":
        groups = groups.loc[groups["area"] == area]
    if category != "All":
        groups = groups.loc[groups["category"] == category]
    if groups.empty:
        return []

    metric_names = list(METRICS.values())
    sums = pd.DataFrame(groups["metric_sums"].tolist(), index=groups.index)
    counts = pd.DataFrame(groups["metric_counts"].tolist(), index=groups.index)
    groups = pd.concat(
        [
            groups.drop(columns=["metric_sums", "metric_counts"]),
            sums.add_suffix("_sum"),
            counts.add_suffix("_count"),
        ],
        axis=1,
    )
    sums = groups.groupby(["state", "category"], as_index=False).agg(
        schools=("schools", "sum"),
        **{
            name: (f"{metric}_{kind}", "sum")
            for metric in metric_names
            for kind, name in (
                ("sum", f"{metric}_sum"),
                ("count", f"{metric}_count"),
            )
        },
    )
    result: list[dict[str, Any]] = []
    for row in sums.to_dict(orient="records"):
        metric_sums = {metric: row[f"{metric}_sum"] for metric in metric_names}
        metric_counts = {
            metric: int(row[f"{metric}_count"]) for metric in metric_names
        }
        result.append(
            {
                "state": row["state"],
                "category": row["category"],
                "schools": int(row["schools"]),
                "metric_sums": metric_sums,
                "metric_counts": metric_counts,
                "metric_means": {
                    metric: (
                        metric_sums[metric] / metric_counts[metric]
                        if metric_counts[metric]
                        else None
                    )
                    for metric in metric_names
                },
            }
        )
    return sorted(result, key=lambda row: (row["state"], row["category"]))


def _distribution_summaries(
    area: Area, category: Category
) -> dict[str, dict[str, Any]]:
    data = _load_dashboard_data()["question_data"]
    groups = _filtered_question_groups(area, category)
    summaries: dict[str, dict[str, Any]] = {}
    for metric in DISTRIBUTION_METRICS:
        total_sum = 0.0
        total_count = 0
        minimum: float | None = None
        maximum: float | None = None
        bins = [0] * data["distribution_specs"][metric]["bins"]
        for group in groups:
            summary = group["distribution_summary"][metric]
            total_sum += summary["sum"]
            total_count += summary["count"]
            if summary["count"]:
                minimum = summary["min"] if minimum is None else min(minimum, summary["min"])
                maximum = summary["max"] if maximum is None else max(maximum, summary["max"])
            for index, value in enumerate(group["distributions"][metric]):
                bins[index] += value
        summaries[metric] = {
            "count": total_count,
            "mean": total_sum / total_count if total_count else None,
            "min": minimum,
            "max": maximum,
            "bins": bins,
            "bin_count": len(bins),
            "data_min": data["distribution_specs"][metric]["min"],
            "data_max": data["distribution_specs"][metric]["max"],
        }
    return summaries


def _build_questions(area: Area, category: Category) -> dict[str, Any]:
    data = _load_dashboard_data()
    question_data = data["question_data"]
    groups = _filtered_question_groups(area, category)

    access_sum = sum(group["access"]["sum"] for group in groups)
    access_count = sum(group["access"]["count"] for group in groups)
    access_average = access_sum / access_count if access_count else None
    access_min = min((group["access"]["min"] for group in groups), default=None)
    access_max = max((group["access"]["max"] for group in groups), default=None)
    if access_count:
        access_average = float(
            np.average(
                [group["access"]["sum"] / group["access"]["count"] for group in groups],
                weights=[group["access"]["count"] for group in groups],
            )
        )
    question_one = {
        "method": "NumPy weighted mean over the school-level aggregate groups",
        "school_count": access_count,
        "mean_internet_access_percentage": access_average,
        "max_internet_access_percentage": access_max,
        "min_internet_access_percentage": access_min,
    }

    q2_records = _filtered_records("All", category)
    area_counts = (
        q2_records.groupby("area", as_index=False)["schools"].sum()
        if not q2_records.empty
        else pd.DataFrame(columns=["area", "schools"])
    )
    school_counts = {area_name: 0 for area_name in ("Rural", "Urban")}
    school_counts.update(
        {row["area"]: int(row["schools"]) for row in area_counts.to_dict(orient="records")}
    )
    q2_total = sum(school_counts.values())
    question_two = {
        "method": "Pandas filter by school category and group by Area",
        "school_counts": school_counts,
        "school_percentages": {
            key: (value / q2_total * 100 if q2_total else 0.0)
            for key, value in school_counts.items()
        },
        "school_count": q2_total,
    }

    missing = question_data["missing_values"]
    question_three = {
        **missing,
        "imputation": question_data["imputation"],
        "access_rate_missing_count": missing["access_statistics_fields"][
            "Internet_Access_Percentage"
        ],
        "access_rate_record_count": question_data["distribution_specs"][
            "internet_access"
        ]["count"],
    }

    state_category = _grouped_state_category_stats(area, category)
    highest_access = max(
        state_category,
        key=lambda row: (
            row["metric_means"]["Internet_Access_Percentage"]
            if row["metric_means"]["Internet_Access_Percentage"] is not None
            else -1
        ),
        default=None,
    )
    question_four = {
        "method": "Pandas groupby by State and School_Category",
        "group_count": len(state_category),
        "groups": state_category,
        "highest_mean_internet_access": highest_access,
    }

    records = _filtered_records(area, category)

    def count_by(column: str) -> dict[str, int]:
        if records.empty:
            return {}
        totals = records.groupby(column)["schools"].sum().sort_values(ascending=False)
        return {key: int(value) for key, value in totals.to_dict().items()}

    question_five = {
        "school_counts_by_area": count_by("area"),
        "school_counts_by_state": count_by("state"),
        "school_counts_by_category": count_by("category"),
        "distributions": _distribution_summaries(area, category),
    }
    return {
        "Q1": question_one,
        "Q2": question_two,
        "Q3": question_three,
        "Q4": question_four,
        "Q5": question_five,
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    _load_dashboard_data()
    return {"status": "ok"}


@app.get("/api/dashboard")
def dashboard_data() -> dict[str, Any]:
    return _load_dashboard_data()


@app.get("/api/summary")
def summary(
    area: Area = Query(default="All"),
    category: Category = Query(default="All"),
) -> dict[str, Any]:
    records = _filtered_records(area, category)
    if records.empty:
        return {
            "filters": {"area": area, "category": category},
            "school_count": 0,
            "connected_school_count": 0,
            "connected_school_percentage": None,
            "mean_internet_access_percentage": None,
            "mean_digital_readiness_score": None,
        }

    schools = int(records["schools"].sum())
    connected = int(records["internet_connected"].sum())
    metric_sums = {
        metric: sum(row[metric] for row in records["metric_sums"])
        for metric in METRICS.values()
    }
    metric_counts = {
        metric: sum(row[metric] for row in records["metric_counts"])
        for metric in METRICS.values()
    }
    return {
        "filters": {"area": area, "category": category},
        "school_count": schools,
        "connected_school_count": connected,
        "connected_school_percentage": connected / schools * 100 if schools else None,
        "mean_internet_access_percentage": (
            metric_sums["Internet_Access_Percentage"]
            / metric_counts["Internet_Access_Percentage"]
            if metric_counts["Internet_Access_Percentage"]
            else None
        ),
        "mean_digital_readiness_score": (
            metric_sums["Digital_Readiness_Score"]
            / metric_counts["Digital_Readiness_Score"]
            if metric_counts["Digital_Readiness_Score"]
            else None
        ),
    }


@app.get("/api/questions")
def questions(
    area: Area = Query(default="All"),
    category: Category = Query(default="All"),
) -> dict[str, Any]:
    return {
        "filters": {"area": area, "category": category},
        "answers": _build_questions(area, category),
    }


@app.get("/api/questions/{question_id}")
def question(
    question_id: int = ApiPath(ge=1, le=5),
    area: Area = Query(default="All"),
    category: Category = Query(default="All"),
) -> dict[str, Any]:
    answer_key = f"Q{question_id}"
    return {
        "question": answer_key,
        "filters": {"area": area, "category": category},
        "answer": _build_questions(area, category)[answer_key],
    }


@app.get("/api/groups")
def groups(
    area: Area = Query(default="All"),
    category: Category = Query(default="All"),
) -> dict[str, Any]:
    results = _grouped_state_category_stats(area, category)
    return {
        "filters": {"area": area, "category": category},
        "group_count": len(results),
        "groups": results,
    }


app.mount(
    "/data",
    StaticFiles(directory=DATA_PATH.parent, check_dir=True),
    name="dashboard-data",
)
