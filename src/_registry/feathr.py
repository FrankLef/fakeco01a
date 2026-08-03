from config import settings

from fltk.feathr.feathr import Feathr

data_path = settings.paths.data


feathr = Feathr(data_path, names=("sales",))
