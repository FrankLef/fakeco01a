"""Drop selected categorical features."""

import json
from rich import print as rprint

from src._registry.main import feathr


def xprt_to_json(data: dict[str, list[str]], fn: str) -> None:
    path = feathr.path.joinpath(fn)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, default=list)


def main() -> None:
    drop_cols = {
        "sales": [
            "cigo_qte_livree",
            "cigo_qte_non_livree",
            "invoiced",
            "client_clean",
            "client_id",
            "produit_id",
            "produit_fk",
            "id",
        ],
        "sales_encc": [
            "cigo_qte_livree",
            "cigo_qte_non_livree",
            "invoiced",
            "client_clean",
            "client_id",
            "produit_id",
            "produit_fk",
            "id",
        ],
        "sales_enct": [
            "cigo_qte_livree",
            "cigo_qte_non_livree",
            "invoiced",
            "client_clean",
            "client_id",
            "produit_id",
            "produit_fk",
            "volume_unitaire_camion",
            "id",
        ],
    }
    xprt_to_json(drop_cols, fn="featdrop.json")
    tbls = ("sales", "sales_encc", "sales_enct")
    for tbl in tbls:
        data = feathr.load(tbl)
        ncols_before = data.width
        data = data.drop(drop_cols[tbl], strict=False)
        ncols_after = data.width
        ncols = ncols_before - ncols_after
        rprint(f"{ncols} features dropped from '{tbl}'")
        feathr.save(data, name=tbl)
