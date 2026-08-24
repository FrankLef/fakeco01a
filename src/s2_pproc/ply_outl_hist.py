import polars as pl
import polars.selectors as cs
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from typing import Final


from flgr.ply.base import Ply


class PlyOutlHist(Ply):
    def __init__(
        self,
        name: str,
        data: pl.DataFrame,
        stats: pl.DataFrame,
        nbins: int,
        without_outl: bool,
    ) -> None:
        super().__init__(name=name)
        self.data = self.check_data(data)
        self.stats = stats
        self.nbins = nbins
        self.without_outl = without_outl

    @property
    def fig(self) -> go.Figure:
        fig = self.execute()
        return fig

    def check_data(self, data: pl.DataFrame) -> pl.DataFrame:
        all_cols = data.columns
        num_cols = data.select(cs.numeric()).columns
        check = len(all_cols) - len(num_cols)
        if check:
            msg: str = f"There are {check} non-numeric columns in the data."
            raise ValueError(msg)
        return data

    def execute(self) -> go.Figure:
        figs = self.create_histograms()
        fig = self.create_base(figs)
        return fig

    def create_histograms(self) -> go.Figure:
        data = self.data
        nbins = self.nbins
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

    def create_base(self, figs: dict[str, go.Figure]) -> go.Figure:
        COL: Final[int] = 1
        fig = make_subplots(
            rows=len(figs),
            cols=COL,
            subplot_titles=[key for key in figs.keys()],
        )
        for irow, (var, subfig) in enumerate(figs.items(), start=1):
            fig.add_trace(subfig, row=irow, col=COL)
            # for trace in subfig.data:
            #     fig.add_trace(trace, row=i, col=COL)
            if not self.without_outl:
                self.add_rect(fig, var=var, irow=irow, icol=COL)
        fig.update_layout(showlegend=False)
        fig.update_layout(template="simple_white")
        # fig.update_layout(plot_bgcolor="gainsboro", paper_bgcolor="gainsboro")
        return fig

    def add_rect(self, fig: go.Figure, var: str, irow: int, icol: int) -> go.Figure:
        LEFT_COLOR: Final[str] = "pink"
        RIGHT_COLOR: Final[str] = "hotpink"
        coords = self.get_coords(var=var)
        fig.add_vrect(
            x0=coords["min"],
            x1=coords["lwr_limit"],
            fillcolor=LEFT_COLOR,
            opacity=0.25,
            line_width=0,
            row=irow,
            col=icol,
        )

        fig.add_vrect(
            x0=coords["upr_limit"],
            x1=coords["max"],
            fillcolor=RIGHT_COLOR,
            opacity=0.25,
            line_width=0,
            row=irow,
            col=icol,
        )
        return fig

    def get_coords(self, var: str) -> dict[str, float]:
        stats = self.stats
        min_val = stats.filter(pl.col("variable").eq(var)).get_column("min").item()
        max_val = stats.filter(pl.col("variable").eq(var)).get_column("max").item()
        lwr_limit = (
            stats.filter(pl.col("variable").eq(var)).get_column("lwr_limit").item()
        )
        upr_limit = (
            stats.filter(pl.col("variable").eq(var)).get_column("upr_limit").item()
        )
        coords = {
            "min": min_val,
            "max": max_val,
            "lwr_limit": lwr_limit,
            "upr_limit": upr_limit,
        }
        return coords
