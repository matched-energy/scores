import unittest

import scores.workflow.supplier_scores as workflow_supplier_scores


class WorkflowSupplierScores(unittest.TestCase):
    def test_extract_regos(self):
        results = workflow_supplier_scores.main(suppliers=["Good Energy", "Octopus"])
        self.assertAlmostEqual(
            results["Good Energy"]["cumulative_generation"], 819312.998, places=2
        )
        self.assertAlmostEqual(
            results["Octopus"]["cumulative_generation"], 11546398.186, places=2
        )


if __name__ == "__main__":
    unittest.main()
