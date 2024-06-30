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


def main(input_dir, output_path):
    dfs = []
    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            dfs.append(pd.read_csv(os.path.join(input_dir, filename)))
    df = pd.concat(dfs)
    df["Settlement Date"] = pd.to_datetime(df["Settlement Date"], dayfirst=True)
    df = df.sort_values(["Settlement Date", "Settlement Period"])

    # Add a column for the interval "Settlement Period * 00:30 from 23:30"
    df["Settlement Datetime"] = df["Settlement Date"] + (
        df["Settlement Period"] - 1
    ) * pd.Timedelta(minutes=30)

    df.to_csv(output_path, index=False)
    plot(df)
    return df

    # Continue with further processing or analysis


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
