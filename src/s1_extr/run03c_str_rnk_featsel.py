"""Feature selection for ranked string columns."""

import duckdb as ddb

from config import settings
import pandas as pd
from rich import print as rprint
from rich.pretty import pprint as rpprint

from .feat_select import main as feat_sel

duckdb_path = settings.paths.duckdb


def get_data(conn: ddb.DuckDBPyConnection, table_nm: str, pat: str) -> pd.DataFrame:
    qry = f"FROM {table_nm};"
    data = conn.sql(qry).df()
    data_rk = data.filter(regex=pat)
    if data_rk.empty:
        raise AssertionError(f"Empty data for pat '{pat}'.")
    return data_rk


def main() -> None:
    table_nm: str = "sales"
    stats_nm: str = table_nm + "_str_rnk"
    with ddb.connect(duckdb_path) as conn:
        data_rnk = get_data(conn, table_nm=stats_nm, pat="_rnk$")
    specs = {"const": 1, "quasi_const": 0.9, "dupl": 0, "corr": 0.9}
    results = feat_sel(data_rnk, specs=specs)
    rprint("Feature selections for ranked strings:")
    rpprint(results)
