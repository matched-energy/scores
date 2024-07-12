import os
import sys

import pandas as pd
import plotly.graph_objects as go

import scores.plot.plot_supplier


def concat_and_sort(dfs):
    df = pd.concat(dfs)
    df["Settlement Date"] = pd.to_datetime(df["Settlement Date"], dayfirst=True)
    df = df.sort_values(["Settlement Date", "Settlement Period"])

    df["Settlement Datetime"] = df["Settlement Date"] + (
        df["Settlement Period"] - 1
    ) * pd.Timedelta(minutes=30)

    return df


def main(input_dir, output_path, bsc_lead_party_id=None, prefixes=None, plot=False):
    df = concat_and_sort(
        [
            pd.read_csv(os.path.join(input_dir, filename))
            for filename in os.listdir(input_dir)
            if filename.endswith(".csv")
            and (prefixes is None or any(filename.startswith(p) for p in prefixes))
            and (bsc_lead_party_id is None or bsc_lead_party_id in filename)
        ]
    )
    df.to_csv(output_path, index=False)
    if plot:
        scores.plot.plot_supplier.plot_load(df)
    return df


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
