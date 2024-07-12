import collections
import os
import pprint
import sys

import pandas as pd
import plotly.graph_objects as go
import scores.configuration.conf as conf
import scores.plot_supplier_gen_load


def calc_scores(hh_generation, hh_load):
    ## TODO - assert timeseries are aligned
    TECH = conf.read("generation.yaml", conf_dir=True)["TECH"]  # TODO
    hh_generation["TOTAL"] = hh_generation[[f"{tech}_supplier" for tech in TECH]].sum(
        axis=1
    )
    hh_load["deficit"] = (
        hh_load["Period Information Imbalance Volume"] - hh_generation["TOTAL"]
    ).clip(lower=0)
    scores = collections.OrderedDict(
        generation_total=hh_generation["TOTAL"].sum(),
        load_total=hh_load["Period Information Imbalance Volume"].sum(),
        unmatched_volume_hh=hh_load["deficit"].sum(),
        matched_volume_percent_hh=(
            1
            - hh_load["deficit"].sum()
            / hh_load["Period Information Imbalance Volume"].sum()
        )
        * 100,
        matched_volume_percent_annual=(
            hh_generation["TOTAL"].sum()
            / hh_load["Period Information Imbalance Volume"].sum()
        )
        * 100,
    )
    pprint.pprint(scores)
    return scores


def get_supplier_load(path_supplier_hh_load):
    hh_load = pd.read_csv(path_supplier_hh_load)
    hh_load["Settlement Datetime"] = pd.to_datetime(hh_load["Settlement Datetime"])
    return hh_load


def main(
    path_supplier_month_tech,
    path_grid_month_tech,
    path_grid_hh_generation,
    path_supplier_gen_by_tech_by_half_hour,
    path_supplier_hh_load,
):
    hh_generation = pd.read_csv(path_supplier_gen_by_tech_by_half_hour)
    hh_load = get_supplier_load(path_supplier_hh_load)

    scores.plot_supplier_gen_load.plot(hh_generation, hh_load)
    return calc_scores(hh_generation, hh_load)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
