"""Create ranked data for string."""

import duckdb as ddb

from config import settings
import pandas as pd
from pandas.api.types import CategoricalDtype


duckdb_path = settings.paths.duckdb


def get_data(conn: ddb.DuckDBPyConnection, table_nm: str) -> pd.DataFrame:
    qry = f"FROM {table_nm}"
    data = conn.sql(qry).df()
    if data.empty:
        raise AssertionError(f"Empty data for {table_nm}.")
    return data


def cast_cat_rank(data: pd.DataFrame, dtypes: list[str]) -> pd.DataFrame:
    cols = data.select_dtypes(include=dtypes).columns
    if not len(cols):
        raise ValueError(f"No columns of type {dtypes}.")
    for col in cols:
        cats = data[col].value_counts().index
        cats_dtype = CategoricalDtype(categories=cats, ordered=True)
        data[col] = data[col].astype(dtype=cats_dtype)
    return data


def main() -> None:
    table_nm: str = "sales"
    with ddb.connect(duckdb_path) as conn:
        data = get_data(conn, table_nm=table_nm)
        data = cast_cat_rank(data, dtypes=["str"])
        qry = f"CREATE OR REPLACE TABLE {table_nm} AS SELECT * FROM data;"
        conn.sql(qry)
