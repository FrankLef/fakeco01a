"""Cast to date dtype and handle NA values."""

import polars as pl

from src._registry.main import feathr
# from src._registry.ddb import get_conn


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    for var in ["date_livraison"]:
        data = data.with_columns(pl.col(var).str.to_date())
    feathr.save(data, name=table_nm)
    # with get_conn() as conn:
    #     qry = f"FROM {table_nm}"
    #     data = conn.sql(qry).pl()
    #     # print("before:\n", data.dtypes)
    #     for var in ["date_livraison"]:
    #         # use coerce to assign NaT (Not a Time)
    #         # data[var] = pd.to_datetime(data[var], errors="coerce").dt.date
    #         data = data.with_columns(pl.col(var).str.to_date())
    #     qry = f"CREATE OR REPLACE TABLE {table_nm} AS SELECT * FROM data;"
    #     conn.sql(qry)


if __name__ == "__main__":
    main()
