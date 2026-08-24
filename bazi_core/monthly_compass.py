from __future__ import annotations

from pathlib import Path
from typing import Any

import sxtwl

from .tables import BRANCHES, BRANCH_ELEMENT, STEMS, STEM_ELEMENT, STEM_YIN_YANG

MONTHLY_SCHEMA_VERSION = "1.0.0"
MONTHLY_MODEL_VERSION = "monthly-compass-v1"

ELEMENT_SHIFT = {
    "wood": {"career": 9, "wealth": 1, "relationship": 4, "stability": -3},
    "fire": {"career": 7, "wealth": 6, "relationship": 2, "stability": -5},
    "earth": {"career": 2, "wealth": 3, "relationship": 3, "stability": 10},
    "metal": {"career": 5, "wealth": 3, "relationship": -2, "stability": 8},
    "water": {"career": 3, "wealth": 7, "relationship": 8, "stability": -1},
}

FOCUS_KEYS = {
    "career": "make_visible_progress",
    "wealth": "test_before_expanding",
    "relationship": "clarify_expectations",
    "stability": "build_repeatable_rhythm",
}

BOUNDARY_KEYS = {
    "career": "limit_scattered_goals",
    "wealth": "set_cost_and_exit_limits",
    "relationship": "replace_guessing_with_requests",
    "stability": "protect_recovery_and_focus",
}

EXPERIMENT_KEYS = {
    "career": "ship_one_visible_result",
    "wealth": "run_one_small_validation",
    "relationship": "hold_one_clear_conversation",
    "stability": "repeat_one_weekly_system",
}

ELEMENT_MARKS = {
    "wood": {"glyph": "生", "palette_key": "jade", "meaning_key": "growth"},
    "fire": {"glyph": "明", "palette_key": "coral", "meaning_key": "clarity"},
    "earth": {"glyph": "衡", "palette_key": "gold", "meaning_key": "balance"},
    "metal": {"glyph": "断", "palette_key": "silver", "meaning_key": "discernment"},
    "water": {"glyph": "流", "palette_key": "cyan", "meaning_key": "adaptation"},
}


def build_monthly_compass(
    core: dict[str, Any],
    trait_output: dict[str, Any],
    *,
    start_year: int,
    start_month: int,
    count: int = 6,
) -> dict[str, Any]:
    if not 1 <= start_month <= 12:
        raise ValueError("start_month must be between 1 and 12")
    count = max(1, min(count, 12))
    traits = trait_output["traits"]
    baseline = {
        "career": round((traits["career_momentum"]["score"] + traits["execution_stability"]["score"]) / 2),
        "wealth": round((traits["wealth_generation"]["score"] + traits["wealth_retention"]["score"]) / 2),
        "relationship": round(
            (traits["relationship_support"]["score"] + 100 - traits["relationship_pressure"]["score"]) / 2
        ),
        "stability": traits["execution_stability"]["score"],
    }
    trait_evidence = {
        "career": _merge_evidence(traits["career_momentum"], traits["execution_stability"]),
        "wealth": _merge_evidence(traits["wealth_generation"], traits["wealth_retention"]),
        "relationship": _merge_evidence(traits["relationship_support"], traits["relationship_pressure"]),
        "stability": list(traits["execution_stability"]["evidence_ids"]),
    }

    months = []
    calculation_evidence = []
    for offset in range(count):
        year, month = _add_months(start_year, start_month, offset)
        day = sxtwl.fromSolar(year, month, 15)
        month_gz = day.getMonthGZ()
        stem = STEMS[month_gz.tg]
        branch = BRANCHES[month_gz.dz]
        stem_element = STEM_ELEMENT[stem]
        branch_element = BRANCH_ELEMENT[branch]
        yin_yang = STEM_YIN_YANG[stem]
        shifts = _combined_shift(stem_element, branch_element, yin_yang)
        scores = {key: _clamp(baseline[key] + shifts[key]) for key in baseline}
        focus_dimension = max(shifts, key=shifts.get)
        boundary_dimension = min(shifts, key=shifts.get)
        evidence_id = f"monthly_compass.{year}-{month:02d}.pillar"
        calculation_evidence.append(
            {
                "id": evidence_id,
                "type": "monthly_pillar_proxy",
                "description": (
                    f"{year}-{month:02d} monthly pillar represented by the 15th day "
                    f"after the monthly solar-term boundary: {stem}{branch}"
                ),
                "confidence": 0.66,
            }
        )
        evidence_ids = sorted(
            {evidence_id}
            | set(trait_evidence[focus_dimension])
            | set(trait_evidence[boundary_dimension])
        )
        mark = ELEMENT_MARKS[branch_element]
        months.append(
            {
                "year": year,
                "month": month,
                "pillar": f"{stem}{branch}",
                "stem_element": stem_element,
                "branch_element": branch_element,
                "yin_yang": yin_yang,
                "scores": scores,
                "focus_key": FOCUS_KEYS[focus_dimension],
                "boundary_key": BOUNDARY_KEYS[boundary_dimension],
                "experiment_key": EXPERIMENT_KEYS[focus_dimension],
                "reflection_key": f"reflect_{boundary_dimension}",
                "mark": {
                    **mark,
                    "pattern_key": "expanding" if yin_yang == "yang" else "gathering",
                    "collection_id": f"{year}{month:02d}-{stem}{branch}-{mark['glyph']}",
                },
                "confidence": _confidence(traits, focus_dimension, boundary_dimension),
                "evidence_ids": evidence_ids,
            }
        )

    return {
        "schema_version": MONTHLY_SCHEMA_VERSION,
        "model_version": MONTHLY_MODEL_VERSION,
        "core_schema_version": core["schema_version"],
        "trait_schema_version": trait_output["schema_version"],
        "start_month": f"{start_year:04d}-{start_month:02d}",
        "months": months,
        "calculation_evidence": calculation_evidence,
    }


def _combined_shift(stem_element: str, branch_element: str, yin_yang: str) -> dict[str, int]:
    polarity = (
        {"career": 2, "wealth": 1, "relationship": -1, "stability": -2}
        if yin_yang == "yang"
        else {"career": -1, "wealth": 0, "relationship": 2, "stability": 2}
    )
    return {
        key: round(ELEMENT_SHIFT[branch_element][key] + ELEMENT_SHIFT[stem_element][key] * 0.4 + polarity[key])
        for key in polarity
    }


def _confidence(
    traits: dict[str, dict[str, Any]],
    focus_dimension: str,
    boundary_dimension: str,
) -> float:
    keys = {
        "career": ("career_momentum", "execution_stability"),
        "wealth": ("wealth_generation", "wealth_retention"),
        "relationship": ("relationship_support", "relationship_pressure"),
        "stability": ("execution_stability",),
    }
    selected = keys[focus_dimension] + keys[boundary_dimension]
    average = sum(traits[key]["confidence"] for key in selected) / len(selected)
    return round(min(0.68, average * 0.78), 2)


def _merge_evidence(*traits: dict[str, Any]) -> list[str]:
    return sorted({item for trait in traits for item in trait["evidence_ids"]})


def _add_months(year: int, month: int, offset: int) -> tuple[int, int]:
    index = year * 12 + (month - 1) + offset
    return index // 12, index % 12 + 1


def _clamp(value: int) -> int:
    return max(0, min(int(value), 100))


def monthly_compass_schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "schemas" / "bazi-monthly-compass-v1.schema.json"
