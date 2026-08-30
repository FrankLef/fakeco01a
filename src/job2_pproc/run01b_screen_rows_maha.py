import polars as pl
from flml.screener.rows.maha import MahaScreener


from src._registry.main import feathr


def add_outliers(
    data: pl.DataFrame, screenr: MahaScreener, new_col: str = "maha_outl"
) -> pl.DataFrame:
    scores = screenr.scores
    cutoff = screenr.elbow_cutoff
    outliers = scores > cutoff
    msg = f"Maha (MCD) outliers added in column '{new_col}'\nnb outl={sum(outliers)}, nb data={len(outliers)}, outl pct={sum(outliers) / len(outliers):.1%}"
    print(msg)
    # Convert to a Series FIRST, then attach it. Otherwise you end up with list(Boolean) in the schema
    data = data.with_columns(pl.Series(outliers, dtype=pl.Boolean).alias(new_col))
    return data


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    # breakpoint()
    screenr = MahaScreener(
        table_nm, data=data, cols=("sales_qty_lg", "sales_amt_lg"), alpha=0.10
    )
    # breakpoint()
    screenr.execute()
    data = add_outliers(data, screenr=screenr)
    # breakpoint()
    tabl = screenr.tabl
    tabl.show()
    # breakpoint()
    fig = screenr.elbow_plot
    fig.show()
    # breakpoint()
    feathr.save(data, name=table_nm)


if __name__ == "__main__":
    main()
