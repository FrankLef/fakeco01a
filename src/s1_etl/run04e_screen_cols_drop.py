"""Drop selected categorical features."""

from rich import print as rprint

from src._registry.main import feathr
from src._registry.specs import specs_mstr

_sales = specs_mstr.specs("schema").group("sales")


def main() -> None:
    drop_cols = _sales.lines().filter_rule("featdrop").line_nms
    tbls = ("sales",)
    for tbl in tbls:
        data = feathr.load(tbl)
        ncols_before = data.width
        data = data.drop(drop_cols, strict=False)
        ncols_after = data.width
        ncols = ncols_before - ncols_after
        rprint(f"{ncols} features dropped from '{tbl}'")
        feathr.save(data, name=tbl)
