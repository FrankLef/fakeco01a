import polars as pl
import polars.selectors as cs
import pandas as pd
from feature_engine.encoding import MeanEncoder

from src._registry.main import feathr


def encode_data(data: pl.DataFrame, na: str = "_na") -> pl.DataFrame:
    col_y = "sales_amt_lg"
    cols_X = list(data.select(cs.by_dtype(pl.Categorical)).columns)
    cols = cols_X + [col_y]
    data = data.select(cols).fill_null(na)
    pd_df = data.to_pandas()
    y_df = pd_df[col_y]
    X_df = pd_df[cols_X]
    me = MeanEncoder(missing_values="ignore", smoothing="auto")
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
    enc_data = encode_data(data)
    append_df = data.select(
        ["date_livraison", "sales_price", "sales_qty", "sales_qty_lg"]
    )
    # breakpoint()
    enc_data = pl.concat([enc_data, append_df], how="horizontal")
    # print(enc_data.glimpse(max_items_per_column=3))
    # breakpoint()
    feathr.save(enc_data, name=dst)
