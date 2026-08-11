from flml.screener.nums import NumsScreener

from src._registry.main import feathr


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    screenr = NumsScreener(data)
    screenr.execute()
    screenr.print()
    print(f"{screenr.nzv_tol=}")
    print(screenr)
    # breakpoint()
