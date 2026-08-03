"""Create ranked data for string."""

import polars as pl
import polars.selectors as cs

from src._registry.main import feathr
# from src._registry.ddb import get_conn, DdbConn


# def get_data(conn: DdbConn, table_nm: str) -> pl.DataFrame:
#     qry = f"FROM {table_nm}"
#     data = conn.sql(qry).pl()
#     if data.is_empty():
#         raise AssertionError(f"Empty data for {table_nm}.")
#     return data


def cast_cat_rank(
    data: pl.DataFrame, tol_uniq: float = 0.10, tol_na: float = 0.05, na: str = "_na"
) -> pl.DataFrame:
    cols = data.select(cs.string()).columns
    if not len(cols):
        raise ValueError("No columns of type string.")
    for col in cols:
        is_enum = check_enum(data, col=col, tol_uniq=tol_uniq, tol_na=tol_na)
        if is_enum:
            values = (
                data.select(pl.col(col).fill_null(na).value_counts(sort=True))
                .unnest()
                .get_column(col)
            )
            cats = pl.Enum(values)
            data = data.with_columns(pl.col(col).fill_null(na).cast(cats))
    return data


def check_enum(data: pl.DataFrame, col: str, tol_uniq: float, tol_na: float) -> bool:
    non_nulls_uniq = data[col].drop_nulls().n_unique()
    non_nulls_len = data[col].drop_nulls().len()
    nulls_len = data.height - non_nulls_len
    is_enum = (non_nulls_uniq < tol_uniq * non_nulls_len) and (
        nulls_len < tol_na * data.height
    )
    return is_enum


def cast_cat2int(data: pl.DataFrame, suffix="_int") -> pl.DataFrame:
    """Convert categories to integer."""
    cols = data.select(cs.by_dtype(pl.Enum)).columns
    for col in cols:
        new_col = col + suffix
        data = data.with_columns(pl.col(col).to_physical().alias(new_col))
    return data


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    feathr.save(data, name=table_nm)
    data = cast_cat_rank(data)
    data = cast_cat2int(data, suffix="_int")
    # with get_conn() as conn:
    #     data = get_data(conn, table_nm=table_nm)
    #     data = cast_cat_rank(data)
    #     data = cast_cat2int(data, suffix="_int")
    #     qry = f"CREATE OR REPLACE TABLE {table_nm} AS SELECT * FROM data;"
    #     conn.sql(qry)
