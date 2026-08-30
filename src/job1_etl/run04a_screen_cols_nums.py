"""Detect numerical columns to remove."""

from flml.screener.cols.nums import NumsScreener

from src._registry.main import feathr


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    screenr = NumsScreener(table_nm, data=data)
    screenr.title = f"Screen numerical columns: '{table_nm}'".title()
    screenr.execute()
    screenr.print()
    print(screenr)
    screenr.tabl.show()


if __name__ == "__main__":
    main()
