from config import settings

from fltk.utils.feathr import Feathr

data_path = settings.paths.data


feathr = Feathr(data_path, names=("sales",))
