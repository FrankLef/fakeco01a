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

        TARGET_AMTs = (
            summ.select([NROWS, sum_var, SSE, SSB, SST])
            .sum()
            .with_columns(pl.lit(None).alias(group_var))
        )
        # move group var to first column
        TARGET_AMTs = TARGET_AMTs.select([group_var, pl.all().exclude(group_var)])
        summ = pl.concat([summ, TARGET_AMTs], how="vertical")
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

        TARGET_AMTs = (
            summ.select([NROWS, sum_var, SSE, SSR, SST])
            .sum()
            .with_columns(pl.lit(None).alias(group_var))
        )
        # move group var to first column
        TARGET_AMTs = TARGET_AMTs.select([group_var, pl.all().exclude(group_var)])
        summ = pl.concat([summ, TARGET_AMTs], how="vertical")
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
            enc_info = self.enc_info(
                df, cat_var=col, target_var=target_var, threshold=threshold
            )
            metrics.append(
                {
                    "variable": col,
                    "null_nb": a_col.null_count(),
                    "uniq_nb": a_col.n_unique(),
                    "ncats": enc_info["ncats"],
                    "ncats_pct": round(100 * enc_info["ncats"] / a_col.n_unique(), 1),
                    "nrows": enc_info["nrows"],
                    "nrows_pct": enc_info["nrows_pct"],
                    "target_mean": enc_info["target_mean"],
                    "target_pct": enc_info["target_pct"],
                }
            )
            main_cats[col] = enc_info["main_cats"]
        metrics_df = pl.DataFrame(metrics)
        self.main_cats = main_cats
        self.cats = metrics_df

    def enc_info(
        self, data: pl.DataFrame, cat_var: str, target_var: str, threshold: float
    ) -> dict[str, Any]:
        """Summary information used to help choose encoding.

        Very useful to help select CountFrequencyEncoder vs MeanEncoder.
        """
        NCATS: Final[str] = "ncats"
        NROWS: Final[str] = "nrows"
        NROWS_PCT: Final[str] = "nrows_pct"
        TARGET_AMT: Final[str] = "target_amt"
        TARGET_MEAN: Final[str] = "target_mean"
        TARGET_PCT: Final[str] = "target_pct"
        raw_data = data.select([cat_var, target_var]).drop_nulls()
        grouped_df = (
            raw_data.group_by(cat_var)
            .agg(
                pl.col(cat_var).len().alias(NROWS),
                pl.col(target_var).sum().alias(TARGET_AMT),
                pl.col(target_var).mean().alias(TARGET_MEAN),
            )
            .sort(TARGET_AMT, descending=True)
            .with_columns(
                [
                    # Calculate running NROWS percentiles
                    (pl.col(NROWS).cum_sum() / pl.col(NROWS).sum()).alias(NROWS_PCT),
                    # Calculate running TARGET_AMT percentiles
                    (pl.col(TARGET_AMT).cum_sum() / pl.col(TARGET_AMT).sum()).alias(
                        TARGET_PCT
                    ),
                ]
            )
            .filter(pl.col(TARGET_PCT).le(threshold))
        )

        nrows = grouped_df[NROWS].sum()
        nrows_pct = round(100 * nrows / raw_data.height, 1)
        target_sum = float(grouped_df[TARGET_AMT].sum())
        target_pct = round(
            100 * target_sum / float(raw_data[target_var].sum()),
            1,
        )
        target_mean = round(target_sum / float(grouped_df[NROWS].sum()), 2)
        main_cats = grouped_df.get_column(cat_var).to_list()

        out = {
            NCATS: grouped_df.height,
            NROWS: nrows,
            TARGET_MEAN: target_mean,
            NROWS_PCT: nrows_pct,
            TARGET_PCT: target_pct,
            "main_cats": main_cats,
        }
        return out
