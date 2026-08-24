from flml.screener.maha import MahaScreener


from src._registry.main import feathr


def main(table_nm: str = "sales") -> None:
    # How to tune the contaminaiton score: Find the point on the graph where the curve suddenly spikes upward. The percentage of points after that spike is your ideal contamination rate.

    data = feathr.load(table_nm)
    screenr = MahaScreener(
        table_nm, data=data, cols=("sales_qty_lg", "sales_amt_lg"), alpha=0.10
    )
    screenr.execute()
    tabl = screenr.tabl
    tabl.show()
    fig = screenr.elbow_plot
    fig.show()
    data = screenr.data
    feathr.save(data, name=table_nm)
