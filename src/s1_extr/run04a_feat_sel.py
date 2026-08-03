"""Feature selection for categorical columns."""

from rich import print as rprint
from rich.pretty import pprint as rpprint

from src._registry.main import feathr
from .select_feat import main as feat_sel


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    specs = {"const": 1, "quasi_const": 0.9, "dupl": 0, "corr": 0.9}
    json_path = feathr.path.joinpath("featsel_num.json")
    results = feat_sel(data, specs=specs, path=json_path)
    rprint(f"Feature selections for data {data.shape}:")
    rpprint(results)
