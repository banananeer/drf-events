import logging

from rest_framework.viewsets import ModelViewSet

from drf_events.mixins import (
    CreateModelEventMixin,
    DestroyModelEventMixin,
    UpdateModelEventMixin,
)
from drf_events.event_handlers.log import SimpleLogEventHandler
from example_app.models import (
    SimpleModel,
    SimpleUuidPkModel,
    ModelWithForeignKeyField,
    ModelWithManyToManyField,
)
from example_app.serializers import (
    SimpleModelSerializer,
    SimpleUuidPkSerializer,
    ModelWithForeignKeyFieldSerializer,
    ModelWithManyToManyFieldSerializer,
)

logger = logging.getLogger(__name__)


class SimpleModelViewSet(
    ModelViewSet, CreateModelEventMixin, DestroyModelEventMixin, UpdateModelEventMixin
):
    queryset = SimpleModel.objects.all()
    serializer_class = SimpleModelSerializer

    event_handler_class = SimpleLogEventHandler
    emit_create_events = True
    emit_update_events = True
    emit_destroy_events = True


class SimpleModelUuidPkViewSet(
    ModelViewSet, CreateModelEventMixin, DestroyModelEventMixin, UpdateModelEventMixin
):
    queryset = SimpleUuidPkModel.objects.all()
    serializer_class = SimpleUuidPkSerializer

    event_handler_class = SimpleLogEventHandler
    emit_create_events = True
    emit_update_events = True
    emit_destroy_events = True


class ModelWithForeignKeyFieldViewSet(
    ModelViewSet, CreateModelEventMixin, DestroyModelEventMixin, UpdateModelEventMixin
):
    queryset = ModelWithForeignKeyField.objects.all()
    serializer_class = ModelWithForeignKeyFieldSerializer

    event_handler_class = SimpleLogEventHandler
    emit_create_events = True
    emit_update_events = True
    emit_destroy_events = True


class ModelWithManyToManyFieldViewSet(
    ModelViewSet, CreateModelEventMixin, DestroyModelEventMixin, UpdateModelEventMixin
):
    queryset = ModelWithManyToManyField.objects.all()
    serializer_class = ModelWithManyToManyFieldSerializer

    event_handler_class = SimpleLogEventHandler
    emit_create_events = True
    emit_update_events = True
    emit_destroy_events = True
