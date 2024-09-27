import os
from pathlib import Path

import pytest

import scores.s0142.parse_s0142_files


def test_process_file():
    expected = {
        "PURE": {"Period Information Imbalance Volume": 2628.072},
        "MERCURY": {"Period Information Imbalance Volume": 38125.445},
    }
    for bsc_party_id, load in scores.s0142.parse_s0142_files.process_file(
        input_path=Path(os.environ["MATCHED_DATA"])
        / "raw/S0142/S0142_20220401_SF_20220427115520.gz",
        bsc_party_ids=list(expected.keys()),
    ):
        result = load.sum()
        assert result["Settlement Period"] == 1176  # 1 + 2 + 3 + ... + 48
        for metric_key, metric_value in expected[bsc_party_id].items():
            assert result[metric_key] == pytest.approx(metric_value, 0.01)


if __name__ == "__main__":
    test_process_file()
