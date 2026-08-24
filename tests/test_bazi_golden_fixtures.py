import json
import unittest
from collections import Counter
from pathlib import Path

from bazi_core.generator import build_core_output
from bazi_core.trait_engine import build_trait_output


FIXTURE_PATH = Path("tests/fixtures/bazi_golden_v1.json")
REQUIRED_CATEGORIES = {
    "solar_term_boundary",
    "zi_hour_day_boundary",
    "us_dst",
    "china_historical_timezone",
    "true_solar_cross_branch",
    "unknown_birth_time",
    "leap_and_cross_year",
}


class BaziGoldenFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture_set = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_fixture_set_shape_and_coverage(self):
        cases = self.fixture_set["cases"]
        self.assertEqual(self.fixture_set["fixture_set_version"], "bazi-golden-v1")
        self.assertEqual(self.fixture_set["case_count"], len(cases))
        self.assertGreaterEqual(len(cases), 100)
        self.assertLessEqual(len(cases), 300)
        self.assertTrue(REQUIRED_CATEGORIES.issubset(Counter(case["category"] for case in cases)))

    def test_golden_fixtures_are_reproducible(self):
        for case in self.fixture_set["cases"]:
            with self.subTest(case=case["id"]):
                core = build_core_output(**case["input"])
                traits = build_trait_output(core)
                expected = case["expected"]
                actual_pillars = {
                    position: core["chart"][position]["stem"]["char"] + core["chart"][position]["branch"]["char"]
                    for position in ("year", "month", "day", "hour")
                }
                self.assertEqual(core["schema_version"], expected["schema_version"])
                self.assertEqual(core["model_versions"], expected["model_versions"])
                self.assertEqual(traits["model_version"], expected["trait_model_version"])
                self.assertEqual(traits["weight_version"], expected["trait_weight_version"])
                self.assertEqual(core["input"]["birth_datetime"], expected["birth_datetime"])
                self.assertEqual(actual_pillars, expected["pillars"])
                self.assertEqual(core["chart"]["day_master"]["char"], expected["day_master"])
                self.assertEqual(core["confidence"], expected["confidence"])
                self.assertEqual(core["uncertainty_reasons"], expected["uncertainty_reasons"])
                self.assertEqual(traits["context"]["main_reminder"], expected["main_reminder"])


if __name__ == "__main__":
    unittest.main()
