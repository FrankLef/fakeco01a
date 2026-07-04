"""Feature selection for number columns."""

import duckdb as ddb
from config import settings
import pandas as pd
from rich import print as rprint
from rich.pretty import pprint as rpprint

from .select_feat import main as feat_sel

duckdb_path = settings.paths.duckdb
data_path = settings.paths.data


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
    dtypes = ["number"]
    with ddb.connect(duckdb_path) as conn:
        data_num = get_data(conn, table_nm=table_nm, dtypes=dtypes)
    specs = {"const": 1, "quasi_const": 0.9, "dupl": 0, "corr": 0.9}
    path = data_path.joinpath("featsel_num.json")
    results = feat_sel(data_num, specs=specs, path=path)
    rprint(f"Feature selections for {dtypes}:")
    rpprint(results)
