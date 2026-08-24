from rich.console import Console
from flml.screener.cols.feats import FeatsScreener

from src._registry.main import feathr


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    screenr = FeatsScreener(table_nm, data=data)
    screenr.title = f"Screen Features With ML: '{table_nm}'"
    console = Console()
    with console.status("Screen features with ML, 1 min ...", spinner="dots"):
        screenr.execute()
    screenr.print()
    print(f"{screenr.const_tol=}, {screenr.quasiconst_tol=}, {screenr.corr_tol=}")
    print(screenr)
    screenr.tabl.show()
