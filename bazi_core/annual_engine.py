from __future__ import annotations

from pathlib import Path
from typing import Any

ANNUAL_SCHEMA_VERSION = "1.0.0"
ANNUAL_MODEL_VERSION = "annual-trait-rules-v1"

ELEMENT_MODIFIERS = {
    "wood": {"career": 8, "wealth": 2, "relationship": 4, "stability": -3},
    "fire": {"career": 7, "wealth": 5, "relationship": 2, "stability": -5},
    "earth": {"career": 2, "wealth": 4, "relationship": 3, "stability": 9},
    "metal": {"career": 5, "wealth": 3, "relationship": -2, "stability": 7},
    "water": {"career": 3, "wealth": 6, "relationship": 7, "stability": -1},
}

FOCUS_KEYS = {
    "career": "career_progress",
    "wealth": "wealth_boundaries",
    "relationship": "relationship_communication",
    "stability": "execution_rhythm",
}

CAUTION_KEYS = {
    "career": "avoid_scattered_goals",
    "wealth": "avoid_unbounded_input",
    "relationship": "avoid_unspoken_expectations",
    "stability": "avoid_overcommitment",
}


def build_annual_outlook(
    core: dict[str, Any],
    trait_output: dict[str, Any],
    *,
    years: int = 5,
) -> dict[str, Any]:
    traits = trait_output["traits"]
    baseline = {
        "career": round((traits["career_momentum"]["score"] + traits["execution_stability"]["score"]) / 2),
        "wealth": round((traits["wealth_generation"]["score"] + traits["wealth_retention"]["score"]) / 2),
        "relationship": round(
            (traits["relationship_support"]["score"] + (100 - traits["relationship_pressure"]["score"])) / 2
        ),
        "stability": traits["execution_stability"]["score"],
    }
    trait_evidence = {
        "career": _merge_evidence(traits["career_momentum"], traits["execution_stability"]),
        "wealth": _merge_evidence(traits["wealth_generation"], traits["wealth_retention"]),
        "relationship": _merge_evidence(traits["relationship_support"], traits["relationship_pressure"]),
        "stability": list(traits["execution_stability"]["evidence_ids"]),
    }

    outlook = []
    for annual in core["annual_flows"][:years]:
        branch_element = annual["pillar"]["branch"]["element"]
        stem_element = annual["pillar"]["stem"]["element"]
        yin_yang = annual["pillar"]["stem"]["yin_yang"]
        branch_modifiers = ELEMENT_MODIFIERS[branch_element]
        stem_modifiers = ELEMENT_MODIFIERS[stem_element]
        polarity_modifiers = (
            {"career": 2, "wealth": 1, "relationship": -1, "stability": -2}
            if yin_yang == "yang"
            else {"career": -1, "wealth": 0, "relationship": 2, "stability": 2}
        )
        modifiers = {
            key: round(branch_modifiers[key] + stem_modifiers[key] * 0.45 + polarity_modifiers[key])
            for key in baseline
        }
        scores = {
            key: _clamp(round(baseline[key] + modifiers[key]), 0, 100)
            for key in baseline
        }
        strongest = max(modifiers, key=modifiers.get)
        weakest = min(modifiers, key=modifiers.get)
        evidence_ids = sorted(
            set(annual.get("evidence_ids", []))
            | set(trait_evidence[strongest])
            | set(trait_evidence[weakest])
        )
        outlook.append(
            {
                "year": annual["year"],
                "pillar": f"{annual['pillar']['stem']['char']}{annual['pillar']['branch']['char']}",
                "theme_element": branch_element,
                "scores": scores,
                "focus_key": FOCUS_KEYS[strongest],
                "caution_key": CAUTION_KEYS[weakest],
                "confidence": _confidence(
                    traits,
                    strongest,
                    weakest,
                    annual.get("evidence_ids", []),
                ),
                "evidence_ids": evidence_ids,
            }
        )

    return {
        "schema_version": ANNUAL_SCHEMA_VERSION,
        "model_version": ANNUAL_MODEL_VERSION,
        "core_schema_version": core["schema_version"],
        "trait_schema_version": trait_output["schema_version"],
        "years": outlook,
    }


def _merge_evidence(*traits: dict[str, Any]) -> list[str]:
    return sorted({evidence_id for trait in traits for evidence_id in trait["evidence_ids"]})


def _confidence(
    traits: dict[str, dict[str, Any]],
    strongest: str,
    weakest: str,
    annual_evidence: list[str],
) -> float:
    trait_keys = {
        "career": ("career_momentum", "execution_stability"),
        "wealth": ("wealth_generation", "wealth_retention"),
        "relationship": ("relationship_support", "relationship_pressure"),
        "stability": ("execution_stability",),
    }
    selected = trait_keys[strongest] + trait_keys[weakest]
    average = sum(traits[key]["confidence"] for key in selected) / len(selected)
    annual_bonus = 0.03 if annual_evidence else 0
    return round(min(0.72, average * 0.82 + annual_bonus), 2)


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(value, upper))


def annual_schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "schemas" / "bazi-annual-outlook-v1.schema.json"
