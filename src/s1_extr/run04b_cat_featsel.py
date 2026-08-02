"""Feature selection for category columns."""

from config import settings
import polars as pl
import polars.selectors as cs
from rich import print as rprint
from rich.pretty import pprint as rpprint

from src._registry.ddb import get_conn, DdbConn
from .select_feat import main as feat_sel

data_path = settings.paths.data


def get_data(conn: DdbConn, table_nm: str) -> pl.DataFrame:
    qry = f"SELECT * FROM {table_nm};"
    data = conn.sql(qry).pl()
    # breakpoint()
    # data = data.select(pl.enum)
    data = data.select(cs.by_dtype(pl.Enum))
    # data = data.select_dtypes(include=dtypes)
    if data.is_empty():
        raise AssertionError("Empty data for enum.")
    return data


def cast_cat2int(data: pl.DataFrame, suffix="_int") -> pl.DataFrame:
    """Convert categories to integer."""
    cols = data.select(cs.by_dtype(pl.Enum)).columns
    for col in cols:
        new_col = col + suffix
        data = data.with_columns(pl.col(col).to_physical().alias(new_col))
    return data


def main() -> None:
    table_nm: str = "sales"
    # dtypes = ["category"]
    with get_conn() as conn:
        data_rnk = get_data(conn, table_nm=table_nm)
    data_int = cast_cat2int(data_rnk)
    specs = {"const": 1, "quasi_const": 0.9, "dupl": 0, "corr": 0.9}
    path = data_path.joinpath("featsel_cat.json")
    results = feat_sel(data_int, specs=specs, path=path)
    rprint("Feature selections for categories:")
    rpprint(results)
