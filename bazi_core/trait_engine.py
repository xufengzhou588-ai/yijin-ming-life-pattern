from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

TRAIT_SCHEMA_VERSION = "1.0.0"
TRAIT_MODEL_VERSION = "trait-rules-v1"

Direction = Literal["positive", "negative"]


@dataclass(frozen=True)
class FactorRule:
    signal_group: Literal["ten_gods", "elements"]
    signal_key: str
    weight: float
    direction: Direction
    label_key: str


TRAIT_RULES: dict[str, tuple[FactorRule, ...]] = {
    "career_momentum": (
        FactorRule("ten_gods", "eating_god", 0.65, "positive", "structured_output"),
        FactorRule("ten_gods", "hurting_officer", 0.75, "positive", "expressive_output"),
        FactorRule("ten_gods", "direct_officer", 0.55, "positive", "responsibility"),
        FactorRule("ten_gods", "seven_killings", 0.45, "positive", "challenge_drive"),
        FactorRule("ten_gods", "indirect_resource", 0.25, "negative", "analysis_delay"),
    ),
    "leadership_drive": (
        FactorRule("ten_gods", "seven_killings", 0.8, "positive", "challenge_drive"),
        FactorRule("ten_gods", "hurting_officer", 0.55, "positive", "independent_expression"),
        FactorRule("ten_gods", "peer", 0.35, "positive", "self_direction"),
        FactorRule("ten_gods", "direct_resource", 0.2, "negative", "support_dependence"),
    ),
    "execution_stability": (
        FactorRule("ten_gods", "direct_officer", 0.85, "positive", "rule_awareness"),
        FactorRule("ten_gods", "direct_wealth", 0.55, "positive", "practical_follow_through"),
        FactorRule("ten_gods", "eating_god", 0.35, "positive", "steady_output"),
        FactorRule("ten_gods", "hurting_officer", 0.35, "negative", "rule_friction"),
        FactorRule("ten_gods", "rob_wealth", 0.35, "negative", "priority_competition"),
    ),
    "learning_capacity": (
        FactorRule("ten_gods", "direct_resource", 0.85, "positive", "structured_learning"),
        FactorRule("ten_gods", "indirect_resource", 0.8, "positive", "pattern_learning"),
        FactorRule("ten_gods", "eating_god", 0.3, "positive", "knowledge_expression"),
        FactorRule("ten_gods", "hurting_officer", 0.2, "negative", "premature_conclusion"),
    ),
    "wealth_generation": (
        FactorRule("ten_gods", "direct_wealth", 0.8, "positive", "stable_opportunity"),
        FactorRule("ten_gods", "indirect_wealth", 0.85, "positive", "market_opportunity"),
        FactorRule("ten_gods", "eating_god", 0.45, "positive", "value_creation"),
        FactorRule("ten_gods", "hurting_officer", 0.5, "positive", "commercial_expression"),
        FactorRule("ten_gods", "indirect_resource", 0.2, "negative", "analysis_delay"),
    ),
    "wealth_retention": (
        FactorRule("ten_gods", "direct_wealth", 0.8, "positive", "budget_awareness"),
        FactorRule("ten_gods", "direct_officer", 0.55, "positive", "financial_rules"),
        FactorRule("ten_gods", "direct_resource", 0.35, "positive", "resource_buffer"),
        FactorRule("ten_gods", "rob_wealth", 0.85, "negative", "resource_competition"),
        FactorRule("ten_gods", "indirect_wealth", 0.45, "negative", "opportunity_expansion"),
        FactorRule("ten_gods", "hurting_officer", 0.25, "negative", "impulse_expression"),
    ),
    "relationship_support": (
        FactorRule("ten_gods", "direct_resource", 0.8, "positive", "stable_support"),
        FactorRule("ten_gods", "indirect_resource", 0.65, "positive", "adaptive_support"),
        FactorRule("ten_gods", "direct_wealth", 0.3, "positive", "practical_care"),
        FactorRule("ten_gods", "rob_wealth", 0.3, "negative", "boundary_competition"),
    ),
    "relationship_pressure": (
        FactorRule("ten_gods", "seven_killings", 0.75, "positive", "high_expectation"),
        FactorRule("ten_gods", "direct_officer", 0.5, "positive", "role_pressure"),
        FactorRule("ten_gods", "rob_wealth", 0.65, "positive", "boundary_competition"),
        FactorRule("ten_gods", "hurting_officer", 0.35, "positive", "communication_friction"),
        FactorRule("ten_gods", "direct_resource", 0.35, "negative", "stable_support"),
    ),
    "risk_appetite": (
        FactorRule("ten_gods", "indirect_wealth", 0.8, "positive", "opportunity_expansion"),
        FactorRule("ten_gods", "seven_killings", 0.65, "positive", "challenge_drive"),
        FactorRule("ten_gods", "hurting_officer", 0.55, "positive", "independent_expression"),
        FactorRule("ten_gods", "direct_officer", 0.5, "negative", "rule_awareness"),
        FactorRule("ten_gods", "direct_wealth", 0.35, "negative", "budget_awareness"),
    ),
    "resource_integration": (
        FactorRule("ten_gods", "direct_resource", 0.55, "positive", "structured_learning"),
        FactorRule("ten_gods", "indirect_resource", 0.65, "positive", "pattern_learning"),
        FactorRule("ten_gods", "direct_wealth", 0.45, "positive", "practical_follow_through"),
        FactorRule("ten_gods", "eating_god", 0.4, "positive", "knowledge_expression"),
        FactorRule("ten_gods", "rob_wealth", 0.3, "negative", "resource_competition"),
    ),
}


