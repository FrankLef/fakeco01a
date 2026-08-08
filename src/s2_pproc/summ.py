import polars as pl
from typing import Final, Any
# from collections.abc import Sequence


class Summ:
    def __init__(self, name: str) -> None:
        self.name = name
        self.ssb = pl.DataFrame()
        self.ssr = pl.DataFrame()

    def run_ssb(
        self,
        data: pl.DataFrame,
        group_var: str,
        amt_var: str,
    ) -> None:
        sum_var: str = amt_var + "_sum"
        NROWS: Final[str] = "nrows"
        GRAND_MEAN: Final[str] = "grand_mean"
        GROUP_MEAN: Final[str] = "group_mean"
        SSE: Final[str] = "SSE"
        SSB: Final[str] = "SSB"
        SST: Final[str] = "SST"
        summ = (
            data.with_columns(
                pl.col(amt_var).mean().alias(GRAND_MEAN),
                pl.col(amt_var).mean().over(group_var).alias(GROUP_MEAN),
            )
            .group_by(group_var)
            .agg(
                pl.len().alias(NROWS),
                pl.col(amt_var).sum().alias(sum_var),
                ((pl.col(amt_var) - pl.col(GROUP_MEAN)) ** 2).sum().alias(SSE),
                ((pl.col(GROUP_MEAN) - pl.col(GRAND_MEAN)) ** 2).sum().alias(SSB),
                ((pl.col(amt_var) - pl.col(GRAND_MEAN)) ** 2).sum().alias(SST),
            )
        )
        summ = summ.sort(group_var)

        totals = (
            summ.select([NROWS, sum_var, SSE, SSB, SST])
            .sum()
            .with_columns(pl.lit(None).alias(group_var))
        )
        # move group var to first column
        totals = totals.select([group_var, pl.all().exclude(group_var)])
        summ = pl.concat([summ, totals], how="vertical")
        self.ssb = summ

    def run_ssr(
        self,
        data: pl.DataFrame,
        group_var: str,
        amt_var: str,
        predict_var: str,
    ) -> None:
        sum_var: str = amt_var + "_sum"
        NROWS: Final[str] = "nrows"
        GRAND_MEAN: Final[str] = "grand_mean"
        SSE: Final[str] = "SSE"
        SSR: Final[str] = "SSR"
        SST: Final[str] = "SST"
        summ = (
            data.with_columns(
                pl.col(amt_var).mean().alias(GRAND_MEAN),
            )
            .group_by(group_var)
            .agg(
                pl.len().alias(NROWS),
                pl.col(amt_var).sum().alias(sum_var),
                ((pl.col(amt_var) - pl.col(predict_var)) ** 2).sum().alias(SSE),
                ((pl.col(predict_var) - pl.col(GRAND_MEAN)) ** 2).sum().alias(SSR),
                ((pl.col(amt_var) - pl.col(GRAND_MEAN)) ** 2).sum().alias(SST),
            )
        )
        summ = summ.sort(group_var)

        totals = (
            summ.select([NROWS, sum_var, SSE, SSR, SST])
            .sum()
            .with_columns(pl.lit(None).alias(group_var))
        )
        # move group var to first column
        totals = totals.select([group_var, pl.all().exclude(group_var)])
        summ = pl.concat([summ, totals], how="vertical")
        self.ssr = summ

    def run_cats(
        self,
        data: pl.DataFrame,
        cat_cols: list[str],
        target_var: str,
        threshold: float,
    ) -> None:
        cols = cat_cols + [target_var]
        df = data.select(cols)
        main_cats: dict[str, list[Any]] = {}
        metrics = []
        for col in cat_cols:
            a_col = df[col]
            cats_paret = self.cats_pareto(
                df, cat_var=col, target_var=target_var, threshold=threshold
            )
            metrics.append(
                {
                    "variable": col,
                    "null_nb": a_col.null_count(),
                    "uniq_nb": a_col.n_unique(),
                    "ncats": cats_paret["nuniq"],
                    "ncats_pct": round(100 * cats_paret["nuniq"] / a_col.n_unique(), 1),
                    "nrows_pct": cats_paret["nrows_pct"],
                    "total_pct": cats_paret["total_pct"],
                }
            )
            main_cats[col] = cats_paret["main_cats"]
        metrics_df = pl.DataFrame(metrics)
        self.main_cats = main_cats
        self.cats = metrics_df

    def cats_pareto(
        self, data: pl.DataFrame, cat_var: str, target_var: str, threshold: float
    ) -> dict[str, Any]:
        NROWS: Final[str] = "nrows"
        TOTAL: Final[str] = "total"
        CUM_PCT: Final[str] = "cum_pct"
        raw_data = data.select([cat_var, target_var]).drop_nulls()
        df = (
            # data.select([cat_var, target_var])
            raw_data.group_by(cat_var)
            .agg(
                pl.col(cat_var).len().alias(NROWS),
                pl.col(target_var).sum().alias(TOTAL),
            )
            .sort(TOTAL, descending=True)
            .with_columns(
                [
                    # Calculate running total percentiles
                    (pl.col(TOTAL).cum_sum() / pl.col(TOTAL).sum()).alias(CUM_PCT)
                ]
            )
            .filter(pl.col(CUM_PCT).le(threshold))
        )

        main_cats = df.get_column(cat_var).unique().to_list()

        nuniq = df.get_column(cat_var).n_unique()
        nrows_pct = round(100 * df[NROWS].sum() / raw_data.height, 1)
        total_pct = round(
            100 * float(df[TOTAL].sum()) / float(raw_data[target_var].sum()), 1
        )
        out = {
            "nuniq": nuniq,
            "nrows_pct": nrows_pct,
            "total_pct": total_pct,
            "main_cats": main_cats,
        }
        return out
