"""Create categories columns."""

import polars as pl
import polars.selectors as cs

from src._registry.main import feathr


def cast_categories(
    data: pl.DataFrame, tol_uniq: float, tol_na: float, na: str = "_na"
) -> pl.DataFrame:
    cols = data.select(cs.string()).columns
    if not len(cols):
        raise ValueError("No columns of type string.")
    for col in cols:
        is_cat = check_cat(data, col=col, tol_uniq=tol_uniq, tol_na=tol_na)
        if is_cat:
            data = data.with_columns(pl.col(col).cast(pl.Categorical))
    return data


def check_cat(data: pl.DataFrame, col: str, tol_uniq: float, tol_na: float) -> bool:
    non_nulls_uniq = data[col].drop_nulls().n_unique()
    non_nulls_len = data[col].drop_nulls().len()
    nulls_len = data.height - non_nulls_len
    is_cat = (non_nulls_uniq < tol_uniq * non_nulls_len) and (
        nulls_len < tol_na * data.height
    )
    return is_cat


# def cast_cat2int(data: pl.DataFrame, suffix="_int") -> pl.DataFrame:
#     """Convert categories to integer."""
#     cols = data.select(cs.by_dtype(pl.Enum)).columns
#     for col in cols:
#         new_col = col + suffix
#         data = data.with_columns(pl.col(col).to_physical().alias(new_col))
#     return data


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    data = cast_categories(data, tol_uniq=0.10, tol_na=0.05)
    # print(data.glimpse(max_items_per_column=3))
    # breakpoint()
    feathr.save(data, name=table_nm)


if __name__ == "__main__":
    main()
