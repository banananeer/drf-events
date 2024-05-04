import logging
from typing import Any

from django.db.models import Model
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from drf_events import BaseEventHandler


logger = logging.getLogger(__name__)


class SimpleLogEventHandler(BaseEventHandler):  # noqa
    def emit_event(self, event):
        logger.debug(f"Emitting event {event}")

    def construct_event(
        self,
        *,
        view: ModelViewSet,
        instance: Model = None,
        serializer: ModelSerializer = None,
    ) -> Any:
        event = {"view": view, "instance": instance, "serializer": serializer}
        logger.debug(f"Constructed event {event}")
        return event
