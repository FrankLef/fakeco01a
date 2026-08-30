"""Add log columns to sales table."""

import polars as pl

from fltk.utils import log1ps as lg

from src._registry.main import feathr


def main() -> None:
    suffix = "_lg"
    cols = ("sales_amt", "sales_qty")
    tbls: tuple[str, ...] = ("sales",)
    for tbl in tbls:
        data = feathr.load(tbl)
        for col in cols:
            col_lg = col + suffix
            data = data.with_columns(pl.col(col).map_batches(lg.log1ps10).alias(col_lg))
        feathr.save(data, tbl)


if __name__ == "__main__":
    main()
