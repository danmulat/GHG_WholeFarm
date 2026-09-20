from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from wholefarm.registry import REQUIRED_COLUMNS, read_registry, validate_registry


REGISTRY = Path(__file__).parents[1] / "registry" / "model_registry.csv"


class RegistryTests(unittest.TestCase):
    def test_repository_registry_is_valid(self):
        headers, rows = read_registry(REGISTRY)
        self.assertEqual([], validate_registry(headers, rows))
        self.assertGreaterEqual(len(rows), 40)

    def test_duplicate_identifier_is_rejected(self):
        row = {column: "value" for column in REQUIRED_COLUMNS}
        row.update({
            "variable_id": "farm.area", "kind": "input", "requirement": "optional",
            "status": "provisional", "evidence_class": "survey",
        })
        issues = validate_registry(REQUIRED_COLUMNS, [row, row.copy()])
        self.assertTrue(any("duplicate" in issue.message for issue in issues))

    def test_verified_entry_requires_precise_source(self):
        row = {column: "value" for column in REQUIRED_COLUMNS}
        row.update({
            "variable_id": "soc.stock", "kind": "derived", "requirement": "optional",
            "status": "verified", "evidence_class": "calculated", "source_locator": "",
        })
        issues = validate_registry(REQUIRED_COLUMNS, [row])
        self.assertTrue(any(issue.field == "source_locator" for issue in issues))


if __name__ == "__main__":
    unittest.main()
