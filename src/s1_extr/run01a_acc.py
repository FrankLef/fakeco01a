"""Extract data from MS Access and set primary key."""

from typing import Final
from rich import print as rprint

from src._registry.ddb import get_conn
from src._registry.acc import main as inst_acc


def main() -> None:
    PK: Final[str] = "_pk"
    table_nms = {"sales_raw": "sales"}
    accdb = inst_acc(db_choice="db")
    conn = accdb[0]
    for raw_nm, new_nm in table_nms.items():
        qry = f"SELECT * FROM {raw_nm};"
        raw_data = conn.read(qry)
        new_data = raw_data.reset_index(names=PK)
        with get_conn() as conn:
            msg: str = f"Uploading '{new_nm}' to 'duckdb'. {new_data.shape[0]} rows."
            rprint(msg)
            qry = f"CREATE OR REPLACE TABLE {new_nm} AS SELECT * FROM new_data;"
            conn.sql(qry)
            qry = f"ALTER TABLE ADD PRIMARY KEY ({PK})"
