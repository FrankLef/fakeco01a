from config import settings

from fltk.feathr.feathr import Feathr

data_path = settings.paths.data

nms = ("sales", "sales_ml", "sales_encc", "sales_enct")
feathr = Feathr(data_path, names=nms)
