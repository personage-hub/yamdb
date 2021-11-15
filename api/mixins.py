from rest_framework import mixins, viewsets


class DestroyCreateListViewSet(
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pass
