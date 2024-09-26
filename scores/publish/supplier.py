import os
import shutil
import sys

import scores.common.utils as utils
import scores.configuration.conf as conf


def publish_scores(scores_input_path, scores_output_path, plot_target_path, supplier):
    supplier_scores = utils.from_yaml_file(scores_input_path)[
        supplier["scoring_methodology"]
    ]
    lines = [
        "---",
        "layout: supplier",
        f'title: {supplier["name"]}',
        f"bsc_party_id: {supplier['bsc_party_id']}",
        f"rego_organisation_name: {supplier['rego_organisation_name']}",
        f"l_hh_sum_GWh: {(supplier_scores['l_hh_sum'] / 1000):.0f}",
        f"g_hh_sum_GWh: {(supplier_scores['g_hh_sum'] / 1000):.0f}",
        f"g_l_ratio: {supplier_scores['g_l_ratio']:.2f}",
        f"g_embedded_ratio: {supplier_scores['g_embedded_ratio']:.2f}",
        f"r_hh_sum: {supplier_scores['r_hh_sum']:.2f}",
        f"r_yr: {supplier_scores['r_yr']:.2f}",
        f"s_hh: {supplier_scores['s_hh']:.2f}",
        f"s_yr: {supplier_scores['s_yr']:.2f}",
        f"chart_timeseries: {os.sep.join(plot_target_path.split(os.sep)[-2:])}",
        f"scoring_methodology: v0.1",
        f"confidence: {supplier['confidence']}",
        f"notes: {supplier.get('notes', '')}",
        "---",
    ]
    with open(scores_output_path, "w") as f:
        f.writelines(l + "\n" for l in lines)


def publish_plot(src_path, target_path):
    shutil.copy2(src_path, target_path)


def main(
    scores_input_path, scores_output_path, plot_src_path, plot_target_path, supplier
):
    publish_scores(scores_input_path, scores_output_path, plot_target_path, supplier)
    publish_plot(plot_src_path, plot_target_path)


if __name__ == "__main__":
    publish_plot(sys.argv[1], sys.argv[2])
