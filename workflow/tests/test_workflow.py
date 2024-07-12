import os

import pytest
import scores.configuration.conf as conf
import scores.workflow.supplier_scores as workflow_supplier_scores


def test_long_workflow():
    expected = {
        "Good Energy": {
            "cumulative_generation": 819312.9981684365,
            "generation_total": 819312.9981684366,
            "load_total": 2628.0719999999997,
            "matched_volume_percent_annual": 31175.439568186743,
            "matched_volume_percent_hh": 78.09742703960463,
            "unmatched_volume_hh": 575.6153872517218,
        },
        "Octopus": {
            "cumulative_generation": 11546398.186882436,
            "generation_total": 11546398.186882434,
            "load_total": 38125.445,
            "matched_volume_percent_annual": 30285.28109477131,
            "matched_volume_percent_hh": 47.61379570039016,
            "unmatched_volume_hh": 19972.473507835384,
        },
    }
    results = workflow_supplier_scores.process_suppliers(
        os.path.join(conf.DIR, "run_long_test.yaml")
    )
    for supplier_name, metrics in expected.items():
        for metric_key, value in metrics.items():
            assert results[supplier_name][metric_key] == pytest.approx(value, 0.001)
