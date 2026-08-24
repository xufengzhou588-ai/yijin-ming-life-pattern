from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import sxtwl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bazi_core.generator import build_core_output
from bazi_core.tables import JIE_INDICES, JIE_QI_NAMES
from bazi_core.trait_engine import build_trait_output


OUTPUT = ROOT / "tests" / "fixtures" / "bazi_golden_v1.json"


def main() -> None:
    cases = _fixture_inputs()
    fixtures = [_build_fixture(case) for case in cases]
    payload = {
        "fixture_set_version": "bazi-golden-v1",
        "case_count": len(fixtures),
        "source_policy": "docs/calculation-policy-v1.md",
        "source_type": "pinned_sxtwl_zoneinfo_snapshot_pending_professional_blind_review",
        "generated_by": "tools/generate_bazi_golden_fixtures.py",
        "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "cases": fixtures,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _fixture_inputs() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    cases.extend(_solar_term_boundary_cases())
    cases.extend(_zi_hour_cases())
    cases.extend(_us_dst_cases())
    cases.extend(_china_historical_timezone_cases())
    cases.extend(_true_solar_cross_branch_cases())
    cases.extend(_unknown_time_cases())
    cases.extend(_leap_and_cross_year_cases())
    assert 100 <= len(cases) <= 300, len(cases)
    return cases


def _base(case_id: str, category: str, birth_datetime: str, timezone: str, **overrides: Any) -> dict[str, Any]:
    item = {
        "id": case_id,
        "category": category,
        "input": {
            "birth_datetime": birth_datetime,
            "timezone": timezone,
            "gender": overrides.pop("gender", "unknown"),
            "calendar": "gregorian",
            "country": overrides.pop("country", ""),
            "region": overrides.pop("region", ""),
            "city": overrides.pop("city", ""),
            "longitude": overrides.pop("longitude", None),
            "latitude": overrides.pop("latitude", None),
            "use_true_solar_time": overrides.pop("use_true_solar_time", False),
            "birth_time_accuracy": overrides.pop("birth_time_accuracy", "exact"),
            "annual_years": overrides.pop("annual_years", 3),
            "annual_start_year": overrides.pop("annual_start_year", 2026),
            "luck_cycles": overrides.pop("luck_cycles", 3),
        },
    }
    item["input"] = {key: value for key, value in item["input"].items() if value is not None}
    if overrides:
        raise ValueError(f"unused overrides for {case_id}: {sorted(overrides)}")
    return item


def _solar_term_boundary_cases() -> list[dict[str, Any]]:
    cases = []
    for info in sxtwl.getJieQiByYear(2024):
        if info.jqIndex not in JIE_INDICES:
            continue
        dt = _datetime_from_jd(info.jd)
        name = JIE_QI_NAMES.get(info.jqIndex, f"jie_{info.jqIndex}")
        for minutes in (-1, 1):
            moment = dt + timedelta(minutes=minutes)
            suffix = "before" if minutes < 0 else "after"
            cases.append(
                _base(
                    f"solar-term-2024-{info.jqIndex:02d}-{suffix}",
                    "solar_term_boundary",
                    moment.strftime("%Y-%m-%dT%H:%M:00+08:00"),
                    "Asia/Shanghai",
                    gender="male",
                    country="CN",
                    region="Shanghai",
                    city=f"{name}-{suffix}",
                    longitude=121.4737,
                    latitude=31.2304,
                )
            )
    return cases


def _zi_hour_cases() -> list[dict[str, Any]]:
    dates = ["2024-02-10", "2024-06-05", "2024-12-31", "2025-01-01", "1990-05-17", "1988-08-08"]
    cases = []
    for index, day in enumerate(dates):
        for clock in ("23:30", "00:30"):
            actual_day = datetime.fromisoformat(f"{day}T00:00:00")
            if clock == "00:30":
                actual_day += timedelta(days=1)
            cases.append(
                _base(
                    f"zi-hour-{index:02d}-{clock.replace(':', '')}",
                    "zi_hour_day_boundary",
                    actual_day.strftime(f"%Y-%m-%dT{clock}:00+08:00"),
                    "Asia/Shanghai",
                    gender="female",
                    country="CN",
                    region="Shanghai",
                    city="Shanghai",
                )
            )
    return cases


def _us_dst_cases() -> list[dict[str, Any]]:
    cases = []
    moments = [
        ("2024-03-10T01:30:00", "before-spring"),
        ("2024-03-10T03:30:00", "after-spring"),
        ("2024-11-03T00:30:00", "before-fall"),
        ("2024-11-03T02:30:00", "after-fall"),
        ("2025-03-09T01:30:00", "before-spring"),
        ("2025-03-09T03:30:00", "after-spring"),
    ]
    cities = [
        ("America/New_York", "US", "New York", "New York City", -74.006, 40.7128),
        ("America/Los_Angeles", "US", "California", "Los Angeles", -118.2437, 34.0522),
    ]
    for timezone, country, region, city, longitude, latitude in cities:
        for moment, label in moments:
            cases.append(
                _base(
                    f"us-dst-{city.lower().replace(' ', '-')}-{label}-{moment[:4]}",
                    "us_dst",
                    moment,
                    timezone,
                    gender="female",
                    country=country,
                    region=region,
                    city=city,
                    longitude=longitude,
                    latitude=latitude,
                )
            )
    return cases


def _china_historical_timezone_cases() -> list[dict[str, Any]]:
    moments = [
        "1900-01-01T08:30:00",
        "1912-02-12T23:30:00",
        "1927-12-31T23:30:00",
        "1949-05-01T00:30:00",
        "1966-08-08T08:08:00",
        "1986-05-04T01:30:00",
        "1991-09-15T01:30:00",
        "2024-02-04T16:27:00",
    ]
    return [
        _base(
            f"china-history-{index:02d}",
            "china_historical_timezone",
            moment,
            "Asia/Shanghai",
            gender="unknown",
            country="CN",
            region="Shanghai",
            city="Shanghai",
            longitude=121.4737,
            latitude=31.2304,
        )
        for index, moment in enumerate(moments)
    ]


def _true_solar_cross_branch_cases() -> list[dict[str, Any]]:
    places = [
        ("kashgar", "CN", "新疆维吾尔自治区", "喀什市", 75.9898, 39.4704),
        ("urumqi", "CN", "新疆维吾尔自治区", "乌鲁木齐市", 87.6168, 43.8256),
        ("guangzhou", "CN", "Guangdong", "Guangzhou", 113.2644, 23.1291),
        ("new-york", "US", "New York", "New York City", -74.006, 40.7128),
    ]
    clocks = ["00:20", "01:10", "08:30", "22:40", "23:20"]
    cases = []
    for place, country, region, city, longitude, latitude in places:
        timezone = "Asia/Shanghai" if country == "CN" else "America/New_York"
        for clock in clocks:
            cases.append(
                _base(
                    f"true-solar-{place}-{clock.replace(':', '')}",
                    "true_solar_cross_branch",
                    f"1990-05-17T{clock}:00",
                    timezone,
                    gender="male",
                    country=country,
                    region=region,
                    city=city,
                    longitude=longitude,
                    latitude=latitude,
                    use_true_solar_time=True,
                )
            )
    return cases


def _unknown_time_cases() -> list[dict[str, Any]]:
    moments = [
        "1990-05-17T08:30:00+08:00",
        "1988-08-08T14:20:00+08:00",
        "2001-09-09T11:05:00-04:00",
        "2024-02-04T16:25:00+08:00",
        "2024-03-10T03:30:00",
        "2024-02-29T23:30:00+08:00",
        "2023-12-31T23:30:00+08:00",
        "1900-01-01T08:30:00",
    ]
    cases = []
    for index, moment in enumerate(moments):
        timezone = "America/New_York" if index in {2, 4} else "Asia/Shanghai"
        country = "US" if timezone.startswith("America") else "CN"
        for accuracy in ("approximate", "unknown"):
            cases.append(
                _base(
                    f"unknown-time-{index:02d}-{accuracy}",
                    "unknown_birth_time",
                    moment,
                    timezone,
                    gender="unknown",
                    country=country,
                    region="New York" if country == "US" else "Shanghai",
                    city="New York City" if country == "US" else "Shanghai",
                    longitude=-74.006 if country == "US" else 121.4737,
                    latitude=40.7128 if country == "US" else 31.2304,
                    birth_time_accuracy=accuracy,
                )
            )
    return cases


def _leap_and_cross_year_cases() -> list[dict[str, Any]]:
    moments = [
        "1904-02-29T00:30:00+08:00",
        "2000-02-29T23:30:00+08:00",
        "2024-02-29T23:30:00+08:00",
        "2096-02-29T12:00:00+08:00",
        "1999-12-31T23:30:00+08:00",
        "2000-01-01T00:30:00+08:00",
        "2023-12-31T23:30:00+08:00",
        "2024-01-01T00:30:00+08:00",
        "2024-02-09T23:30:00+08:00",
        "2024-02-10T00:30:00+08:00",
    ]
    return [
        _base(
            f"leap-cross-year-{index:02d}",
            "leap_and_cross_year",
            moment,
            "Asia/Shanghai",
            gender="female",
            country="CN",
            region="Shanghai",
            city="Shanghai",
            longitude=121.4737,
            latitude=31.2304,
        )
        for index, moment in enumerate(moments)
    ]


def _datetime_from_jd(jd: float) -> datetime:
    value = sxtwl.JD2DD(jd)
    return datetime(int(value.Y), int(value.M), int(value.D), int(value.h), int(value.m), int(value.s))


def _build_fixture(case: dict[str, Any]) -> dict[str, Any]:
    core = build_core_output(**case["input"])
    traits = build_trait_output(core)
    pillars = {
        position: core["chart"][position]["stem"]["char"] + core["chart"][position]["branch"]["char"]
        for position in ("year", "month", "day", "hour")
    }
    return {
        "id": case["id"],
        "category": case["category"],
        "input": case["input"],
        "expected": {
            "schema_version": core["schema_version"],
            "model_versions": core["model_versions"],
            "trait_model_version": traits["model_version"],
            "trait_weight_version": traits["weight_version"],
            "birth_datetime": core["input"]["birth_datetime"],
            "pillars": pillars,
            "day_master": core["chart"]["day_master"]["char"],
            "confidence": core["confidence"],
            "uncertainty_reasons": core["uncertainty_reasons"],
            "main_reminder": traits["context"]["main_reminder"],
        },
    }


if __name__ == "__main__":
    main()
