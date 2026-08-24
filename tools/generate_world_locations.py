"""Generate the offline global birthplace directory from the IANA tz database."""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path


def find_tzdata_root() -> Path:
    candidates = []
    for entry in sys.path:
        if entry:
            candidates.append(Path(entry) / "tzdata" / "zoneinfo")

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        python_root = Path(local_app_data) / "Programs" / "Python"
        candidates.extend(python_root.glob("Python*/Lib/site-packages/tzdata/zoneinfo"))

    for candidate in candidates:
        if (candidate / "zone.tab").is_file() and (candidate / "iso3166.tab").is_file():
            return candidate
    raise FileNotFoundError("Could not find tzdata/zoneinfo with zone.tab and iso3166.tab")


def read_country_names(path: Path) -> dict[str, str]:
    countries = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line or raw_line.startswith("#"):
            continue
        code, name = raw_line.split("\t", 1)
        countries[code] = name
    return countries


def parse_coordinate(value: str, degree_digits: int) -> float:
    sign = -1 if value.startswith("-") else 1
    digits = value[1:]
    degrees = int(digits[:degree_digits])
    minutes = int(digits[degree_digits : degree_digits + 2])
    seconds = int(digits[degree_digits + 2 :]) if len(digits) > degree_digits + 2 else 0
    return round(sign * (degrees + minutes / 60 + seconds / 3600), 4)


def split_coordinates(value: str) -> tuple[float, float]:
    split_at = next(index for index in range(1, len(value)) if value[index] in "+-")
    return parse_coordinate(value[:split_at], 2), parse_coordinate(value[split_at:], 3)


def readable_name(value: str) -> str:
    return value.replace("_", " ").replace("-", " ")


def region_name(timezone: str) -> str:
    parts = timezone.split("/")
    return readable_name(parts[-2]) if len(parts) > 2 else "Major cities"


def city_name(timezone: str) -> str:
    return readable_name(timezone.rsplit("/", 1)[-1])


def build_directory(root: Path) -> dict[str, dict]:
    country_names = read_country_names(root / "iso3166.tab")
    grouped: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))

    for raw_line in (root / "zone.tab").read_text(encoding="utf-8").splitlines():
        if not raw_line or raw_line.startswith("#"):
            continue
        columns = raw_line.split("\t")
        country_code, coordinates, timezone = columns[:3]
        latitude, longitude = split_coordinates(coordinates)
        grouped[country_code][region_name(timezone)].append(
            {
                "label": city_name(timezone),
                "timezone": timezone,
                "longitude": longitude,
                "latitude": latitude,
            }
        )

    directory = {}
    for country_code in sorted(grouped, key=lambda code: country_names.get(code, code)):
        if country_code in {"CN", "US"}:
            continue
        regions = {}
        for region in sorted(grouped[country_code]):
            cities = {}
            for city in sorted(grouped[country_code][region], key=lambda item: item["label"]):
                key = city["label"]
                if key in cities:
                    key = f"{key} ({city['timezone']})"
                cities[key] = city
            regions[region] = {"label": region, "label_en": region, "cities": cities}
        country_name = country_names.get(country_code, country_code)
        directory[country_code] = {
            "label": country_name,
            "label_en": country_name,
            "regions": regions,
        }
    return directory


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "web" / "assets" / "world-locations-v1.json"
    directory = build_directory(find_tzdata_root())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(directory, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    city_count = sum(
        len(region["cities"])
        for country in directory.values()
        for region in country["regions"].values()
    )
    print(f"Wrote {len(directory)} countries and territories, {city_count} timezone cities")


if __name__ == "__main__":
    main()
