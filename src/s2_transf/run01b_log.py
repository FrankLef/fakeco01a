import duckdb as ddb
import pandas as pd
from feature_engine.transformation import LogCpTransformer

from config import settings

duckdb_path = settings.paths.duckdb


def add_data(conn: ddb.DuckDBPyConnection, table_nm: str, cols: dict[str, str]) -> None:
    for old_col, new_col in cols.items():
        qry = f"ALTER TABLE {table_nm} ADD COLUMN IF NOT EXISTS {new_col} FLOAT DEFAULT 0;"
        conn.sql(qry)
        qry = f"UPDATE {table_nm} SET {new_col} = {old_col};"
        conn.sql(qry)
        qry = f"UPDATE {table_nm} SET {new_col} = 0 WHERE {old_col} IS NULL;"
        conn.sql(qry)


def get_data(conn: ddb.DuckDBPyConnection, table_nm: str) -> pd.DataFrame:
    qry = f"FROM {table_nm};"
    data = conn.sql(qry).df()
    return data


def main() -> None:
    suffix: str = "_lg"
    table_nm: str = "sales"
    cols: list[str] = ["sales_amt"]
    the_cols = {col: col + suffix for col in cols}
    with ddb.connect(duckdb_path) as conn:
        add_data(conn, table_nm=table_nm, cols=the_cols)
        data = get_data(conn, table_nm=table_nm)
        vars: list[str | int] = list(the_cols.values())
        lct = LogCpTransformer(variables=vars, base="10", C=1)
        lct.fit(data)
        data_lg = lct.transform(data)  # noqa: F841
        qry: str = f"CREATE OR REPLACE TABLE {table_nm} AS SELECT * FROM data_lg;"
        conn.sql(qry)
