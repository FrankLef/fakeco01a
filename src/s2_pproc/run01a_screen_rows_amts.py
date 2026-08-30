import polars as pl

from flml.screener.rows.amts import AmtsScreener

from src._registry.main import feathr


def add_outliers(
    data: pl.DataFrame, screenr: AmtsScreener, new_col: str = "univ_outl"
) -> pl.DataFrame:
    cols = ("sales_qty_lg", "sales_amt_lg")
    outliers = screenr.get_outliers(cols)
    msg = f"{new_col}: nb outl={sum(outliers)}, nb data={len(outliers)}, outl pct={sum(outliers) / len(outliers):.1%}"
    print(msg)
    # Convert to a Series FIRST, then attach it. Otherwise you end up with list(Boolean) in the schema
    data = data.with_columns(pl.Series(outliers, dtype=pl.Boolean).alias(new_col))
    return data


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    screenr = AmtsScreener(table_nm, data=data, alpha=0.05, kgstd=2)
    screenr.execute()
    data = add_outliers(data, screenr=screenr)
    screenr.tabl.show()
    feathr.save(screenr.summ, name="survey_amts")
    feathr.save(data, name=table_nm)
