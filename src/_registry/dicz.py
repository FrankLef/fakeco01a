import pandas as pd
from pathlib import Path
from config import settings
from joblib import Memory
from typing import Any
from datetime import datetime

from fltk.dicz.main import Dicz

data_path = settings.paths.data

sources_xl = settings.bag.sources
schema_xl = settings.bag.schema
output_xl = settings.bag.output


cache_path: Path = Path(data_path).joinpath(".dicz_cache")
mem = Memory(cache_path, verbose=0)

specs = {
    "sources": (sources_xl, "data"),
    "schema": (schema_xl, "data"),
    "output": (output_xl, "data"),
}


def get_mtimes(specs: dict[str, Any]) -> tuple[float, ...]:
    """Get a tuple of modification times for all files."""
    mtimes = []
    for val in specs.values():
        path = Path(data_path).joinpath(val[0])
        mtime = path.stat().st_mtime
        mtimes.append(mtime)
    return tuple(mtimes)


@mem.cache
def initialize_dicz(
    name: str, specs: dict[str, Any], mtimes: tuple[float, ...]
) -> Dicz:
    print(f"Dicz cache '{name}' updated {datetime.now().isoformat()}.")
    dicz = Dicz(name=name)
    for key, val in specs.items():
        path = Path(data_path).joinpath(val[0])
        sheet_nm = val[1]
        data = pd.read_excel(path, sheet_name=sheet_nm)
        dicz.append(key=key, data=data)
    return dicz


# NOTE: clear the cache to force its update
if False:
    initialize_dicz.clear()

mtimes = get_mtimes(specs)
dicz = initialize_dicz(name="fakeco01a", specs=specs, mtimes=mtimes)
