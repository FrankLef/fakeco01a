import polars as pl


def clus_summ(
    data: pl.DataFrame,
    clus_var: str,
    nrow_var: str,
    amt_var: str,
    pct_suffix: str = "_pct",
) -> pl.DataFrame:
    summ = (
        data.group_by(clus_var)
        .agg(
            pl.len().alias(nrow_var),
            pl.col(amt_var).sum().alias(amt_var),
        )
        .sort(clus_var)
    )
    summ = summ.with_columns(
        (pl.col(nrow_var) / pl.col(nrow_var).sum() * 100)
        .round(2)
        .alias(nrow_var + pct_suffix)
    )
    summ = summ.with_columns(
        (pl.col(amt_var) / pl.col(amt_var).sum() * 100)
        .round(2)
        .alias(amt_var + pct_suffix)
    )
    return summ
