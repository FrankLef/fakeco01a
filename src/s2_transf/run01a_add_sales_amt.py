"""Add sales_amt to sales table."""

from src._registry.ddb import get_conn


def main() -> None:
    table_nm: str = "sales"
    col: str = "sales_amt"
    with get_conn() as conn:
        qry = f"ALTER TABLE {table_nm} ADD COLUMN IF NOT EXISTS {col} FLOAT DEFAULT 0;"
        conn.sql(qry)
        qry = f"UPDATE {table_nm} SET {col} = sales_qty * sales_price;"
        conn.sql(qry)
