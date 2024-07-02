from django_filters import (
    BaseInFilter,
    UUIDFilter,
    ChoiceFilter,
)


class UuidInFilter(BaseInFilter, UUIDFilter):
    pass


class ChoiceInFilter(BaseInFilter, ChoiceFilter):
    pass
