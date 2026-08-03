import polars as pl
import polars.selectors as cs
from feature_engine.encoding import CountFrequencyEncoder

from src._registry.main import feathr


def encode_freq(data: pl.DataFrame) -> pl.DataFrame:
    # use specifi type hint to avoid error message
    cols: list[str | int] = list(data.select(cs.by_dtype(pl.Categorical)).columns)
    pd_df = data.to_pandas()
    cf = CountFrequencyEncoder(
        encoding_method="count", variables=cols, missing_values="ignore"
    )
    enc_df = cf.fit_transform(pd_df)
    enc_data = pl.from_pandas(enc_df)
    return enc_data


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    enc_data = encode_freq(data)
    # print(enc_data.glimpse(max_items_per_column=3))
    # breakpoint()
    feathr.save(enc_data, name=table_nm)
