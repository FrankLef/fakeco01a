import polars as pl
from rich import print as rprint
from rich.pretty import pprint as rpprint
from typing import Any

from src._registry.main import feathr
from src._registry.specs import specs_mstr

from .summ import Summ

_sales = specs_mstr.specs("schema").group("sales")


def set_others(
    data: pl.DataFrame, main_cats: dict[str, Any], other_nm="Other"
) -> pl.DataFrame:
    for var, cats in main_cats.items():
        data = data.with_columns(
            pl.when(pl.col(var).is_in(cats))
            .then(pl.lit(other_nm))
            .otherwise(pl.col(var))
            .alias(var)
        )
    return data


def main(
    table_nm: str = "sales", target_var="sales_amt", dst: str = "sales_outl"
) -> None:
    data = feathr.load(table_nm)
    summ = Summ("outliers")
    target_cols = list(_sales.lines().filter_role("target").line_nms)
    num_cols = list(_sales.lines().filter_role("num").line_nms)
    cat_cols = list(_sales.lines().filter_role("cat").line_nms)
    ml_cols = cat_cols + num_cols + target_cols
    data_ml = data.select(ml_cols)
    threshold: float = 0.90
    summ.run_cats(
        data_ml, cat_cols=cat_cols, target_var=target_var, threshold=threshold
    )
    # Print all rows
    with pl.Config(tbl_rows=-1):
        msg: str = f"Summary with {threshold=} and {data_ml.shape=}"
        rprint(msg)
        rpprint(summ.cats)
    data_ml = set_others(data_ml, main_cats=summ.main_cats)
    feathr.save(data_ml, name=dst)
