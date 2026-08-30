"""Detect string/categorical columns to removed."""

from flml.screener.cols.strs import StrsScreener

from src._registry.main import feathr


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    screenr = StrsScreener(table_nm, data=data)
    screenr.title = f"Screen string/categorical columns: '{table_nm}'".title()
    screenr.execute()
    screenr.print()
    print(f"{screenr.freq_tol=}, {screenr.uniq_tol=}")
    print(screenr)
    screenr.tabl.show()


if __name__ == "__main__":
    main()
