import polars as pl

# from rich.console import Console
from rich.pretty import pprint as rpprint
from collections.abc import Sequence
from typing import Any
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


from src._registry.main import feathr
from src._registry.specs import specs_mstr

_sales = specs_mstr.specs("schema").group("sales")


def get_arrays(data, X_vars: Sequence[str], y_var: Sequence[str]):
    y_col = data.get_column(y_var).to_numpy()
    X_mat = data.select(X_vars).to_numpy()
    return {"X": X_mat, "y": y_col}


def lr_summ(model, predictions, y_col) -> dict[str, Any]:
    summ = {
        "Slopes": model.coef_,
        "Intercept": model.intercept_,
        "R2": r2_score(y_col, predictions),
        "MSE": mean_squared_error(y_col, predictions),
    }
    return summ


def main() -> None:
    table_nm = "sales"
    data = feathr.load(table_nm)

    the_specs = {
        "lrdbscan": {
            "X_vars": ("clus_dbscan", "sales_qty_lg"),
            "y_var": "sales_amt_lg",
            "predict_var": "lrdbscan",
        },
        "lraggl": {
            "X_vars": ("clus_aggl", "sales_qty_lg"),
            "y_var": "sales_amt_lg",
            "predict_var": "lraggl",
        },
    }
    for nm, specs in the_specs.items():
        cols = _sales.lines().filter_role(nm).line_nms
        data_lr = data.select(cols)
        arrs = get_arrays(data_lr, X_vars=specs["X_vars"], y_var=specs["y_var"])
        predict_var = nm
        model = LinearRegression()
        model.fit(arrs["X"], arrs["y"])
        predictions = model.predict(arrs["X"])

        summ = lr_summ(model, predictions, arrs["y"])
        rpprint(summ)

        predict_df = pl.from_numpy(predictions, schema=[predict_var])
        data = data.drop(predict_var, strict=False)
        data = pl.concat([data, predict_df], how="horizontal")

    feathr.save(data, name=table_nm)
