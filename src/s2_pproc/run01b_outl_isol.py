import pandas as pd
import polars as pl
import numpy.typing as npt
from datetime import datetime as dt
from rich.console import Console
from rich import print as rprint
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from feature_engine.encoding import MeanEncoder

# from feature_engine.encoding import MeanEncoder
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline

from src._registry.main import feathr
from src._registry.specs import specs_mstr

_sales = specs_mstr.specs("schema").group("sales")


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


def get_preproc(cats: list[str], nums: list[str]) -> ColumnTransformer:
    """Create a preprocessor to handle both data types simultaneously."""
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), nums),
            (
                "cat",
                MeanEncoder(smoothing="auto", missing_values="ignore"),
                cats,
            ),
        ]
    )
    return preprocessor


def get_pipe(preproc: ColumnTransformer) -> Pipeline:
    """Combine preprocessing and anomaly detection into one pipeline."""
    outlier_pipeline = Pipeline(
        [
            ("preprocessor", preproc),
            (
                "detector",
                IsolationForest(contamination=0.10, random_state=42),
            ),
        ]
    )
    return outlier_pipeline


def run_pipe(
    pipeline: Pipeline,
    data_X: pd.DataFrame,
    data_y: npt.NDArray,
    outl_var: str,
    score_var: str | None,
) -> pd.DataFrame:
    rprint(f"Start time: {dt.now().strftime('%H:%M:%S')}")
    console = Console()
    msg: str = "Isolation forest pipeline, 1 min ..."
    with console.status(msg, spinner="dots"):
        pipeline.fit(X=data_X, y=data_y)
    rprint(f"Finish time: {dt.now().strftime('%H:%M:%S')}")

    # Get predictions (1 = Normal transaction, -1 = Outlier)
    data_X[outl_var] = pipeline.predict(data_X)

    # Get anomaly scores (Lower/more negative scores mean highly anomalous)
    data_X[score_var] = pipeline.decision_function(data_X.drop(columns=[outl_var]))
    return data_X


def get_data_pl(
    table_nm: str,
    data_X: pd.DataFrame,
    outl_var: str,
    score_var: str | None,
) -> pl.DataFrame:
    """Create final polars dataframe."""
    data = feathr.load(table_nm)
    data_pl = pl.from_pandas(data_X)
    if score_var:
        new_cols = [outl_var, score_var]
    else:
        new_cols = [outl_var]
    data_sel = data_pl.select(new_cols)
    data = pl.concat([data, data_sel], how="horizontal")
    return data


def main(
    table_nm: str = "sales_outl",
    target_var: str = "sales_amt",
    outl_var: str = "isol",
    score_var: str | None = "isol_score",
) -> None:
    data = feathr.load(table_nm)
    feats = get_features()
    data_X = get_data_X(data, cats=feats["cats"], nums=feats["nums"])
    data_y = data[target_var].to_numpy()
    preproc = get_preproc(cats=feats["cats"], nums=feats["nums"])
    pipeline = get_pipe(preproc)
    data_X = run_pipe(pipeline, data_X, data_y, outl_var=outl_var, score_var=score_var)
    data = get_data_pl(
        table_nm=table_nm,
        data_X=data_X,
        outl_var=outl_var,
        score_var=score_var,
    )
    feathr.save(data, name=table_nm)
