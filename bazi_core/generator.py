from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import cos, floor, pi, sin
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import sxtwl

from .tables import (
    BRANCH_ELEMENT,
    BRANCH_YIN_YANG,
    BRANCHES,
    CONTROLS,
    ELEMENTS,
    GENERATES,
    HIDDEN_STEMS,
    JIE_INDICES,
    JIE_QI_NAMES,
    STEM_ELEMENT,
    STEM_YIN_YANG,
    STEMS,
    TEN_GODS,
)

SCHEMA_VERSION = "1.0.0"
CALCULATION_MODEL_VERSION = "bazi-calculation-rules-v1"
INTERPRETATION_MODEL_VERSION = "bazi-structural-interpretation-v1"
POSITION_NAMES = ["year", "month", "day", "hour"]
TIME_ACCURACY_CONFIDENCE = {
    "exact": 1.0,
    "approximate": 0.74,
    "unknown": 0.42,
}


@dataclass(frozen=True)
class BirthInput:
    birth_datetime: datetime
    timezone: str
    gender: str = "unknown"
    calendar: str = "gregorian"
    country: str = ""
    region: str = ""
    city: str = ""
    longitude: float | None = None
    latitude: float | None = None
    use_true_solar_time: bool = False
    birth_time_accuracy: str = "exact"


def build_core_output(
    *,
    birth_datetime: str | datetime,
    timezone: str,
    gender: str = "unknown",
    calendar: str = "gregorian",
    country: str = "",
    region: str = "",
    city: str = "",
    longitude: float | None = None,
    latitude: float | None = None,
    use_true_solar_time: bool = False,
    birth_time_accuracy: str = "exact",
    annual_years: int = 12,
    annual_start_year: int | None = None,
    luck_cycles: int = 8,
) -> dict[str, Any]:
    birth = _normalize_input(
        birth_datetime=birth_datetime,
        timezone=timezone,
        gender=gender,
        calendar=calendar,
        country=country,
        region=region,
        city=city,
        longitude=longitude,
        latitude=latitude,
        use_true_solar_time=use_true_solar_time,
        birth_time_accuracy=birth_time_accuracy,
    )
    warnings: list[str] = []
    if birth.calendar != "gregorian":
        raise ValueError("BaziCoreOutput v1 generator currently supports gregorian input only.")
    if birth.gender == "unknown":
        warnings.append("gender unknown; luck cycle direction defaults to forward")
    uncertainty_reasons = _uncertainty_reasons(birth)
    if birth.birth_time_accuracy == "unknown":
        warnings.append("birth time unknown; selected clock time is treated as an hour-pillar placeholder")

    calculation_datetime, solar_correction_minutes = _calculation_datetime(birth)
    day = sxtwl.fromSolar(
        calculation_datetime.year,
        calculation_datetime.month,
        calculation_datetime.day,
    )
    evidence: list[dict[str, Any]] = []
    year_gz, month_gz = _year_month_gz_for_exact_jie_boundary(calculation_datetime, day, evidence)
    pillar_gz = {
        "year": year_gz,
        "month": month_gz,
        "day": day.getDayGZ(),
        "hour": day.getHourGZ(calculation_datetime.hour),
    }

    evidence.append(
        _time_basis_evidence(
            birth,
            calculation_datetime,
            solar_correction_minutes,
        )
    )
    chart: dict[str, Any] = {}
    for position in POSITION_NAMES:
        chart[position] = _pillar_from_gz(pillar_gz[position], position, evidence)
    chart["day_master"] = deepcopy(chart["day"]["stem"])

    elements, ten_gods = _score_energy_and_ten_gods(chart, evidence)
    luck = _build_luck_cycles(birth, pillar_gz, evidence, luck_cycles)
    annual = _build_annual_flows(annual_start_year or birth.birth_datetime.year, annual_years, evidence)

    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "model_versions": {
            "calculation_model": CALCULATION_MODEL_VERSION,
            "interpretation_model": INTERPRETATION_MODEL_VERSION,
        },
        "confidence": _overall_confidence(birth, evidence),
        "uncertainty_reasons": uncertainty_reasons,
        "input": _input_payload(birth),
        "chart": chart,
        "elements": elements,
        "ten_gods": ten_gods,
        "luck_cycles": luck,
        "annual_flows": annual,
        "evidence": evidence,
    }
    if warnings:
        result["warnings"] = warnings
    return result


