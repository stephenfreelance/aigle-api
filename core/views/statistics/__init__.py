from django.urls import path
from . import validation_status_evolution

URL_PREFIX = "statistics/"

urls = [
    path(f"{URL_PREFIX}{view.URL}", view.endpoint, name=view.URL)
    for view in [validation_status_evolution]
]
