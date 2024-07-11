import os
import sys

import pandas as pd
import plotly.graph_objects as go


def plot(df):
    fig = go.Figure(
        data=go.Scatter(
            x=df["Settlement Datetime"], y=df["Period Information Imbalance Volume"]
        )
    )
    fig.show()


def concat_and_sort(dfs):
    df = pd.concat(dfs)
    df["Settlement Date"] = pd.to_datetime(df["Settlement Date"], dayfirst=True)
    df = df.sort_values(["Settlement Date", "Settlement Period"])

    df["Settlement Datetime"] = df["Settlement Date"] + (
        df["Settlement Period"] - 1
    ) * pd.Timedelta(minutes=30)


def main(input_dir, output_path):
    df = concat_and_sort(
        [
            pd.read_csv(os.path.join(input_dir, filename))
            for filename in os.listdir(input_dir)
            if filename.endswith(".csv")
        ]
    )
    df.to_csv(output_path, index=False)
    plot(df)
    return df


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
