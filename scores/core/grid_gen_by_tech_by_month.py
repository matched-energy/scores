import sys

import pandas as pd
import scores.plot.plot_grid_gen


def read(filename, start, end):
    d = pd.read_csv(filename)
    d["DATETIME"] = pd.to_datetime(d["DATETIME"])
    return d[(d["DATETIME"] > start) & (d["DATETIME"] < end)]


def group_by_month_and_tech(d):
    d["month"] = d["DATETIME"].dt.to_period("M")
    return (
        d[["month", "BIOMASS", "HYDRO", "OTHER", "WIND", "SOLAR"]]
        .groupby(["month"])
        .sum()
        / 2  # convert from MW to MWh
    ).reset_index()


def main(
    path_historic_generation_mix,
    start,
    end,
    path_grid_hh,
    path_grid_month_tech,
    plot=False,
):
    d = read(path_historic_generation_mix, start, end)
    d.to_csv(path_grid_hh, index=False)
    if plot:
        scores.plot.plot_grid_gen(d)
    d_agg_month_tech = group_by_month_and_tech(d)
    d_agg_month_tech.to_csv(path_grid_month_tech, index=False)


if __name__ == "__main__":
    main(
        path_historic_generation_mix=sys.argv[1],
        start=sys.argv[2],
        end=sys.argv[3],
        path_grid_hh=sys.argv[4],
        path_grid_month_tech=sys.argv[5],
    )
