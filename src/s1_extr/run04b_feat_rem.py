"""Remove selected categorical features."""

from rich import print as rprint

from src._registry.main import feathr


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    ncols_before = data.width
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
    data = data.drop(cols, strict=False)
    ncols_after = data.width
    ncols = ncols_before - ncols_after
    rprint(f"{ncols} features removed from '{table_nm}'")
    feathr.save(data, name=table_nm)
