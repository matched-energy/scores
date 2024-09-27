import sys
from pathlib import Path

import pandas as pd
from scores.plot import plot_grid_gen


def read(filepath: Path, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    d = pd.read_csv(filepath)
    d["DATETIME"] = pd.to_datetime(d["DATETIME"])
    return d[(d["DATETIME"] > start) & (d["DATETIME"] < end)]


def group_by_month_and_tech(d: pd.DataFrame) -> pd.DataFrame:
    d["month"] = d["DATETIME"].dt.to_period("M")
    return (
        d[["month", "BIOMASS", "HYDRO", "OTHER", "WIND", "SOLAR"]]
        .groupby(["month"])
        .sum()
        / 2  # convert from MW to MWh
    ).reset_index()


def main(
    path_historic_generation_mix: Path,
    start: pd.Timestamp,
    end: pd.Timestamp,
    path_grid_hh: Path,
    path_grid_month_tech: Path,
    plot: bool = False,
):
    d = read(path_historic_generation_mix, start, end)
    d.to_csv(path_grid_hh, index=False)
    if plot:
        plot_grid_gen.plot(d)
    d_agg_month_tech = group_by_month_and_tech(d)
    d_agg_month_tech.to_csv(path_grid_month_tech, index=False)


if __name__ == "__main__":
    main(
        path_historic_generation_mix=Path(sys.argv[1]),
        start=pd.Timestamp(sys.argv[2]),
        end=pd.Timestamp(sys.argv[3]),
        path_grid_hh=Path(sys.argv[4]),
        path_grid_month_tech=Path(sys.argv[5]),
    )
