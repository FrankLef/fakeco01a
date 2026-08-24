from flml.screener.cols.cats import CatsScreener

from src._registry.main import feathr


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    screenr = CatsScreener(table_nm, data=data, target_var="sales_amt")
    screenr.title = f"Screen Categories: '{table_nm}'".title()
    screenr.execute()
    screenr.print()
    print(f"{screenr.target_tol=}")
    print(screenr)
    screenr.tabl.show()
