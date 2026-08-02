import polars as pl
from config import settings
from pathlib import Path

data_path = settings.paths.data


def feather_path(name: str) -> Path:
    name = name.lower()
    nms = ("sales",)
    if name in nms:
        path = data_path.joinpath(f"{name}.feather")
    else:
        raise ValueError(f"'{name}' is an invalid feather file name.")
    return path


def save_feather(data: pl.DataFrame, name: str) -> Path:
    path = feather_path(name)
    data.write_ipc(path)
    return path


def load_feather(name: str) -> pl.DataFrame:
    path = feather_path(name)
    data = pl.read_ipc(path)
    return data
