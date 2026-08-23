import polars as pl
import polars.selectors as cs
from plotly.subplots import make_subplots

# import plotly.express as px
import plotly.graph_objects as go
from typing import Final

from src._registry.main import feathr


def get_data(data: pl.DataFrame) -> pl.DataFrame:
    data = data.select(cs.numeric())
    return data


def create_histograms(data: pl.DataFrame, nbins: int = 20) -> go.Figure:
    figs = {}
    for col in data.columns:
        xdata = data.get_column(col).cast(pl.Float64)
        if len(xdata):
            mn = xdata.min()
            mx = xdata.max()
            size = (mx - mn) / nbins  # type: ignore
            xbins = dict(start=mn, end=mx, size=size)
        else:
            continue
        obj = go.Histogram(
            x=data.get_column(col),
            name=col,  # name used in legend and hover labels
            histnorm="probability",
            xbins=xbins,
            autobinx=False,
        )
        # fig = go.Figure(data=[obj])
        # fig = px.histogram(xdata, histnorm="probability")
        # fig.update_traces(xbins=xbins)

        figs[col] = obj
    return figs


def create_base(figs: dict[str, go.Figure], stats: pl.DataFrame) -> go.Figure:
    LEFT_COLOR: Final[str] = "pink"
    RIGHT_COLOR: Final[str] = "hotpink"
    fig = make_subplots(
        rows=len(figs),
        cols=1,
        subplot_titles=[key for key in figs.keys()],
    )
    COL: Final[int] = 1
    for ndx, (col, subfig) in enumerate(figs.items(), start=1):
        coords = get_coords(stats, col=col)
        fig.add_trace(subfig, row=ndx, col=COL)
        # for trace in subfig.data:
        #     fig.add_trace(trace, row=i, col=COL)
        fig.add_vrect(
            x0=coords["min"],
            x1=coords["lwr_limit"],
            fillcolor=LEFT_COLOR,
            opacity=0.25,
            line_width=0,
            row=ndx,
            col=COL,
        )

        fig.add_vrect(
            x0=coords["upr_limit"],
            x1=coords["max"],
            fillcolor=RIGHT_COLOR,
            opacity=0.25,
            line_width=0,
            row=ndx,
            col=COL,
        )
    fig.update_layout(showlegend=False)
    fig.update_layout(template="simple_white")
    # fig.update_layout(plot_bgcolor="gainsboro", paper_bgcolor="gainsboro")
    return fig


def get_coords(stats: pl.DataFrame, col: str) -> dict[str, float]:
    min_val = stats.filter(pl.col("variable").eq(col)).get_column("min").item()
    max_val = stats.filter(pl.col("variable").eq(col)).get_column("max").item()
    lwr_limit = stats.filter(pl.col("variable").eq(col)).get_column("lwr_limit").item()
    upr_limit = stats.filter(pl.col("variable").eq(col)).get_column("upr_limit").item()
    coords = {
        "min": min_val,
        "max": max_val,
        "lwr_limit": lwr_limit,
        "upr_limit": upr_limit,
    }
    return coords


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    stats = feathr.load("survey_amts")
    df = get_data(data)
    figs = create_histograms(df)
    fig = create_base(figs, stats=stats)
    fig.show()
