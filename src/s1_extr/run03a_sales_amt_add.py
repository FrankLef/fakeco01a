"""Add sales_amt to sales table."""

import polars as pl
from src._registry.main import feathr


def main() -> None:
    col: str = "sales_amt"
    tbls = ("sales",)
    for tbl in tbls:
        data = feathr.load(tbl)
        data = data.with_columns(
            (pl.col("sales_qty") * pl.col("sales_price")).alias(col)
        )
        feathr.save(data, tbl)

    # with get_conn() as conn:
    #     qry = f"ALTER TABLE {table_nm} ADD COLUMN IF NOT EXISTS {col} FLOAT DEFAULT 0;"
    #     conn.sql(qry)
    #     qry = f"UPDATE {table_nm} SET {col} = sales_qty * sales_price;"
    #     conn.sql(qry)
