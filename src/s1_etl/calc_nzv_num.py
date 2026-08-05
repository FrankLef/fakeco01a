import pandas as pd


def calc_nzv_num(data: pd.DataFrame, cv_tol: float = 0.01):
    agg_df = data.agg(["mean", "std", "median"]).transpose()
    # coefficient of variation
    agg_df["cv"] = agg_df["std"] / agg_df["mean"]
    mad_df = pd.DataFrame(
        {"mad": data.apply(lambda x: (x - x.median()).abs().median())}
    )
    summary = pd.concat([agg_df, mad_df], axis=1)
    # robust coefficient of variation
    summary["rcv"] = summary["mad"] / summary["median"]

    summary["nzv"] = (summary["cv"] <= cv_tol) | summary["cv"].isna()

    # Move median column after cv
    temp_col = summary.pop("median")
    insert_idx = summary.columns.get_loc("cv") + 1
    summary.insert(insert_idx, "median", temp_col)
    return summary
