import pandas as pd

def aggregate_10min_long(records: list[dict], value_column: str) -> pd.DataFrame:
    df = pd.DataFrame.from_records(records)
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "metric", "value"]).astype(
            {"timestamp": "datetime64[ns, UTC]", "metric": "string", "value": "float64"}
        )

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.set_index("timestamp").sort_index()
    agg = df[value_column].resample("10min").agg(["mean", "min", "max", "std"]).rename(columns={"std": "stddev"})
    agg = agg.stack().rename("value").reset_index()
    agg.columns = ["timestamp", "metric", "value"]
    return agg