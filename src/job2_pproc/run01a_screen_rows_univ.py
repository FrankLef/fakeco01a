import polars as pl

from flml.screener.rows.univ import UnivScreener

from src._registry.main import feathr


def add_outliers(
    data: pl.DataFrame, screenr: UnivScreener, new_col: str = "univ_outl"
) -> pl.DataFrame:
    cols = ("sales_qty_lg", "sales_amt_lg")
    outliers = screenr.get_outliers(cols)
    msg = f"Univariate outliers added in column '{new_col}'\n{new_col}: nb outl={sum(outliers)}, nb data={len(outliers)}, outl pct={sum(outliers) / len(outliers):.1%}"
    print(msg)
    # Convert to a Series FIRST, then attach it. Otherwise you end up with list(Boolean) in the schema
    data = data.with_columns(pl.Series(outliers, dtype=pl.Boolean).alias(new_col))
    return data


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    screenr = UnivScreener(table_nm, data=data, alpha=0.05, kgstd=2)
    screenr.execute()
    data = add_outliers(data, screenr=screenr)
    # breakpoint()
    screenr.tabl.show()
    feathr.save(screenr.summ, name="survey_amts")
    feathr.save(data, name=table_nm)


if __name__ == "__main__":
    main()
