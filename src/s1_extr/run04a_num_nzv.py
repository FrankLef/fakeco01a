"""Fit NZV columns for number."""

import duckdb as ddb
from config import settings
import pandas as pd

from .calc_nzv_num import calc_nzv_num

duckdb_path = settings.paths.duckdb


def get_data(
    conn: ddb.DuckDBPyConnection, table_nm: str, dtypes=list[str]
) -> pd.DataFrame:
    qry = f"FROM {table_nm}"
    data = conn.sql(qry).df()
    data = data.select_dtypes(include=dtypes)
    if data.empty:
        raise AssertionError(f"Empty data for dtypes {dtypes}.")
    return data


def main() -> None:
    table_nm: str = "sales"
    stats_nm: str = "stats_" + table_nm + "_num"
    dtypes = ["number"]
    with ddb.connect(duckdb_path) as conn:
        data_num = get_data(conn, table_nm=table_nm, dtypes=dtypes)
        stats_df = calc_nzv_num(data_num)
        qry = f"CREATE OR REPLACE TABLE {stats_nm} AS SELECT * FROM stats_df;"
        conn.sql(qry)
    print("Variance Summary:\n", stats_df)
