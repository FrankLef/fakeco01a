import polars as pl
import polars.selectors as cs


from src._registry.ddb import get_conn, DdbConn


def get_data(conn: DdbConn, table_nm: str) -> pl.DataFrame:
    qry = f"FROM {table_nm}"
    data = conn.sql(qry).pl()
    if data.is_empty():
        raise AssertionError(f"Empty data for {table_nm}.")
    return data


def clean_str(data: pl.DataFrame) -> pl.DataFrame:
    cols = data.select(cs.string()).columns
    if not len(cols):
        raise ValueError("No columns of type string.")
    for col in cols:
        # keep only 1 space between word.
        data = data.with_columns(
            pl.col(col).str.replace_all(r"\s+", " ").str.strip_chars().alias(col)
        )
        # set to null the string with only blank spaces
        # data = data.with_columns(pl.col(col).str.replace_all(r"^\s*$", "").alias(col))
        # NOTE: Use this to make sure you get None, replace_all() gives empty string, not None
        data = data.with_columns(
            pl.when(pl.col(col).str.contains(r"^\s*$"))
            .then(None)
            .otherwise(pl.col(col))
            .alias(col)
        )

    return data


def main() -> None:
    table_nm: str = "sales"
    with get_conn() as conn:
        data = get_data(conn, table_nm=table_nm)
        data = clean_str(data)
        qry = f"CREATE OR REPLACE TABLE {table_nm} AS SELECT * FROM data;"
        conn.sql(qry)
