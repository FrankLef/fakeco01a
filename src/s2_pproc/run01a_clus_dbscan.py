import polars as pl
from rich.console import Console
from rich.pretty import pprint as rpprint
from sklearn.cluster import DBSCAN


from src._registry.main import feathr
from src._registry.specs import specs_mstr

from .clus_summ import clus_summ

_sales = specs_mstr.specs("schema").group("sales")


def main() -> None:
    data = feathr.load("sales")
    data_enc = feathr.load("sales_enct")
    cols = _sales.lines().filter_rule("clus").line_nms
    data_clus = data_enc.select(cols)
    cluster_var = "clus_dbscan"
    console = Console()
    with console.status("DBSCAN clustering, 1 min ...", spinner="dots"):
        clustering = DBSCAN(eps=0.15, min_samples=50).fit(data_clus)

    clus_df = pl.from_numpy(clustering.labels_, schema=[cluster_var])
    data = data.drop(cluster_var, strict=False)
    data = pl.concat([data, clus_df], how="horizontal")
    # summ = get_clus_summ(data, clus_col=clus_col)
    summ = clus_summ(data, clus_var=cluster_var, nrow_var="nrows", amt_var="sales_amt")
    rpprint(summ)
    feathr.save(data, name="sales")
    feathr.save(data_enc, name="sales_enct")
