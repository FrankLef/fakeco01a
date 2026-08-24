from flml.screener.cols.nums import NumsScreener

from src._registry.main import feathr


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    screenr = NumsScreener(table_nm, data=data)
    screenr.title = f"Screen numerical columns: '{table_nm}'".title()
    screenr.execute()
    screenr.print()
    # print(f"{screenr.nzv_tol=}")
    print(screenr)
    screenr.tabl.show()
