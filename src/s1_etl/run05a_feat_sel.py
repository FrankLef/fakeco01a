"""Feature selection for categorical columns."""

from rich import print as rprint
from rich.pretty import pprint as rpprint
from rich.console import Console

from src._registry.main import feathr
from .select_feat import main as feat_sel


def main() -> None:
    tbls = ("sales_encc", "sales_enct")
    for tbl in tbls:
        data = feathr.load(tbl)
        specs = {"const": 1, "quasi_const": 0.9, "dupl": 0, "corr": 0.9}
        fn = f"featsel_{tbl}.json"
        json_path = feathr.path.joinpath(fn)
        console = Console()
        with console.status("Features select, 1 min ...", spinner="dots"):
            results = feat_sel(data, specs=specs, path=json_path)
        rprint(f"Feature selections for {tbl}:")
        rpprint(results)
