from flml.screener.rows.maha import MahaScreener


from src._registry.main import feathr


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    # breakpoint()
    screenr = MahaScreener(
        table_nm, data=data, cols=("sales_qty_lg", "sales_amt_lg"), alpha=0.10
    )
    # breakpoint()
    screenr.execute()
    # breakpoint()
    tabl = screenr.tabl
    tabl.show()
    # breakpoint()
    fig = screenr.elbow_plot
    fig.show()
    # breakpoint()
    data = screenr.data
    feathr.save(data, name=table_nm)


if __name__ == "__main__":
    main()
