"""Create ranked data for string."""

import duckdb as ddb

from config import settings
import pandas as pd


duckdb_path = settings.paths.duckdb


def get_data(
    conn: ddb.DuckDBPyConnection, table_nm: str, dtypes: list[str]
) -> pd.DataFrame:
    qry = f"FROM {table_nm}"
    data = conn.sql(qry).df()
    data = data.select_dtypes(include=dtypes)
    if data.empty:
        raise AssertionError(f"Empty data for dtypes {dtypes}.")
    return data


def apply_rank(data: pd.DataFrame, suffix: str = "_rnk") -> pd.DataFrame:
    for col in data.columns:
        col_rank: str = col + suffix
        data[col_rank] = data[col].rank(method="dense").fillna(0).astype(int)
    return data


def main() -> None:
    table_nm: str = "sales"
    stats_nm: str = table_nm + "_str_rnk"
    dtypes = ["str"]
    with ddb.connect(duckdb_path) as conn:
        data_str = get_data(conn, table_nm=table_nm, dtypes=dtypes)
        data_ranked = apply_rank(data_str)
        qry = f"CREATE OR REPLACE TABLE {stats_nm} AS SELECT * FROM data_ranked;"
        conn.sql(qry)
    data_ranked.info()
