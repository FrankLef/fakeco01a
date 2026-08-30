"""Clean the string columns."""

import polars as pl
import polars.selectors as cs

from src._registry.main import feathr


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


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    data = clean_str(data)
    feathr.save(data, name=table_nm)


if __name__ == "__main__":
    main()
