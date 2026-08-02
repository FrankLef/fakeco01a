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
    """Clean blank, empty string. Keep None, DO NOT replace None."""
    cols = data.select(cs.string()).columns
    if not len(cols):
        raise ValueError("No columns of type string.")
    data = data.with_columns(
        pl.col(cols).str.replace_all(r"\s+", " ").str.strip_chars()
    )
    data = data.with_columns(
        pl.when(pl.col(cols).str.contains(r"^\s*$"))
        .then(None)
        .otherwise(pl.col(cols))
        .name.keep()
    )
    return data


def main() -> None:
    table_nm: str = "sales"
    with get_conn() as conn:
        data = get_data(conn, table_nm=table_nm)
        data = clean_str(data)
        qry = f"CREATE OR REPLACE TABLE {table_nm} AS SELECT * FROM data;"
        conn.sql(qry)
