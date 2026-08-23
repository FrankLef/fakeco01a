# from rich.console import Console
from flml.surveyor.amts import AmtsSurveyor

from src._registry.main import feathr


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    screenr = AmtsSurveyor(table_nm, data=data, alpha=0.05, kgstd=2)
    screenr.title = f"Initial survey: '{table_nm}'"
    # console = Console()
    # with console.status("Surveyor, 1 min ...", spinner="dots"):
    screenr.execute()
    screenr.print()
    # print(screenr)
    feathr.save(screenr.summ, name="survey_amts")
    screenr.tabl.show()
