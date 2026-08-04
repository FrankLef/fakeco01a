"""Drop selected categorical features."""

import json
from rich import print as rprint

from src._registry.main import feathr


def xprt_to_json(data, path):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, default=list)


def main() -> None:
    cols = (
        "cigo_qte_livree",
        "cigo_qte_non_livree",
        "invoiced",
        "client_clean",
        "client_id",
        "produit_id",
        "produit_fk",
        "id",
    )
    tbls = ("sales", "sales_encc", "sales_enct")
    for tbl in tbls:
        fn = f"featdrop_{tbl}.json"
        json_path = feathr.path.joinpath(fn)
        xprt_to_json(cols, path=json_path)
        data = feathr.load(tbl)
        ncols_before = data.width
        data = data.drop(cols, strict=False)
        ncols_after = data.width
        ncols = ncols_before - ncols_after
        rprint(f"{ncols} features dropped from '{tbl}'")
        feathr.save(data, name=tbl)
