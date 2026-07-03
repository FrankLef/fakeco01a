"""Convert to date dtype."""

import duckdb as ddb

# from typing import Iterable
from config import settings
import pandas as pd


duckdb_path = settings.paths.duckdb


def get_data(conn: ddb.DuckDBPyConnection, table_nm: str) -> pd.DataFrame:
    qry = f"FROM {table_nm}"
    data = conn.sql(qry).df()
    data = data.select_dtypes(include="str")
    return data


def apply_rank(data: pd.DataFrame, suffix: str = "_rnk") -> pd.DataFrame:
    for col in data.columns:
        col_rank: str = col + suffix
        data[col_rank] = data[col].rank(method="dense").fillna(0).astype(int)
    return data


def main() -> None:
    table_nm: str = "sales"
    with ddb.connect(duckdb_path) as conn:
        data_str = get_data(conn, table_nm=table_nm)
    data_ranked = apply_rank(data_str)
    data_ranked.info()
    # print(data_ranked)
