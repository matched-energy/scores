import collections
import pprint
import sys

import pandas as pd
import plotly.graph_objects as go
import scores.plot_supplier_gen_load

pd.set_option("display.max_columns", 1000)

TECH = ["BIOMASS", "HYDRO", "OTHER", "WIND", "SOLAR"]


def calc_scores(hh_generation, hh_load):
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


def calculate_supplier_generation(
    path_supplier_month_tech, path_grid_month_tech, path_grid_hh_generation
):
    supplier_month_tech = pd.read_csv(path_supplier_month_tech)
    grid_month_tech = pd.read_csv(path_grid_month_tech)

    supplier_month_tech["Output Month"] = pd.to_datetime(
        supplier_month_tech["Output Month"]
    )
    grid_month_tech["month"] = pd.to_datetime(grid_month_tech["month"])

    supplier_month_tech.set_index("Output Month", inplace=True)
    grid_month_tech.set_index("month", inplace=True)
    supplier_month_tech_scale = supplier_month_tech / grid_month_tech

    hh_generation = pd.read_csv(path_grid_hh_generation)
    hh_generation["DATETIME"] = pd.to_datetime(hh_generation["DATETIME"])
    hh_generation["date"] = (
        hh_generation["DATETIME"].dt.to_period("M").dt.to_timestamp()
    )

    for tech in TECH:
        hh_generation[f"{tech}_scale"] = supplier_month_tech_scale.loc[
            hh_generation["date"], tech
        ].values
        hh_generation[f"{tech}_supplier"] = (  ## now in MWh!!
            hh_generation[f"{tech}_scale"] * hh_generation[tech] / 2
        )

    return hh_generation[["DATETIME"] + [f"{tech}_supplier" for tech in TECH]]


def get_supplier_load(path_supplier_hh_load):
    hh_load = pd.read_csv(path_supplier_hh_load)
    hh_load["Settlement Datetime"] = pd.to_datetime(hh_load["Settlement Datetime"])
    return hh_load


def main(
    path_supplier_month_tech,
    path_grid_month_tech,
    path_grid_hh_generation,
    path_supplier_hh_load,
):
    hh_generation = calculate_supplier_generation(
        path_supplier_month_tech, path_grid_month_tech, path_grid_hh_generation
    )
    hh_load = get_supplier_load(path_supplier_hh_load)

    scores.plot_supplier_gen_load.plot(hh_generation, hh_load)
    return calc_scores(hh_generation, hh_load)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
