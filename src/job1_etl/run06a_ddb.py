from rich import print as rprint

from src._registry.main import feathr, get_conn


def main() -> None:
    for tbl in feathr.names:
        try:
            data = feathr.load(tbl, silent=True)
        except FileNotFoundError:
            return None
        rprint(f"Save '{tbl}' to duckdb")
        with get_conn() as conn:
            conn.register(view_name="data", python_object=data)
            qry: str = f"CREATE OR REPLACE TABLE {tbl} AS SELECT * FROM data;"
            conn.sql(qry)
