import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from bazi_core.annual_engine import annual_schema_path, build_annual_outlook
from bazi_core.generator import build_core_output, schema_path
from bazi_core.monthly_compass import build_monthly_compass, monthly_compass_schema_path
from bazi_core.oracle_engine import interpret_cast, oracle_schema_path
from bazi_core.trait_engine import build_trait_output, trait_schema_path


class BaziCoreOutputTests(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads(schema_path().read_text(encoding="utf-8"))
        self.validator = Draft202012Validator(self.schema, format_checker=FormatChecker())
        self.trait_schema = json.loads(trait_schema_path().read_text(encoding="utf-8"))
        self.trait_validator = Draft202012Validator(self.trait_schema, format_checker=FormatChecker())
        self.annual_schema = json.loads(annual_schema_path().read_text(encoding="utf-8"))
        self.annual_validator = Draft202012Validator(self.annual_schema, format_checker=FormatChecker())
        self.monthly_schema = json.loads(monthly_compass_schema_path().read_text(encoding="utf-8"))
        self.monthly_validator = Draft202012Validator(self.monthly_schema, format_checker=FormatChecker())
        self.oracle_schema = json.loads(oracle_schema_path().read_text(encoding="utf-8"))
        self.oracle_validator = Draft202012Validator(self.oracle_schema, format_checker=FormatChecker())

    def test_generated_payload_validates(self):
        payload = build_core_output(
            birth_datetime="1990-05-17T08:30:00+08:00",
            timezone="Asia/Shanghai",
            gender="male",
            country="CN",
            region="Shanghai",
            city="Shanghai",
            longitude=121.4737,
            latitude=31.2304,
        )
        self.validator.validate(payload)
        self.assertEqual(payload["schema_version"], "1.0.0")
        self.assertEqual(payload["chart"]["day_master"], payload["chart"]["day"]["stem"])
        self.assertGreater(len(payload["evidence"]), 0)

    def test_sample_files_validate(self):
        for sample in Path("samples").glob("*.json"):
            with self.subTest(sample=sample):
                payload = json.loads(sample.read_text(encoding="utf-8"))
                self.validator.validate(payload)

    def test_trait_output_validates_and_references_core_evidence(self):
        core = build_core_output(
            birth_datetime="1990-05-17T08:30:00+08:00",
            timezone="Asia/Shanghai",
            gender="male",
            country="CN",
            region="Shanghai",
            city="Shanghai",
        )
        traits = build_trait_output(core)
        self.trait_validator.validate(traits)

        self.assertEqual(len(traits["traits"]), 10)
        core_evidence_ids = {item["id"] for item in core["evidence"]}
        for trait_key, trait in traits["traits"].items():
            with self.subTest(trait=trait_key):
                self.assertGreaterEqual(trait["score"], 0)
                self.assertLessEqual(trait["score"], 100)
                self.assertGreaterEqual(trait["confidence"], 0)
                self.assertLessEqual(trait["confidence"], 1)
                self.assertTrue(set(trait["evidence_ids"]).issubset(core_evidence_ids))

    def test_true_solar_time_requires_longitude(self):
        with self.assertRaisesRegex(ValueError, "longitude is required"):
            build_core_output(
                birth_datetime="1990-05-17T08:30:00+08:00",
                timezone="Asia/Shanghai",
                gender="male",
                use_true_solar_time=True,
            )

    def test_true_solar_time_changes_kashgar_hour_and_is_evidenced(self):
        common = {
            "birth_datetime": "1990-05-17T08:30:00+08:00",
            "timezone": "Asia/Shanghai",
            "gender": "male",
            "country": "CN",
            "region": "新疆维吾尔自治区",
            "city": "喀什市",
            "longitude": 75.9898,
            "latitude": 39.4704,
        }
        civil = build_core_output(**common)
        solar = build_core_output(**common, use_true_solar_time=True)
        self.validator.validate(solar)

        civil_hour = (
            civil["chart"]["hour"]["stem"]["char"],
            civil["chart"]["hour"]["branch"]["char"],
        )
        solar_hour = (
            solar["chart"]["hour"]["stem"]["char"],
            solar["chart"]["hour"]["branch"]["char"],
        )
        self.assertNotEqual(civil_hour, solar_hour)
        time_evidence = next(item for item in solar["evidence"] if item["id"] == "input.time_basis")
        self.assertLess(time_evidence["weight"], -150)
        self.assertEqual(
            time_evidence["source"]["rule_id"],
            "noaa_equation_of_time_longitude_v1",
        )

    def test_new_york_timezone_applies_seasonal_dst_offset(self):
        summer = build_core_output(
            birth_datetime="1990-05-17T08:30:00",
            timezone="America/New_York",
            gender="female",
            country="US",
            region="New York",
            city="New York City",
            longitude=-74.006,
            latitude=40.7128,
        )
        winter = build_core_output(
            birth_datetime="1990-01-17T08:30:00",
            timezone="America/New_York",
            gender="female",
            country="US",
            region="New York",
            city="New York City",
            longitude=-74.006,
            latitude=40.7128,
        )
        self.assertTrue(summer["input"]["birth_datetime"].endswith("-04:00"))
        self.assertTrue(winter["input"]["birth_datetime"].endswith("-05:00"))

    def test_trait_conflicts_are_separate_dimensions(self):
        core = build_core_output(
            birth_datetime="1988-08-08T14:20:00+08:00",
            timezone="Asia/Shanghai",
            gender="female",
            country="CN",
            region="Guangdong",
            city="Guangzhou",
        )
        traits = build_trait_output(core)["traits"]
        self.assertIn("wealth_generation", traits)
        self.assertIn("wealth_retention", traits)
        self.assertNotEqual(
            traits["wealth_generation"]["trait"],
            traits["wealth_retention"]["trait"],
        )

    def test_annual_outlook_validates_and_keeps_confidence_capped(self):
        core = build_core_output(
            birth_datetime="1990-05-17T08:30:00+08:00",
            timezone="Asia/Shanghai",
            gender="male",
            annual_start_year=2026,
            annual_years=5,
        )
        traits = build_trait_output(core)
        annual = build_annual_outlook(core, traits, years=5)
        self.annual_validator.validate(annual)

        self.assertEqual(len(annual["years"]), 5)
        for item in annual["years"]:
            self.assertLessEqual(item["confidence"], 0.72)
            self.assertTrue(item["evidence_ids"])
            for score in item["scores"].values():
                self.assertGreaterEqual(score, 0)
                self.assertLessEqual(score, 100)

    def test_monthly_compass_is_collectible_and_traceable(self):
        core = build_core_output(
            birth_datetime="1990-05-17T08:30:00+08:00",
            timezone="Asia/Shanghai",
            gender="male",
            annual_start_year=2026,
            annual_years=2,
        )
        traits = build_trait_output(core)
        compass = build_monthly_compass(
            core,
            traits,
            start_year=2026,
            start_month=6,
            count=6,
        )
        self.monthly_validator.validate(compass)

        self.assertEqual(len(compass["months"]), 6)
        self.assertEqual(len(compass["calculation_evidence"]), 6)
        collection_ids = {item["mark"]["collection_id"] for item in compass["months"]}
        self.assertEqual(len(collection_ids), 6)
        for item in compass["months"]:
            self.assertLessEqual(item["confidence"], 0.68)
            self.assertTrue(item["experiment_key"])
            self.assertTrue(item["evidence_ids"])

    def test_oracle_maps_three_coin_lines_to_qian_and_kun(self):
        qian = interpret_cast([7, 7, 7, 7, 7, 7], category="decision")
        self.oracle_validator.validate(qian)
        self.assertEqual(qian["primary"]["number"], 1)
        self.assertEqual(qian["relating"]["number"], 1)
        self.assertEqual(qian["moving_lines"], [])

        changing = interpret_cast([9, 9, 9, 9, 9, 9], category="decision")
        self.oracle_validator.validate(changing)
        self.assertEqual(changing["primary"]["number"], 1)
        self.assertEqual(changing["relating"]["number"], 2)
        self.assertEqual(changing["moving_lines"], [1, 2, 3, 4, 5, 6])

    def test_oracle_known_hexagram_three_mapping(self):
        result = interpret_cast([7, 8, 8, 8, 7, 8], category="general")
        self.oracle_validator.validate(result)
        self.assertEqual(result["primary"]["number"], 3)
        self.assertEqual(result["primary"]["name_zh"], "屯")

    def test_oracle_rejects_invalid_cast(self):
        with self.assertRaisesRegex(ValueError, "six values"):
            interpret_cast([7, 8, 9])


if __name__ == "__main__":
    unittest.main()
