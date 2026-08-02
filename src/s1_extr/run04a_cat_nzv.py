"""Fit NZV columns for category."""

from config import settings
import polars as pl
import polars.selectors as cs

from src._registry.ddb import get_conn, DdbConn
from .calc_nzv_str import calc_nzv_str


duckdb_path = settings.paths.duckdb


def get_data(conn: DdbConn, table_nm: str) -> pl.DataFrame:
    qry = f"FROM {table_nm}"
    data = conn.sql(qry).pl()
    # data = data.select_dtypes(include=dtypes)
    # breakpoint()
    data = data.select(cs.enum())
    if data.is_empty():
        raise AssertionError("Empty data for dtypes enum.")
    return data


def main() -> None:
    table_nm: str = "sales"
    stats_nm: str = "stats_" + table_nm + "_str"
    # NOTE: could use 90 / 10 to be less strict
    freq_ratio_tol: float = 95 / 5
    # NOTE: use 0.05 because large data set, small sets can use 0.10
    uniq_pct_tol: float = 0.05
    with get_conn() as conn:
        data_str = get_data(conn, table_nm=table_nm)
        stats_df = calc_nzv_str(
            data_str, freq_ratio_tol=freq_ratio_tol, uniq_pct_tol=uniq_pct_tol
        )
        qry = f"CREATE OR REPLACE TABLE {stats_nm} AS SELECT * FROM stats_df;"
        conn.sql(qry)
    print("Number of columns with near-zero variance:", sum(stats_df["nzv"]))
    print("Frequency Summary:\n", stats_df)
