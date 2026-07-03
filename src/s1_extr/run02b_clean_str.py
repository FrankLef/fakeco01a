"""Convert to date dtype."""

import duckdb as ddb
from config import settings
import pandas as pd


duckdb_path = settings.paths.duckdb


def calc_freq_ratios(
    data: pd.DataFrame, freq_ratio_tol: float = 95 / 5, uniq_pct_tol: float = 0.05
) -> pd.DataFrame:
    summary_data = []
    for col in data.columns:
        # Get sorted frequencies of unique values (excluding NaNs by default)
        counts = data[col].value_counts()

        # Safely extract the highest frequency (default to 0 if column is completely empty)
        most_freq = counts.iloc[0] if len(counts) > 0 else 0

        # Safely extract the second highest frequency (default to 0 if there's no second unique value)
        second_freq = counts.iloc[1] if len(counts) > 1 else 0

        nuniq = data[col].nunique()

        nvalid = data[col].count()

        freq_ratio = most_freq / second_freq if second_freq > 0 else 0

        uniq_pct = nuniq / nvalid if nvalid > 0 else 0

        nzv = (freq_ratio >= freq_ratio_tol) & (uniq_pct <= uniq_pct_tol)

        summary_data.append(
            {
                "name": col,
                "most_freq": most_freq,
                "second_freq": second_freq,
                "nuniq": nuniq,
                "nvalid": nvalid,
                "freq_ratio": freq_ratio,
                "uniq_pct": uniq_pct,
                "nzv": nzv,
            }
        )

    freq_df = pd.DataFrame(summary_data)
    return freq_df


def main() -> None:
    # could use 97.5 / 2.5 to be very strict
    freq_ratio_tol: float = 95 / 5
    # use uniq_pct cutoff 0.05 because large data set, small sets can use 0.10
    uniq_pct_tol: float = 0.05
    table_nm: str = "sales"
    with ddb.connect(duckdb_path) as conn:
        qry = f"FROM {table_nm}"
        data = conn.sql(qry).df()
    data_str = data.select_dtypes(include="str")
    freq_df = calc_freq_ratios(
        data_str, freq_ratio_tol=freq_ratio_tol, uniq_pct_tol=uniq_pct_tol
    )
    print("Number of columns with near-zero variance:", sum(freq_df["nzv"]))
    print("Frequency Summary:\n", freq_df)
