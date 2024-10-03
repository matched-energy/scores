import os
import shutil
import sys

from pathlib import Path
from typing import Any

import scores.common.utils as utils
import scores.configuration.conf as conf


def publish_scores(
    scores_input_path: Path,
    scores_output_path: Path,
    plot_target_path: Path,
    supplier: dict[str, Any],
) -> None:
    supplier_scores = utils.from_yaml_file(scores_input_path)[
        supplier["scoring_methodology"]
    ]
    lines = [
        "---",
        f"permalink: /scores/{supplier['file_id']}/",
        "permalink_validation: false",
        f"fs_path: /scores/data/{supplier['file_id']}",
        f"chart_timeseries: {os.sep.join(plot_target_path.split(os.sep)[-1:])}",
        "layout: supplier",
        f'title: {supplier["name"]}',
        f"bsc_party_id: {supplier['bsc_party_id']}",
        f"rego_organisation_name: {supplier['rego_organisation_name']}",
        f"l_hh_sum_GWh: {(supplier_scores['l_hh_sum'] / 1000):.0f}",
        f"l_hh_sum_GWh_pretty: '{(supplier_scores['l_hh_sum'] / 1000):,.0f}'",
        f"g_hh_sum_GWh: {(supplier_scores['g_hh_sum'] / 1000):,.0f}",
        f"g_hh_sum_GWh_pretty: '{(supplier_scores['g_hh_sum'] / 1000):,.0f}'",
        f"g_l_ratio: {supplier_scores['g_l_ratio']:.2f}",
        f"g_embedded_ratio: {supplier_scores['g_embedded_ratio']:.2f}",
        f"r_hh_sum: {supplier_scores['r_hh_sum']:.2f}",
        f"r_yr: {supplier_scores['r_yr']:.2f}",
        f"s_hh: {supplier_scores['s_hh']:.2f}",
        f"s_hh_pretty: {100 * supplier_scores['s_hh']:.0f}%",
        f"s_yr: {supplier_scores['s_yr']:.2f}",
        f"s_yr_pretty: {100 * supplier_scores['s_yr']:.0f}%",
        f"scoring_methodology: v0.1",
        f"confidence: {supplier['confidence']}",
        f"notes: {supplier.get('notes', '')}",
        f"known_issues: {supplier.get('known_issues', '')}",
        "---",
    ]
    with open(scores_output_path, "w") as f:
        f.writelines(l + "\n" for l in lines)


def publish_plot(src_path: Path, target_path: Path) -> None:
    shutil.copy2(src_path, target_path)


def main(
    scores_input_path: Path,
    scores_output_path: Path,
    plot_src_path: Path,
    plot_target_path: Path,
    supplier: dict[str, Any],
) -> None:
    publish_scores(scores_input_path, scores_output_path, plot_target_path, supplier)
    publish_plot(plot_src_path, plot_target_path)


if __name__ == "__main__":
    publish_plot(Path(sys.argv[1]), Path(sys.argv[2]))