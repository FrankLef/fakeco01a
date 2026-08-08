import polars as pl
import numpy.typing as npt
from rich.console import Console
from rich.pretty import pprint as rpprint
from sklearn.cluster import AgglomerativeClustering


from src._registry.main import feathr
from src._registry.specs import specs_mstr

from .summ import Summ

_sales = specs_mstr.specs("schema").group("sales")


def get_data_clus(feathr_nm: str) -> pl.DataFrame:
    data_enc = feathr.load(feathr_nm)
    cols = _sales.lines().filter_rule("clus").line_nms
    data_clus = data_enc.select(cols)
    return data_clus


def add_array_to_data(feathr_nm: str, arr: npt.NDArray, new_var: str) -> pl.DataFrame:
    new_df = pl.from_numpy(arr, schema=[new_var])
    data = feathr.load(feathr_nm)
    data = data.drop(new_var, strict=False)
    data = pl.concat([data, new_df], how="horizontal")
    return data


def main(
    enc_data_nm: str = "sales_enct",
    data_nm: str = "sales",
    cluster_var="clus_aggl",
    target_nm: str = "sales_amt",
) -> None:
    data_clus = get_data_clus(enc_data_nm)

    console = Console()
    with console.status("Agglomerative clustering, 1 min ...", spinner="dots"):
        clustering = AgglomerativeClustering(n_clusters=5).fit(data_clus)
    data = add_array_to_data(data_nm, arr=clustering.labels_, new_var=cluster_var)

    summ = Summ(name=cluster_var)
    summ.run_ssb(data, group_var=cluster_var, amt_var=target_nm)
    # summ = summ_sse(data, group_var=cluster_var, amt_var=target_nm, type="regression")
    # breakpoint()
    rpprint(summ.ssb)
    feathr.save(data, name=data_nm)
