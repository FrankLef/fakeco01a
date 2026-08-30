"""Validate Duckdb connection."""

from src._registry.main import get_conn


def main():
    with get_conn() as conn:
        result = conn.execute("SELECT 1").fetchone()
    if result == (1,):
        print("✅" + " DuckDB connection is ok.")
    else:
        raise AssertionError("Invalid return value for duckdb connection.")


if __name__ == "__main__":
    main()
