import copy
import json
import unittest
from pathlib import Path

from src.account_intelligence import build_brief, validate

SAMPLE = Path(__file__).resolve().parents[1] / "examples" / "fictional_account.json"


class BriefTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(SAMPLE.read_text(encoding="utf-8"))

    def test_sample_has_scored_sources(self):
        brief = build_brief(self.data)
        self.assertIn("ICP fit: 100/100", brief)
        self.assertIn("[S1]", brief)
        self.assertIn("https://northstar.example/news/expansion", brief)
        self.assertIn("not fetched or verified", brief)

    def test_refuses_unsourced_brief(self):
        self.data["evidence"] = []
        with self.assertRaises(ValueError):
            build_brief(self.data)

    def test_refuses_non_https_source(self):
        self.data["evidence"][0]["url"] = "http://northstar.example"
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_no_unsupported_role_angle(self):
        data = copy.deepcopy(self.data)
        data["evidence"] = [data["evidence"][0]]
        brief = build_brief(data)
        self.assertNotIn("**Operations**", brief)
        self.assertNotIn("**Finance**", brief)

    def test_untrusted_text_is_escaped(self):
        self.data["company"] = "A <script> [test]"
        brief = build_brief(self.data)
        self.assertNotIn("<script>", brief)
        self.assertIn("\\<script\\>", brief)

    def test_incorrect_employee_count_is_rejected(self):
        self.data["employee_count"] = True
        with self.assertRaises(ValueError):
            validate(self.data)


if __name__ == "__main__":
    unittest.main()
