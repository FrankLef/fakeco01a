import duckdb as ddb

from config import settings

duckdb_path = settings.paths.duckdb


def main() -> None:
    table_nm: str = "sales"
    col: str = "sales_amt"
    with ddb.connect(duckdb_path) as conn:
        qry = f"ALTER TABLE {table_nm} ADD COLUMN IF NOT EXISTS {col} FLOAT DEFAULT 0;"
        conn.sql(qry)
        qry = f"UPDATE {table_nm} SET {col} = sales_qty * sales_price;"
        conn.sql(qry)
