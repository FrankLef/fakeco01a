"""Convert to date dtype."""

import duckdb as ddb
from config import settings
import pandas as pd


duckdb_path = settings.paths.duckdb


def main() -> None:
    table_nm: str = "sales"
    with ddb.connect(duckdb_path) as conn:
        qry = f"FROM {table_nm}"
        data = conn.sql(qry).df()
        # print("before:\n", data.dtypes)
        for var in ["date_livraison"]:
            # use coerce to assign NaT (Not a Time)
            data[var] = pd.to_datetime(data[var], errors="coerce").dt.date
