import os

import pytest

import scores.s0142.supplier_hh_load_by_day


def test_process_file():
    expected = {
        "PURE": {"Period Information Imbalance Volume": 2628.072},
        "MERCURY": {"Period Information Imbalance Volume": 38125.445},
    }
    for bsc_party_id, load in scores.s0142.supplier_hh_load_by_day.process_file(
        input_path=os.path.join(
            os.environ["MATCHED_DATA"],
            "raw",
            "S0142",
            "S0142_20220401_SF_20220427115520.gz",
        ),
        bsc_party_ids=expected.keys(),
    ):
        result = load.sum()
        assert result["Settlement Period"] == 1176  # 1 + 2 + 3 + ... + 48
        for metric_key, metric_value in expected[bsc_party_id].items():
            assert result[metric_key] == pytest.approx(metric_value, 0.01)
