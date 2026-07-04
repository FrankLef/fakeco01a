"""Feature selection for category columns."""

import duckdb as ddb

from config import settings
import pandas as pd
from rich import print as rprint
from rich.pretty import pprint as rpprint

from .select_feat import main as feat_sel

duckdb_path = settings.paths.duckdb
data_path = settings.paths.data


def get_data(
    conn: ddb.DuckDBPyConnection, table_nm: str, dtypes: list[str]
) -> pd.DataFrame:
    qry = f"FROM {table_nm};"
    data = conn.sql(qry).df()
    data = data.select_dtypes(include=dtypes)
    if data.empty:
        raise AssertionError(f"Empty data for dtypes {dtypes}.")
    return data


def cast_cat2int(data: pd.DataFrame) -> pd.DataFrame:
    """Conver categories to integer."""
    df = data.copy()
    for col in df.select_dtypes(include=["category"]).columns:
        # cat.codes assign -1 to missing values
        df[col] = df[col].cat.codes
        # Must use Int64 for integer with missing values
        df[col] = df[col].replace(-1, pd.NA).astype("Int64")
    return df


def main() -> None:
    table_nm: str = "sales"
    dtypes = ["category"]
    with ddb.connect(duckdb_path) as conn:
        data_rnk = get_data(conn, table_nm=table_nm, dtypes=dtypes)
    data_int = cast_cat2int(data_rnk)
    specs = {"const": 1, "quasi_const": 0.9, "dupl": 0, "corr": 0.9}
    path = data_path.joinpath("featsel_cat.json")
    results = feat_sel(data_int, specs=specs, path=path)
    rprint("Feature selections for categories:")
    rpprint(results)
