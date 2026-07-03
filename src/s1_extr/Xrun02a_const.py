"""Clean contant features and identify low-frequency rows."""

import duckdb as ddb
from config import settings
import pandas as pd
from sklearn.feature_selection import VarianceThreshold

duckdb_path = settings.paths.duckdb


def get_data(conn: ddb.DuckDBPyConnection, table_nm: str) -> pd.DataFrame:
    qry = f"FROM {table_nm}"
    data = conn.sql(qry).df()
    # data = data.select_dtypes(include="number")
    return data


def find_constant_feat(data: pd.DataFrame, sel: VarianceThreshold):
    # sel.fit(data)
    data_num = data.select_dtypes(include="number")
    agg_df = data_num.agg(["mean", "median", "std"]).transpose()
    print(agg_df)
    mad_df = pd.DataFrame(
        {"mad": data_num.apply(lambda x: (x - x.median()).abs().median())}
    )
    print(mad_df)
    data_desc = pd.concat([agg_df, mad_df], axis=1)
    data_desc["cv"] = data_desc["std"] / data_desc["mean"]
    # robust coefficient of variation
    data_desc["rcv"] = data_desc["mad"] / data_desc["median"]
    print(data_desc)
    # print("support:", sel.get_support())
    # out = pd.DataFrame({"feature": sel.feature_names_in_, "variance": sel.variances_})
    # print("out:", out)
    # print("support:", sel.variances_)
    # constant_data = data.loc[:, ~sel.get_support()]
    # constant_data.info()
    # reduced_data = pd.DataFrame(data, columns=sel.get_feature_names_out())
    return data


def main() -> None:
    sel = VarianceThreshold(threshold=0.001).set_output(transform="pandas")
    with ddb.connect(duckdb_path) as conn:
        data = get_data(conn, table_nm="sales_raw")
    find_constant_feat(data, sel)
