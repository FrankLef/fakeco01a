"""Validate MS Access connection."""

from config import settings

from rich import print as rprint
from src._registry.acc import main as inst_acc

duckdb_path = settings.paths.duckdb


def main() -> None:
    accdb = inst_acc(db_choice="db")
    conn = accdb[0]
    check = conn.test_connect()
    if check:
        msg: str = f"MS Access connect is ok.\n{accdb[1]}"
        rprint(msg)


if __name__ == "__main__":
    main()
