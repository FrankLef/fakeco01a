import polars as pl
import polars.selectors as cs

from src._registry.main import feathr
from .ply_outl_hist import PlyOutlHist


def get_data(data: pl.DataFrame) -> pl.DataFrame:
    data = data.select(cs.numeric())
    return data


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    stats = feathr.load("survey_amts")
    data_sel = get_data(data)
    ply_outl_freq = PlyOutlHist(
        table_nm, data=data_sel, stats=stats, nbins=20, without_outl=False
    )
    ply_outl_freq.title = f"Frequencies with outlier for '{table_nm}'"
    fig = ply_outl_freq.fig
    fig.show()
