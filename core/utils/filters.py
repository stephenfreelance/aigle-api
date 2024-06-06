from django_filters import BaseInFilter, UUIDFilter


class UuidInFilter(BaseInFilter, UUIDFilter):
    pass
