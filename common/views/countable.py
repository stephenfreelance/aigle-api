from rest_framework.response import Response
from rest_framework.decorators import action



class CountableModelViewSetMixin:
    @action(methods=["get"], detail=False)
    def count(self, request):
        return Response(self.get_queryset().count())
