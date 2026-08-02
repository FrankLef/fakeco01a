"""Remove features manually."""

from src._registry.ddb import get_conn


def main() -> None:
    table_nm: str = "sales"
    # NOTE: we choose to remove only duplicates in the current case
    cols = ("produit_fk_rnk", "cigo_qte_non_livree")
    with get_conn() as conn:
        for col in cols:
            qry = f"ALTER TABLE {table_nm} DROP COLUMN if EXISTS {col};"
            conn.sql(qry)
            print(f"Drop column {col} FROM {table_nm}.")
