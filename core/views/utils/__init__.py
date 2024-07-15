from django.urls import path
from . import get_tile_view
from . import get_import_infos

URL_PREFIX = "utils/"

urls = [
    path(f"{URL_PREFIX}{view.URL}", view.endpoint, name=view.URL)
    for view in [get_tile_view, get_import_infos]
]
