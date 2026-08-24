from __future__ import annotations

from datetime import date
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from .generator import CALCULATION_MODEL_VERSION, INTERPRETATION_MODEL_VERSION
from .trait_engine import TRAIT_INTERPRETATION_MODEL_VERSION, TRAIT_MODEL_VERSION, TRAIT_WEIGHT_VERSION


def _package_version(package: str, fallback: str) -> str:
    try:
        return version(package)
    except PackageNotFoundError:
        return fallback


SYSTEM_VERSION = "2026.08.21"
CALCULATION_DATA_VERSION = "2026.08"
LOCATION_DATA_VERSION = "world-locations-v1"
RULE_MODEL_VERSION = CALCULATION_MODEL_VERSION
ANNUAL_MODEL_VERSION = "annual-trait-rules-v1"
MONTHLY_MODEL_VERSION = "monthly-compass-v1"
ORACLE_MODEL_VERSION = "three-coin-change-rules-v1"
INTERPRETATION_VERSION = INTERPRETATION_MODEL_VERSION
CONTENT_COPY_VERSION = "en-US-zh-CN-2026.08"
LAST_METHODOLOGY_REVIEW = "2026-08-21"


def build_system_status() -> dict[str, Any]:
    return {
        "system_version": SYSTEM_VERSION,
        "last_methodology_review": LAST_METHODOLOGY_REVIEW,
        "generated_at": date.today().isoformat(),
        "versions": {
            "calculation_data": CALCULATION_DATA_VERSION,
            "location_data": LOCATION_DATA_VERSION,
            "rule_model": RULE_MODEL_VERSION,
            "trait_model": TRAIT_MODEL_VERSION,
            "trait_weight_model": TRAIT_WEIGHT_VERSION,
            "interpretation_model": INTERPRETATION_VERSION,
            "trait_interpretation_model": TRAIT_INTERPRETATION_MODEL_VERSION,
            "annual_model": ANNUAL_MODEL_VERSION,
            "monthly_model": MONTHLY_MODEL_VERSION,
            "oracle_model": ORACLE_MODEL_VERSION,
            "content_copy": CONTENT_COPY_VERSION,
            "calendar_dependency": f"sxtwl {_package_version('sxtwl', '2.0.7')}",
            "timezone_dependency": "Python zoneinfo / host tzdata",
        },
        "data_sources": [
            {
                "key": "traditional_rule_tables",
                "label": "Heavenly stems, earthly branches, five elements, ten-god relationships, hidden stems",
                "source_type": "curated_internal_rules",
                "update_policy": "Manual review only; release as a versioned rule-model update.",
            },
            {
                "key": "calendar_and_solar_terms",
                "label": "Chinese calendar, stems/branches, solar-term boundaries",
                "source_type": "pinned_dependency",
                "update_policy": "Quarterly dependency check; upgrade only after regression tests pass.",
            },
            {
                "key": "timezone_and_location",
                "label": "IANA timezone names, city list, approximate longitude/latitude",
                "source_type": "bundled_dataset",
                "update_policy": "Semi-automatic refresh every 3-6 months, followed by manual acceptance testing.",
            },
            {
                "key": "daily_monthly_annual_content",
                "label": "Daily cards, monthly compass, annual rhythm",
                "source_type": "deterministic_derivation",
                "update_policy": "Generated from user input, chart structure, and date rhythm; not an external ranking or live prediction feed.",
            },
            {
                "key": "copy_and_localization",
                "label": "English and Chinese explanatory copy",
                "source_type": "curated_product_copy",
                "update_policy": "Manual editorial review every 2-4 weeks during launch iteration.",
            },
        ],
        "release_policy": {
            "automatic_generation": [
                "daily_card",
                "daily_seal",
                "monthly_compass",
                "annual_rhythm",
            ],
            "manual_review_required": [
                "rule_tables",
                "calendar_dependency_upgrade",
                "location_dataset_release",
                "paid_report_copy",
                "app_store_metadata",
                "privacy_terms_support_copy",
            ],
        },
        "boundaries": [
            "MING is for cultural exploration and personal reflection.",
            "The system does not provide medical, legal, financial, mental-health, safety, or emergency advice.",
            "Daily, monthly, and annual outputs are pattern-based prompts, not guaranteed predictions.",
            "Birth details are processed to generate the requested reading and are not used for advertising tracking.",
        ],
    }
