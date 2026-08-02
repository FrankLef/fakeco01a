"""Cast to date dtype and handle NA values."""

import pandas as pd

from src._registry.ddb import get_conn


def main() -> None:
    table_nm: str = "sales"
    with get_conn() as conn:
        qry = f"FROM {table_nm}"
        data = conn.sql(qry).df()
        # print("before:\n", data.dtypes)
        for var in ["date_livraison"]:
            # use coerce to assign NaT (Not a Time)
            data[var] = pd.to_datetime(data[var], errors="coerce").dt.date
        qry = f"CREATE OR REPLACE TABLE {table_nm} AS SELECT * FROM data;"
        conn.sql(qry)