def build_trait_output(core: dict[str, Any]) -> dict[str, Any]:
    evidence_lookup = {item["id"]: item for item in core["evidence"]}
    element_entries = sorted(core["elements"].items(), key=lambda item: item[1]["adjusted"], reverse=True)
    ten_god_entries = sorted(core["ten_gods"].items(), key=lambda item: item[1]["adjusted"], reverse=True)
    element_max = max((item[1]["adjusted"] for item in element_entries), default=1.0) or 1.0
    ten_god_max = max((item[1]["adjusted"] for item in ten_god_entries), default=1.0) or 1.0

    traits = {
        trait_key: _evaluate_trait(
            trait_key,
            rules,
            core,
            evidence_lookup,
            element_max=element_max,
            ten_god_max=ten_god_max,
        )
        for trait_key, rules in TRAIT_RULES.items()
    }
    reminders = {
        "wealth_retention": 100 - traits["wealth_retention"]["score"],
        "relationship_pressure": traits["relationship_pressure"]["score"],
        "execution_stability": 100 - traits["execution_stability"]["score"],
    }
    main_reminder = max(reminders, key=reminders.get)
    all_evidence_ids = sorted({evidence_id for trait in traits.values() for evidence_id in trait["evidence_ids"]})

    return {
        "schema_version": TRAIT_SCHEMA_VERSION,
        "model_version": TRAIT_MODEL_VERSION,
        "core_schema_version": core["schema_version"],
        "context": {
            "strongest_element": element_entries[0][0],
            "strongest_ten_god": ten_god_entries[0][0],
            "main_reminder": main_reminder,
        },
        "traits": traits,
        "evidence_ids": all_evidence_ids,
    }


def _evaluate_trait(
    trait_key: str,
    rules: tuple[FactorRule, ...],
    core: dict[str, Any],
    evidence_lookup: dict[str, dict[str, Any]],
    *,
    element_max: float,
    ten_god_max: float,
) -> dict[str, Any]:
    positive_rules = [rule for rule in rules if rule.direction == "positive"]
    negative_rules = [rule for rule in rules if rule.direction == "negative"]
    positive_strength = _group_strength(positive_rules, core, element_max, ten_god_max)
    negative_strength = _group_strength(negative_rules, core, element_max, ten_god_max)
    # V1 is an uncalibrated structural model. Keep a neutral baseline and let
    # negative factors constrain, rather than erase, the positive signal.
    score = round(_clamp(25 + (positive_strength * 0.75) - (negative_strength * 0.2), 0.0, 100.0))

    positive_factors = _build_factors(positive_rules, core, element_max, ten_god_max)
    negative_factors = _build_factors(negative_rules, core, element_max, ten_god_max)
    evidence_ids = sorted({
        evidence_id
        for factor in positive_factors + negative_factors
        for evidence_id in factor["evidence_ids"]
    })
    confidence = _confidence(evidence_ids, evidence_lookup, positive_strength, negative_strength)
    return {
        "trait": trait_key,
        "score": score,
        "level": _level(score),
        "confidence": confidence,
        "positive_factors": positive_factors,
        "negative_factors": negative_factors,
        "evidence_ids": evidence_ids,
    }


def _group_strength(
    rules: list[FactorRule],
    core: dict[str, Any],
    element_max: float,
    ten_god_max: float,
) -> float:
    if not rules:
        return 0.0
    weighted = sum(
        rule.weight * _signal_intensity(rule, core, element_max, ten_god_max)
        for rule in rules
    )
    return (weighted / sum(rule.weight for rule in rules)) * 100


def _signal_intensity(
    rule: FactorRule,
    core: dict[str, Any],
    element_max: float,
    ten_god_max: float,
) -> float:
    bundle = core[rule.signal_group][rule.signal_key]
    denominator = element_max if rule.signal_group == "elements" else ten_god_max
    return _clamp(bundle["adjusted"] / denominator, 0.0, 1.0)


def _build_factors(
    rules: list[FactorRule],
    core: dict[str, Any],
    element_max: float,
    ten_god_max: float,
) -> list[dict[str, Any]]:
    factors = []
    for rule in rules:
        bundle = core[rule.signal_group][rule.signal_key]
        intensity = _signal_intensity(rule, core, element_max, ten_god_max)
        if intensity <= 0:
            continue
        factors.append(
            {
                "id": f"{rule.signal_group}.{rule.signal_key}",
                "label_key": rule.label_key,
                "direction": rule.direction,
                "contribution": round(rule.weight * intensity * 100, 2),
                "evidence_ids": sorted(set(bundle["evidence_ids"])),
            }
        )
    return sorted(factors, key=lambda factor: factor["contribution"], reverse=True)


def _confidence(
    evidence_ids: list[str],
    evidence_lookup: dict[str, dict[str, Any]],
    positive_strength: float,
    negative_strength: float,
) -> float:
    if not evidence_ids:
        return 0.35
    source_confidence = sum(evidence_lookup[item]["confidence"] for item in evidence_ids) / len(evidence_ids)
    coverage = min(len(evidence_ids) / 8, 1.0)
    signal_strength = min(max(positive_strength, negative_strength) / 75, 1.0)
    # Confidence reflects evidence coverage but is capped by the current
    # uncalibrated trait-rule model. Historical calibration can raise it later.
    return round(_clamp(0.24 + source_confidence * 0.25 + coverage * 0.18 + signal_strength * 0.08, 0.0, 0.76), 2)


def _level(score: int) -> str:
    if score >= 82:
        return "very_prominent"
    if score >= 62:
        return "relatively_strong"
    if score >= 38:
        return "moderate"
    if score >= 18:
        return "relatively_weak"
    return "very_weak"


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def trait_schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "schemas" / "bazi-trait-output-v1.schema.json"
