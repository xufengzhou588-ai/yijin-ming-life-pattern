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
        self.assertEqual(payload["model_versions"]["calculation_model"], "bazi-calculation-rules-v1")
        self.assertEqual(payload["model_versions"]["interpretation_model"], "bazi-structural-interpretation-v1")
        self.assertGreaterEqual(payload["confidence"], 0)
        self.assertLessEqual(payload["confidence"], 1)
        self.assertIn("uncertainty_reasons", payload)
        self.assertEqual(payload["chart"]["day_master"], payload["chart"]["day"]["stem"])
        self.assertGreater(len(payload["evidence"]), 0)

    def test_sample_files_validate(self):
        for sample in (path for path in Path("samples").glob("*.json") if not path.name.startswith("._")):
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
        self.assertEqual(traits["weight_version"], "trait-weights-v1")
        self.assertEqual(traits["interpretation_model_version"], "trait-structural-interpretation-v1")
        self.assertIn("trait_scores_are_uncalibrated_structural_indicators", traits["uncertainty_reasons"])

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

    def test_solar_term_exact_minute_boundary_changes_year_and_month(self):
        before = build_core_output(
            birth_datetime="2024-02-04T16:25:00+08:00",
            timezone="Asia/Shanghai",
            gender="male",
            country="CN",
            region="Shanghai",
            city="Shanghai",
        )
        after = build_core_output(
            birth_datetime="2024-02-04T16:27:00+08:00",
            timezone="Asia/Shanghai",
            gender="male",
            country="CN",
            region="Shanghai",
            city="Shanghai",
        )
        self.validator.validate(before)
        self.validator.validate(after)
        self.assertEqual(before["chart"]["year"]["stem"]["char"] + before["chart"]["year"]["branch"]["char"], "癸卯")
        self.assertEqual(before["chart"]["month"]["stem"]["char"] + before["chart"]["month"]["branch"]["char"], "乙丑")
        self.assertEqual(after["chart"]["year"]["stem"]["char"] + after["chart"]["year"]["branch"]["char"], "甲辰")
        self.assertEqual(after["chart"]["month"]["stem"]["char"] + after["chart"]["month"]["branch"]["char"], "丙寅")
        self.assertTrue(any(item["id"] == "solar_term.minute_boundary" for item in before["evidence"]))

    def test_zi_hour_policy_uses_midnight_day_boundary(self):
        late_zi = build_core_output(
            birth_datetime="2024-02-10T23:30:00+08:00",
            timezone="Asia/Shanghai",
            gender="male",
        )
        early_zi = build_core_output(
            birth_datetime="2024-02-11T00:30:00+08:00",
            timezone="Asia/Shanghai",
            gender="male",
        )
        self.assertEqual(late_zi["chart"]["hour"]["branch"]["char"], "子")
        self.assertEqual(early_zi["chart"]["hour"]["branch"]["char"], "子")
        self.assertNotEqual(late_zi["chart"]["day"], early_zi["chart"]["day"])

    def test_china_historical_timezone_offset_is_preserved_and_flagged(self):
        payload = build_core_output(
            birth_datetime="1900-01-01T08:30:00",
            timezone="Asia/Shanghai",
            gender="unknown",
            country="CN",
            region="Shanghai",
            city="Shanghai",
        )
        self.validator.validate(payload)
        self.assertTrue(payload["input"]["birth_datetime"].endswith("+08:05:43"))
        self.assertIn("historical_timezone_offset_has_subminute_component", payload["uncertainty_reasons"])

    def test_unknown_birth_time_lowers_confidence_and_marks_hour_placeholder(self):
        exact = build_core_output(
            birth_datetime="1990-05-17T08:30:00+08:00",
            timezone="Asia/Shanghai",
            gender="male",
            birth_time_accuracy="exact",
        )
        unknown = build_core_output(
            birth_datetime="1990-05-17T08:30:00+08:00",
            timezone="Asia/Shanghai",
            gender="male",
            birth_time_accuracy="unknown",
        )
        self.validator.validate(unknown)
        self.assertLess(unknown["confidence"], exact["confidence"])
        self.assertIn("birth_time_unknown_hour_pillar_placeholder", unknown["uncertainty_reasons"])
        time_evidence = next(item for item in unknown["evidence"] if item["id"] == "input.time_basis")
        self.assertLess(time_evidence["confidence"], 0.5)

    def test_leap_day_and_cross_year_are_reproducible(self):
        leap = build_core_output(
            birth_datetime="2024-02-29T23:30:00+08:00",
            timezone="Asia/Shanghai",
            gender="female",
        )
        cross_year = build_core_output(
            birth_datetime="2023-12-31T23:30:00+08:00",
            timezone="Asia/Shanghai",
            gender="female",
        )
        self.validator.validate(leap)
        self.validator.validate(cross_year)
        self.assertEqual(leap["chart"]["day"]["stem"]["char"] + leap["chart"]["day"]["branch"]["char"], "癸亥")
        self.assertEqual(cross_year["chart"]["year"]["stem"]["char"] + cross_year["chart"]["year"]["branch"]["char"], "癸卯")

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
