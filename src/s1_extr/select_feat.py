import pandas as pd
from typing import Any
from pathlib import Path
from feature_engine.selection import (
    DropConstantFeatures,
    DropDuplicateFeatures,
    DropCorrelatedFeatures,
)
import json


def get_dict(data: pd.DataFrame, specs: dict[str, float]) -> dict[str, Any]:
    results = {}
    for name, tol in specs.items():
        if name == "const":
            sel = DropConstantFeatures(tol=tol, missing_values="ignore")
            sel.fit(data)
            results[name] = sel.features_to_drop_
        elif name == "quasi_const":
            sel = DropConstantFeatures(tol=tol, missing_values="ignore")
            sel.fit(data)
            results[name] = sel.features_to_drop_
        elif name == "dupl":
            sel = DropDuplicateFeatures()
            sel.fit(data)
            results[name] = sel.duplicated_feature_sets_
        elif name == "corr":
            sel = DropCorrelatedFeatures(method="kendall", threshold=tol)
            sel.fit(data)
            results[name] = sel.correlated_feature_sets_
        else:
            msg: str = f"'{name}' is an invalid feature selection method."
            raise KeyError(msg)
    return results


def main(data: pd.DataFrame, specs: dict[str, float], path: Path | None):
    results = get_dict(data, specs=specs)
    if path:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(results, file, default=list)
    return results
