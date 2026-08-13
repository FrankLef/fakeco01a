# from rich.console import Console
from flml.surveyor.amts import AmtsSurveyor

from src._registry.main import feathr


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    screenr = AmtsSurveyor(table_nm, data=data)
    screenr.title = f"Initial survey: '{table_nm}'"
    # console = Console()
    # with console.status("Screen features with ML, 1 min ...", spinner="dots"):
    screenr.execute()
    screenr.print()
    print(screenr)
    screenr.tabl.show()
