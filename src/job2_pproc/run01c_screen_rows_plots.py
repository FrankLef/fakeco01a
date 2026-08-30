import polars as pl
import polars.selectors as cs
import plotly.graph_objects as go

from src._registry.main import feathr
from job2_pproc.ply_outl_hist import PlyOutlHist
from job2_pproc.plt_subplot_hist import plt


def get_data(data: pl.DataFrame, without_outl: bool) -> pl.DataFrame:
    if not without_outl:
        data = data.filter(
            pl.col("maha_outl").eq(False) & pl.col("univ_outl").eq(False)
        )
    return data


def get_figure(
    data: pl.DataFrame,
    stats: pl.DataFrame,
    table_nm: str,
    nbins: int,
    without_outl: bool,
) -> go.Figure:
    ply = PlyOutlHist(
        table_nm, data=data, stats=stats, nbins=nbins, without_outl=without_outl
    )
    ply.title = f"Numerical Columns Histogram for '{table_nm}'"
    fig = ply.fig
    fig.update_layout(template=plt())
    return fig


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    stats = feathr.load("survey_amts")
    data_sel = get_data(data, without_outl=False)
    data_plot = data_sel.select(cs.numeric())
    for without_outl in (False, True):
        fig = get_figure(
            data_plot,
            stats=stats,
            table_nm=table_nm,
            nbins=30,
            without_outl=without_outl,
        )
        fig.show()


if __name__ == "__main__":
    main()
