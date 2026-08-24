from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from .generator import build_core_output, schema_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and validate BaziCoreOutput v1 JSON.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Generate canonical BaziCoreOutput JSON.")
    generate.add_argument("--birth", required=True, help="ISO date-time, e.g. 1990-05-17T08:30:00+08:00")
    generate.add_argument("--timezone", required=True, help="IANA timezone, e.g. Asia/Shanghai")
    generate.add_argument("--gender", choices=["male", "female", "unknown"], default="unknown")
    generate.add_argument("--calendar", choices=["gregorian", "lunar"], default="gregorian")
    generate.add_argument("--country", default="")
    generate.add_argument("--region", default="")
    generate.add_argument("--city", default="")
    generate.add_argument("--longitude", type=float)
    generate.add_argument("--latitude", type=float)
    generate.add_argument("--true-solar-time", action="store_true")
    generate.add_argument("--birth-time-accuracy", choices=["exact", "approximate", "unknown"], default="exact")
    generate.add_argument("--annual-years", type=int, default=12)
    generate.add_argument("--annual-start-year", type=int)
    generate.add_argument("--luck-cycles", type=int, default=8)
    generate.add_argument("--output", help="Write JSON to this file instead of stdout.")

    validate = subparsers.add_parser("validate", help="Validate a BaziCoreOutput JSON file.")
    validate.add_argument("file")

    args = parser.parse_args()
    if args.command == "generate":
        payload = build_core_output(
            birth_datetime=args.birth,
            timezone=args.timezone,
            gender=args.gender,
            calendar=args.calendar,
            country=args.country,
            region=args.region,
            city=args.city,
            longitude=args.longitude,
            latitude=args.latitude,
            use_true_solar_time=args.true_solar_time,
            birth_time_accuracy=args.birth_time_accuracy,
            annual_years=args.annual_years,
            annual_start_year=args.annual_start_year,
            luck_cycles=args.luck_cycles,
        )
        _validate_payload(payload)
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
        return

    payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
    _validate_payload(payload)
    print(f"valid: {args.file}")


def _validate_payload(payload: dict) -> None:
    schema = json.loads(schema_path().read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(payload)


if __name__ == "__main__":
    main()
