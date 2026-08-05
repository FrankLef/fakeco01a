import polars as pl
import polars.selectors as cs
import pandas as pd
from feature_engine.encoding import MeanEncoder

from src._registry.main import feathr


def encode_freq(data: pl.DataFrame) -> pl.DataFrame:
    cols: list[str | int] = list(data.select(cs.by_dtype(pl.Categorical)).columns)
    col_y = "sales_amt_lg"
    col_X = [col for col in data.columns if col != col_y]
    pd_df = data.to_pandas()
    y_df = pd_df[col_y]
    X_df = pd_df[col_X]
    me = MeanEncoder(variables=cols, missing_values="ignore", smoothing="auto")
    me.fit(X=X_df, y=y_df)
    enc_df = me.transform(X_df)
    all_df = pd.concat([enc_df, y_df], axis=1)
    # breakpoint()
    enc_data = pl.from_pandas(all_df)
    return enc_data


def main() -> None:
    src = "sales"
    dst = "sales_enct"
    data = feathr.load(src)
    enc_data = encode_freq(data)
    # print(enc_data.glimpse(max_items_per_column=3))
    # breakpoint()
    feathr.save(enc_data, name=dst)
