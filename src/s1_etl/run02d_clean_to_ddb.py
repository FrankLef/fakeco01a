"""Create sales stable in duckddb."""

from src._registry.main import feathr, get_conn


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    with get_conn() as conn:
        conn.register(view_name="data", python_object=data)
        qry: str = f"CREATE OR REPLACE TABLE {table_nm} AS SELECT * FROM data;"
        conn.sql(qry)
