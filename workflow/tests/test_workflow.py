import unittest

import scores.workflow.supplier_scores as workflow_supplier_scores


class WorkflowSupplierScores(unittest.TestCase):
    def test_workflow(self):
        expected = {
            "Good Energy": {
                "cumulative_generation": 819312.998,
                "load_total": 869533.709,
                "matched_volume_percent_annual": 94.224,
                "matched_volume_percent_hh": 83.306,
            },
            "Octopus": {
                "cumulative_generation": 11546398.186,
                "load_total": 12238244.329,
                "matched_volume_percent_annual": 94.347,
                "matched_volume_percent_hh": 66.235,
            },
        }

        results = workflow_supplier_scores.process_suppliers(
            suppliers=["Good Energy", "Octopus"]
        )
        for supplier_name, metrics in expected.items():
            for metric_key, value in metrics.items():
                self.assertAlmostEqual(
                    results[supplier_name][metric_key], value, places=2
                )


if __name__ == "__main__":
    unittest.main()
