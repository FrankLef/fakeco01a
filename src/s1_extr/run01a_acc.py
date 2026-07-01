"""Extract data from MS Access."""

import duckdb as ddb
from config import settings

from rich import print as rprint
from src._registry.acc import main as inst_acc

duckdb_path = settings.paths.duckdb


def main() -> None:
    table_nm: str = "sales_raw"
    accdb = inst_acc(db_choice="db")
    conn = accdb[0]
    # check = conn.test_connect()
    # if check:
    #     msg: str = f"MS Access connect is ok.\n{accdb[1]}"
    #     rprint(msg)
    qry = f"SELECT * FROM {table_nm};"
    data = conn.read(qry)
    # data.info()
    with ddb.connect(duckdb_path) as conn:
        msg: str = f"Uploading '{table_nm}' to 'duckdb'. {data.shape[0]} rows."
        rprint(msg)
        qry = f"CREATE OR REPLACE TABLE {table_nm} AS SELECT * FROM data;"
        conn.sql(qry)


if __name__ == "__main__":
    main()
