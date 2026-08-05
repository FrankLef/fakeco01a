import polars as pl
from rich.console import Console
from sklearn.cluster import AgglomerativeClustering


from src._registry.main import feathr


def get_clus_summ(data: pl.DataFrame, clus_col: str) -> pl.DataFrame:
    summ = (
        data.group_by(clus_col)
        .agg(
            pl.len().alias("nrows"),
            pl.col("sales_amt").sum().alias("sales_amt"),
        )
        .sort(clus_col)
    )
    summ = summ.with_columns(
        (pl.col("nrows") / pl.col("nrows").sum() * 100).round(2).alias("nrows_pct")
    )
    summ = summ.with_columns(
        (pl.col("sales_amt") / pl.col("sales_amt").sum() * 100)
        .round(2)
        .alias("sales_amt_pct")
    )
    return summ


def main() -> None:
    data = feathr.load("sales")
    data_enc = feathr.load("sales_enct")
    cols = [
        "client_nm",
        "category_fr",
        "latin_nm",
        "client_grp1",
        "sales_qty_lg",
        "sales_amt_lg",
    ]
    data_clus = data_enc.select(cols)
    clus_col = "clus_aggl"
    console = Console()
    with console.status("Agglomerative clustering, 1 min ...", spinner="dots"):
        clustering = AgglomerativeClustering(n_clusters=5).fit(data_clus)
    clus_df = pl.from_numpy(clustering.labels_, schema=[clus_col])
    # breakpoint()
    data = pl.concat([data, clus_df], how="horizontal")
    summ = get_clus_summ(data, clus_col=clus_col)
    # breakpoint()
    print(summ)
    # print(data)