def _normalize_input(**kwargs: Any) -> BirthInput:
    raw_dt = kwargs["birth_datetime"]
    timezone = kwargs["timezone"]
    tz = ZoneInfo(timezone)
    if isinstance(raw_dt, datetime):
        dt = raw_dt
    else:
        dt = datetime.fromisoformat(raw_dt.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    birth_time_accuracy = kwargs.get("birth_time_accuracy") or "exact"
    if birth_time_accuracy not in TIME_ACCURACY_CONFIDENCE:
        raise ValueError("birth_time_accuracy must be exact, approximate, or unknown")
    return BirthInput(
        birth_datetime=dt,
        timezone=timezone,
        gender=kwargs["gender"],
        calendar=kwargs["calendar"],
        country=kwargs["country"],
        region=kwargs["region"],
        city=kwargs["city"],
        longitude=kwargs["longitude"],
        latitude=kwargs["latitude"],
        use_true_solar_time=kwargs["use_true_solar_time"],
        birth_time_accuracy=birth_time_accuracy,
    )


def _input_payload(birth: BirthInput) -> dict[str, Any]:
    location: dict[str, Any] = {
        "country": birth.country,
        "region": birth.region,
        "city": birth.city,
    }
    if birth.longitude is not None:
        location["longitude"] = birth.longitude
    if birth.latitude is not None:
        location["latitude"] = birth.latitude
    return {
        "calendar": birth.calendar,
        "birth_datetime": birth.birth_datetime.isoformat(),
        "timezone": birth.timezone,
        "gender": birth.gender,
        "birth_time_accuracy": birth.birth_time_accuracy,
        "location": location,
        "use_true_solar_time": birth.use_true_solar_time,
    }


def _uncertainty_reasons(birth: BirthInput) -> list[str]:
    reasons: list[str] = []
    if birth.birth_time_accuracy == "approximate":
        reasons.append("birth_time_approximate_hour_boundary_possible")
    elif birth.birth_time_accuracy == "unknown":
        reasons.append("birth_time_unknown_hour_pillar_placeholder")
    if birth.gender == "unknown":
        reasons.append("gender_unknown_luck_direction_defaulted")
    if birth.use_true_solar_time:
        reasons.append("true_solar_time_uses_approximate_equation_of_time")
    offset = birth.birth_datetime.utcoffset()
    if offset is not None and offset.total_seconds() % 60 != 0:
        reasons.append("historical_timezone_offset_has_subminute_component")
    return reasons


def _overall_confidence(birth: BirthInput, evidence: list[dict[str, Any]]) -> float:
    evidence_confidence = sum(item["confidence"] for item in evidence) / len(evidence) if evidence else 0.72
    time_confidence = TIME_ACCURACY_CONFIDENCE[birth.birth_time_accuracy]
    method_cap = 0.9 if not birth.use_true_solar_time else 0.84
    if birth.gender == "unknown":
        method_cap = min(method_cap, 0.82)
    return round(min(evidence_confidence, time_confidence, method_cap), 2)


def _calculation_datetime(birth: BirthInput) -> tuple[datetime, float]:
    if not birth.use_true_solar_time:
        return birth.birth_datetime, 0.0
    if birth.longitude is None:
        raise ValueError("longitude is required when true solar time is enabled")

    utc_offset = birth.birth_datetime.utcoffset()
    if utc_offset is None:
        raise ValueError("timezone offset is required when true solar time is enabled")

    day_of_year = birth.birth_datetime.timetuple().tm_yday
    days_in_year = 366 if _is_leap_year(birth.birth_datetime.year) else 365
    fractional_hour = (
        birth.birth_datetime.hour
        + birth.birth_datetime.minute / 60
        + birth.birth_datetime.second / 3600
    )
    fractional_year = 2 * pi / days_in_year * (
        day_of_year - 1 + (fractional_hour - 12) / 24
    )
    equation_of_time = 229.18 * (
        0.000075
        + 0.001868 * cos(fractional_year)
        - 0.032077 * sin(fractional_year)
        - 0.014615 * cos(2 * fractional_year)
        - 0.040849 * sin(2 * fractional_year)
    )
    utc_offset_minutes = utc_offset.total_seconds() / 60
    correction_minutes = equation_of_time + 4 * birth.longitude - utc_offset_minutes
    corrected = birth.birth_datetime + timedelta(minutes=correction_minutes)
    return corrected, round(correction_minutes, 2)


def _is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _year_month_gz_for_exact_jie_boundary(
    calculation_datetime: datetime,
    day: Any,
    evidence: list[dict[str, Any]],
) -> tuple[Any, Any]:
    birth_jd = _to_jd(calculation_datetime)
    for year in range(calculation_datetime.year - 1, calculation_datetime.year + 2):
        for info in sxtwl.getJieQiByYear(year):
            if info.jqIndex not in JIE_INDICES:
                continue
            boundary = sxtwl.JD2DD(info.jd)
            if (
                int(boundary.Y) == calculation_datetime.year
                and int(boundary.M) == calculation_datetime.month
                and int(boundary.D) == calculation_datetime.day
                and birth_jd < info.jd
            ):
                previous = calculation_datetime - timedelta(days=1)
                previous_day = sxtwl.fromSolar(previous.year, previous.month, previous.day)
                boundary_name = JIE_QI_NAMES.get(info.jqIndex, f"jie_qi_{info.jqIndex}")
                evidence.append(
                    _evidence(
                        "solar_term.minute_boundary",
                        "calculation",
                        "chart.year_month",
                        f"year and month pillars use the previous jie period before {boundary_name} at exact minute boundary",
                        1.0,
                        0.92,
                        "deterministic_core",
                        "sxtwl_jie_qi_minute_boundary_v1",
                        "month",
                    )
                )
                return previous_day.getYearGZ(), previous_day.getMonthGZ()
    return day.getYearGZ(), day.getMonthGZ()


def _time_basis_evidence(
    birth: BirthInput,
    calculation_datetime: datetime,
    correction_minutes: float,
) -> dict[str, Any]:
    if birth.use_true_solar_time:
        description = (
            f"true solar time applied: civil time {birth.birth_datetime.isoformat()} "
            f"shifted by {correction_minutes:+.2f} minutes to "
            f"{calculation_datetime.isoformat()}"
        )
        rule_id = "noaa_equation_of_time_longitude_v1"
        confidence = min(0.88, TIME_ACCURACY_CONFIDENCE[birth.birth_time_accuracy])
    else:
        description = (
            f"civil clock time used for pillar calculation: "
            f"{birth.birth_datetime.isoformat()}"
        )
        rule_id = "civil_clock_time_v1"
        confidence = TIME_ACCURACY_CONFIDENCE[birth.birth_time_accuracy]
    return _evidence(
        "input.time_basis",
        "calculation",
        "chart",
        description,
        correction_minutes,
        confidence,
        "deterministic_core",
        rule_id,
        "hour",
    )


def _stem(char: str) -> dict[str, str]:
    return {
        "char": char,
        "element": STEM_ELEMENT[char],
        "yin_yang": STEM_YIN_YANG[char],
    }


def _branch(char: str, position: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
    hidden = []
    for hidden_char, qi_type, weight in HIDDEN_STEMS[char]:
        ev_id = f"{position}.branch.{char}.hidden.{hidden_char}.{qi_type}"
        hidden.append({"stem": _stem(hidden_char), "qi_type": qi_type, "weight": weight})
        evidence.append(
            _evidence(
                ev_id,
                "branch_hidden_stem",
                f"{position}.branch.hidden_stems",
                f"{position} branch {char} contains hidden stem {hidden_char} as {qi_type} qi",
                weight,
                1.0,
                "deterministic_core",
                "hidden_stem_table_v1",
                position,
            )
        )
    return {
        "char": char,
        "element": BRANCH_ELEMENT[char],
        "yin_yang": BRANCH_YIN_YANG[char],
        "hidden_stems": hidden,
    }


def _pillar_from_gz(gz: Any, position: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
    stem_char = STEMS[gz.tg]
    branch_char = BRANCHES[gz.dz]
    evidence.append(
        _evidence(
            f"{position}.pillar",
            "calculation",
            f"chart.{position}",
            f"{position} pillar calculated as {stem_char}{branch_char}",
            1.0,
            1.0,
            "deterministic_core",
            "sxtwl_ganzhi_v1",
            position,
        )
    )
    evidence.append(
        _evidence(
            f"{position}.stem.{stem_char}",
            "stem_visible",
            f"chart.{position}.stem",
            f"{position} visible heavenly stem is {stem_char}",
            1.0,
            1.0,
            "deterministic_core",
            "sxtwl_ganzhi_v1",
            position,
        )
    )
    return {"stem": _stem(stem_char), "branch": _branch(branch_char, position, evidence)}


def _score_energy_and_ten_gods(
    chart: dict[str, Any],
    evidence: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    element_scores = {element: {"raw": 0.0, "evidence_ids": []} for element in ELEMENTS}
    ten_scores = {god: {"raw": 0.0, "evidence_ids": []} for god in TEN_GODS}
    day_master = chart["day_master"]

    for position in POSITION_NAMES:
        stem = chart[position]["stem"]
        stem_ev = f"{position}.stem.{stem['char']}"
        _add_element_score(element_scores, stem["element"], 1.0, stem_ev)
        if position != "day":
            god = ten_god(day_master, stem)
            _add_ten_god_score(ten_scores, god, 1.0, stem_ev)
            evidence.append(_ten_god_evidence(position, stem["char"], god, stem_ev, 1.0))

        for hidden in chart[position]["branch"]["hidden_stems"]:
            hidden_stem = hidden["stem"]
            contribution = round(0.5 * hidden["weight"], 4)
            hidden_ev = (
                f"{position}.branch.{chart[position]['branch']['char']}"
                f".hidden.{hidden_stem['char']}.{hidden['qi_type']}"
            )
            _add_element_score(element_scores, hidden_stem["element"], contribution, hidden_ev)
            god = ten_god(day_master, hidden_stem)
            _add_ten_god_score(ten_scores, god, contribution, hidden_ev)
            evidence.append(_ten_god_evidence(position, hidden_stem["char"], god, hidden_ev, contribution))

    month_element = chart["month"]["branch"]["element"]
    adjusted = {}
    for element, payload in element_scores.items():
        multiplier = _season_multiplier(element, month_element)
        adjusted_value = round(payload["raw"] * multiplier, 4)
        ev_id = f"elements.{element}.season_adjustment"
        evidence.append(
            _evidence(
                ev_id,
                "month_order",
                f"elements.{element}.adjusted",
                f"{element} adjusted by month branch element {month_element} with multiplier {multiplier}",
                multiplier,
                0.72,
                "energy_engine",
                "season_multiplier_v1",
                "month",
            )
        )
        adjusted[element] = {
            "raw": round(payload["raw"], 4),
            "adjusted": adjusted_value,
            "confidence": 0.72,
            "evidence_ids": payload["evidence_ids"] + [ev_id],
        }

    ten_gods = {
        god: {
            "raw": round(payload["raw"], 4),
            "adjusted": round(payload["raw"], 4),
            "confidence": 0.78 if payload["raw"] else 1.0,
            "evidence_ids": payload["evidence_ids"],
        }
        for god, payload in ten_scores.items()
    }
    return adjusted, ten_gods


def ten_god(day_master: dict[str, str], other: dict[str, str]) -> str:
    dm_element = day_master["element"]
    other_element = other["element"]
    same_polarity = day_master["yin_yang"] == other["yin_yang"]

    if other_element == dm_element:
        return "peer" if same_polarity else "rob_wealth"
    if GENERATES[dm_element] == other_element:
        return "eating_god" if same_polarity else "hurting_officer"
    if CONTROLS[dm_element] == other_element:
        return "indirect_wealth" if same_polarity else "direct_wealth"
    if CONTROLS[other_element] == dm_element:
        return "seven_killings" if same_polarity else "direct_officer"
    if GENERATES[other_element] == dm_element:
        return "indirect_resource" if same_polarity else "direct_resource"
    raise ValueError(f"Cannot derive ten god for {day_master} and {other}")


def _add_element_score(scores: dict[str, Any], element: str, weight: float, evidence_id: str) -> None:
    scores[element]["raw"] += weight
    scores[element]["evidence_ids"].append(evidence_id)


def _add_ten_god_score(scores: dict[str, Any], god: str, weight: float, evidence_id: str) -> None:
    scores[god]["raw"] += weight
    scores[god]["evidence_ids"].append(evidence_id)


def _season_multiplier(element: str, month_element: str) -> float:
    if element == month_element:
        return 1.25
    if GENERATES[element] == month_element:
        return 0.9
    if GENERATES[month_element] == element:
        return 1.1
    if CONTROLS[month_element] == element:
        return 0.85
    return 1.0


def _ten_god_evidence(position: str, stem_char: str, god: str, source_id: str, weight: float) -> dict[str, Any]:
    return _evidence(
        f"ten_god.{position}.{stem_char}.{god}",
        "ten_god_relation",
        f"ten_gods.{god}",
        f"{position} stem {stem_char} maps to {god} relative to day master",
        weight,
        1.0,
        "ten_god_engine",
        "ten_god_relation_v1",
        position,
        extra_source_id=source_id,
    )


def _build_luck_cycles(
    birth: BirthInput,
    pillar_gz: dict[str, Any],
    evidence: list[dict[str, Any]],
    count: int,
) -> list[dict[str, Any]]:
    direction = _luck_direction(birth.gender, pillar_gz["year"].tg)
    start_age, anchor_name = _luck_start_age(birth.birth_datetime, direction)
    month_idx = _sexagenary_index(pillar_gz["month"].tg, pillar_gz["month"].dz)
    cycles = []
    for index in range(1, count + 1):
        cycle_idx = (month_idx + direction * index) % 60
        start_age_i = round(start_age + (index - 1) * 10, 2)
        start_year = floor(birth.birth_datetime.year + start_age_i)
        ev_id = f"luck_cycle.{index}.calculation"
        evidence.append(
            _evidence(
                ev_id,
                "calculation",
                f"luck_cycles[{index - 1}]",
                f"luck cycle {index} derived from month pillar with {anchor_name} anchor",
                1.0,
                0.62,
                "luck_engine",
                "luck_cycle_mvp_v1",
                "luck_cycle",
            )
        )
        cycles.append(
            {
                "index": index,
                "start_age": start_age_i,
                "end_age": round(start_age_i + 10, 2),
                "start_year": start_year,
                "end_year": start_year + 9,
                "pillar": _pillar_from_indices(cycle_idx % 10, cycle_idx % 12),
                "evidence_ids": [ev_id],
            }
        )
    return cycles


def _luck_direction(gender: str, year_stem_index: int) -> int:
    year_is_yang = year_stem_index % 2 == 0
    if gender == "unknown":
        return 1
    return 1 if (gender == "male" and year_is_yang) or (gender == "female" and not year_is_yang) else -1


def _luck_start_age(dt: datetime, direction: int) -> tuple[float, str]:
    birth_jd = _to_jd(dt)
    infos = []
    for year in range(dt.year - 1, dt.year + 2):
        infos.extend(sxtwl.getJieQiByYear(year))
    jie_infos = sorted((info for info in infos if info.jqIndex in JIE_INDICES), key=lambda item: item.jd)
    if direction == 1:
        anchor = next(info for info in jie_infos if info.jd > birth_jd)
        days = anchor.jd - birth_jd
    else:
        anchor = next(info for info in reversed(jie_infos) if info.jd < birth_jd)
        days = birth_jd - anchor.jd
    return round(days / 3, 2), JIE_QI_NAMES.get(anchor.jqIndex, f"jie_qi_{anchor.jqIndex}")


def _to_jd(dt: datetime) -> float:
    time = sxtwl.Time()
    time.Y = dt.year
    time.M = dt.month
    time.D = dt.day
    time.h = dt.hour
    time.m = dt.minute
    time.s = dt.second + dt.microsecond / 1_000_000
    return sxtwl.toJD(time)


def _build_annual_flows(start_year: int, count: int, evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flows = []
    for offset in range(count):
        year = start_year + offset
        day = sxtwl.fromSolar(year, 7, 1)
        gz = day.getYearGZ()
        ev_id = f"annual_flow.{year}.calculation"
        evidence.append(
            _evidence(
                ev_id,
                "calculation",
                f"annual_flows.{year}",
                f"annual flow for {year} calculated from year pillar",
                1.0,
                1.0,
                "luck_engine",
                "sxtwl_year_ganzhi_v1",
                "annual_flow",
            )
        )
        flows.append({"year": year, "pillar": _pillar_from_indices(gz.tg, gz.dz), "evidence_ids": [ev_id]})
    return flows


def _sexagenary_index(stem_index: int, branch_index: int) -> int:
    for index in range(60):
        if index % 10 == stem_index and index % 12 == branch_index:
            return index
    raise ValueError(f"Invalid sexagenary pair: stem={stem_index}, branch={branch_index}")


def _pillar_from_indices(stem_index: int, branch_index: int) -> dict[str, Any]:
    branch_char = BRANCHES[branch_index]
    return {
        "stem": _stem(STEMS[stem_index]),
        "branch": {
            "char": branch_char,
            "element": BRANCH_ELEMENT[branch_char],
            "yin_yang": BRANCH_YIN_YANG[branch_char],
            "hidden_stems": [
                {"stem": _stem(stem_char), "qi_type": qi_type, "weight": weight}
                for stem_char, qi_type, weight in HIDDEN_STEMS[branch_char]
            ],
        },
    }


def _evidence(
    evidence_id: str,
    evidence_type: str,
    target: str,
    description: str,
    weight: float,
    confidence: float,
    layer: str,
    rule_id: str,
    position: str,
    extra_source_id: str | None = None,
) -> dict[str, Any]:
    item = {
        "id": evidence_id,
        "type": evidence_type,
        "target": target,
        "description": description,
        "weight": weight,
        "confidence": confidence,
        "source": {
            "layer": layer,
            "rule_id": rule_id,
            "position": position,
        },
    }
    if extra_source_id:
        item["description"] = f"{description}; source evidence {extra_source_id}"
    return item


def schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "schemas" / "bazi-core-output-v1.schema.json"
