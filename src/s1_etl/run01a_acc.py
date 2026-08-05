"""Extract data from MS Access and set primary key."""

# from typing import Final
# from rich import print as rprint

from src._registry.main import feathr, inst_acc


def main() -> None:
    # PK: Final[str] = "_pk"
    table_nms = {"sales_raw": "sales"}
    conn_acc = inst_acc(db_choice="db")
    for raw_nm, new_nm in table_nms.items():
        qry = f"SELECT * FROM {raw_nm};"
        data = conn_acc.read(qry)
        # msg: str = f"Saving '{new_nm}' to 'feather' {data.shape}."
        # rprint(msg)
        feathr.save(data, name=new_nm)
        # with get_conn() as conn:
        #     msg: str = f"Uploading '{new_nm}' to 'duckdb'. {data.shape}."
        #     rprint(msg)
        #     qry = f"CREATE OR REPLACE TABLE {new_nm} AS SELECT * FROM data;"
        #     conn.sql(qry)
        #     qry = f"ALTER TABLE ADD PRIMARY KEY ({PK})"
