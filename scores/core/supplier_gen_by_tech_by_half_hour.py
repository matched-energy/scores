from pathlib import Path
from typing import Optional

import pandas as pd

import scores.configuration.conf as conf


def calculate_supplier_generation(
    path_supplier_month_tech: Path,
    path_grid_month_tech: Path,
    path_grid_hh_generation: Path,
    output_path: Optional[Path] = None,
) -> pd.DataFrame:
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

    tech_categories = conf.read("generation.yaml", conf_dir=True)["TECH"]

    for tech in tech_categories:
        hh_generation[f"{tech}_scale"] = supplier_month_tech_scale.loc[
            hh_generation["date"], tech
        ].values
        hh_generation[f"{tech}_supplier"] = (  ## now in MWh!!
            hh_generation[f"{tech}_scale"] * hh_generation[tech] / 2
        )

    df = hh_generation[["DATETIME"] + [f"{tech}_supplier" for tech in tech_categories]]
    if output_path:
        df.to_csv(output_path, index=False)
    return df
