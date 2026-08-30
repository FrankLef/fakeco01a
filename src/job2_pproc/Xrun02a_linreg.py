from typing import Any


# from sklearn.linear_model import LinearRegression
# from sklearn.metrics import mean_squared_error, r2_score
import statsmodels.formula.api as smf


from src._registry.main import feathr
from src._registry.specs import specs_mstr

_sales = specs_mstr.specs("schema").group("sales")


def get_specs() -> dict[str, Any]:
    the_specs = {
        "lrdbscan": {
            "group_var": "clus_dbscan",
            "qty_var": "sales_qty_lg",
            "target_var": "sales_amt_lg",
        },
        "lraggl": {
            "group_var": "clus_aggl",
            "qty_var": "sales_qty_lg",
            "target_var": "sales_amt_lg",
        },
    }
    return the_specs


# def get_arrays(data, X_vars: Sequence[str], y_var: Sequence[str]):
#     y_col = data.get_column(y_var).to_numpy()
#     X_mat = data.select(X_vars).to_numpy()
#     return {"X": X_mat, "y": y_col}


# def add_array_to_data(feathr_nm: str, arr: npt.NDArray, new_var: str) -> pl.DataFrame:
#     new_df = pl.from_numpy(arr, schema=[new_var])
#     data = feathr.load(feathr_nm)
#     data = data.drop(new_var, strict=False)
#     data = pl.concat([data, new_df], how="horizontal")
#     return data


# def lr_summ(model, predictions, y_col) -> dict[str, Any]:
#     summ = {
#         "Slopes": model.coef_,
#         "Intercept": model.intercept_,
#         "R2": r2_score(y_col, predictions),
#         "MSE": mean_squared_error(y_col, predictions),
#     }
#     return summ


def main() -> None:
    table_nm = "sales"
    data = feathr.load(table_nm)
    the_specs = get_specs()
    for nm, specs in the_specs.items():
        # cols = _sales.lines().filter_role(nm).line_nms
        data_linreg = data.select(
            [specs["group_var"], specs["qty_var"], specs["target_var"]]
        )
        # data_linreg = data_linreg.with_columns(
        #     pl.col(specs["cat_var"]).to_physical().alias(specs["cat_var"])
        # )
        data_linreg = data_linreg.to_pandas()
        # arrs = get_arrays(data_lr, X_vars=specs["X_vars"], y_var=specs["y_var"])
        forml = (
            "+".join([specs["group_var"], specs["qty_var"]]) + "~" + specs["target_var"]
        )
        # breakpoint()
        model = smf.ols(formula=forml, data=data_linreg).fit()
        print(model.summary())
        # predict_var = nm
        # model = LinearRegression()
        # model.fit(arrs["X"], arrs["y"])
        # predictions = model.predict(arrs["X"])

        # summ = lr_summ(model, predictions, arrs["y"])
        # rpprint(summ)

        # data = add_array_to_data(table_nm, arr=predictions, new_var=predict_var)

    feathr.save(data, name=table_nm)
