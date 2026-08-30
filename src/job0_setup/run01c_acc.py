"""Validate MS Access connection."""

from config import settings

from rich import print as rprint
from src._registry.main import inst_acc

duckdb_path = settings.paths.duckdb


def main() -> None:
    conn = inst_acc(db_choice="db")
    check = conn.test_connect()
    if check:
        msg: str = "✅" + " MS Access connect is ok."
        rprint(msg)


if __name__ == "__main__":
    main()
