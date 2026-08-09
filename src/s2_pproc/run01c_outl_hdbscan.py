import pandas as pd
import polars as pl
from datetime import datetime as dt
from rich.console import Console
from rich import print as rprint
from sklearn.compose import ColumnTransformer

from sklearn.preprocessing import StandardScaler
from feature_engine.encoding import CountFrequencyEncoder

# from sklearn.preprocessing import StandardScaler, TargetEncoder
from sklearn.cluster import HDBSCAN
from sklearn.pipeline import Pipeline

from src._registry.main import feathr
from src._registry.specs import specs_mstr

_sales = specs_mstr.specs("schema").group("sales")

# 1. Define your feature groups
# categorical_features = ["store_id", "product_category", "payment_method"]
# numerical_features = ["amount", "quantity", "discount_percent"]


def get_features() -> dict[str, list[str]]:
    """Define the feature groups."""
    cats = list(_sales.lines().filter_role("cat").line_nms)
    nums = list(_sales.lines().filter_role("num").line_nms)
    out = {"cats": cats, "nums": nums}
    return out


def get_data_X(data: pl.DataFrame, cats: list[str], nums: list[str]) -> pd.DataFrame:
    """Get data as a pandas dataframe."""
    cols = cats + nums
    data = data.select(cols)
    data_X = data.to_pandas()
    return data_X


def get_preproc(cats: list[str], nums: list[str]):
    """Create a preprocessor to handle both data types simultaneously.

    Do not use target encoding with HDBSCAN. The distance is distorted categories have similar target mean.

    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), nums),
            (
                "cat",
                CountFrequencyEncoder(encoding_method="count", missing_values="ignore"),
                cats,
            ),
        ]
    )
    return preprocessor


def get_pipe(preproc):
    """Combine preprocessing and anomaly detection into one pipeline."""
    outlier_pipeline = Pipeline(
        [
            ("preprocessor", preproc),
            (
                "detector",
                HDBSCAN(min_cluster_size=5),
            ),
        ]
    )
    return outlier_pipeline


def get_data_pl(table_nm: str, data_X: pd.DataFrame) -> pl.DataFrame:
    """Create final polars dataframe."""
    data = feathr.load(table_nm)
    new_cols = {"is_outl": "hdbscan"}
    data = data.drop(list(new_cols.values()), strict=False)
    data = data.drop(list(new_cols.keys()), strict=False)
    data_pl = pl.from_pandas(data_X)
    data_sel = data_pl.select(list(new_cols.keys()))
    data = pl.concat([data, data_sel], how="horizontal")
    data = data.rename(new_cols)
    return data


def main(table_nm: str = "sales_outl", target_var: str = "sales_amt") -> None:
    data = feathr.load(table_nm)
    feats = get_features()
    data_X = get_data_X(data, cats=feats["cats"], nums=feats["nums"])
    # data_y = data[target_var].to_numpy()
    preproc = get_preproc(cats=feats["cats"], nums=feats["nums"])
    pipeline = get_pipe(preproc)
    rprint(f"Start time: {dt.now().strftime('%H:%M:%S')}")
    console = Console()
    with console.status("DBSCAN pipeline, 1 min ...", spinner="dots"):
        # No target 'y' needed with OneHotEncoder and HDBSCAN
        pipeline.fit(X=data_X)
    rprint(f"Finish time: {dt.now().strftime('%H:%M:%S')}")
    cluster_labels = pipeline.named_steps["detector"].labels_
    data_X["is_outl"] = cluster_labels

    # NOTE: outlier_scores_ not available when using HDBSCAM from sklearn
    # outlier_scores = pipeline.named_steps["detector"].outlier_scores_
    # data_pd["outl_score"] = outlier_scores
    data = get_data_pl(table_nm=table_nm, data_X=data_X)
    feathr.save(data, name=table_nm)
