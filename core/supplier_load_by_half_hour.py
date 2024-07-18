import os
import sys

import pandas as pd
import plotly.graph_objects as go
import scores.plot.plot_supplier


def filter_and_group(df):
    return (
        df[df["BM Unit Id"].str.contains(f"^2__", regex=True)]
        .groupby(["Settlement Date", "Settlement Period"])
        .sum()
        .reset_index()
    )


def segregate_import_exports(df):
    updated_df = df.copy()
    updated_df["BM Unit Metered Volume: +ve"] = updated_df[
        "BM Unit Metered Volume"
    ].clip(lower=0)
    updated_df["BM Unit Metered Volume: -ve"] = updated_df[
        "BM Unit Metered Volume"
    ].clip(upper=0)
    return updated_df


def concat_and_sort(dfs):
    df = pd.concat(dfs)
    df["Settlement Date"] = pd.to_datetime(df["Settlement Date"], dayfirst=True)
    df = df.sort_values(["Settlement Date", "Settlement Period"])

    df["Settlement Datetime"] = df["Settlement Date"] + (
        df["Settlement Period"] - 1
    ) * pd.Timedelta(minutes=30)

    return df


def main(input_dir, output_path, bsc_lead_party_id, prefixes=None, plot=False):
    df = concat_and_sort(
        [
            filter_and_group(
                segregate_import_exports(pd.read_csv(os.path.join(input_dir, filename)))
            )
            for filename in os.listdir(input_dir)
            if filename.endswith(".csv")
            and bsc_lead_party_id in filename
            and (prefixes is None or any(filename.startswith(p) for p in prefixes))
        ]
    )
    df.to_csv(output_path, index=False)
    if plot:
        scores.plot.plot_supplier.plot_load(df)
    return df


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
