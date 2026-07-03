"""Clean contant features and identify low-frequency rows."""

import duckdb as ddb
from config import settings
import pandas as pd

duckdb_path = settings.paths.duckdb


def get_data(conn: ddb.DuckDBPyConnection, table_nm: str) -> pd.DataFrame:
    qry = f"FROM {table_nm}"
    data = conn.sql(qry).df()
    data = data.select_dtypes(include="number")
    return data


def variance_stats(data: pd.DataFrame, cv_tol: float = 0.01):
    agg_df = data.agg(["mean", "median", "std"]).transpose()
    # coefficient of variation
    agg_df["cv"] = agg_df["std"] / agg_df["mean"]
    mad_df = pd.DataFrame(
        {"mad": data.apply(lambda x: (x - x.median()).abs().median())}
    )
    summary = pd.concat([agg_df, mad_df], axis=1)
    # robust coefficient of variation
    summary["rcv"] = summary["mad"] / summary["median"]

    summary["nzv"] = (summary["cv"] <= cv_tol) | summary["cv"].isna()

    # Move median column after cv
    temp_col = summary.pop("median")
    insert_idx = summary.columns.get_loc("cv") + 1
    summary.insert(insert_idx, "median", temp_col)
    return summary


def main() -> None:
    table_nm: str = "sales"
    with ddb.connect(duckdb_path) as conn:
        data_num = get_data(conn, table_nm=table_nm)
    stats_df = variance_stats(data_num)
    print("Variance Summary:\n", stats_df)
