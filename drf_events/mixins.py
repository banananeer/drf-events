import logging
from typing import Any

from django.db.models import Model
from rest_framework import mixins
from django.conf import settings
from django.db import transaction
from rest_framework.serializers import Serializer

from drf_events.event_handlers import BaseEventHandler

logger = logging.getLogger(__name__)


class EventViewMixin:
    """
    Emit events for views.
    """

    event_handler_class: BaseEventHandler = None

    def get_event_handler(self) -> BaseEventHandler:
        """
        Return the event handler instance that should be used for emitting events.
        """
        event_handler_class = self.get_event_handler_class()
        return event_handler_class()  # noqa

    def get_event_handler_class(self) -> BaseEventHandler:
        """
        Return the class to use for the event handler.
        Defaults to using `self.event_handler_class`.

        You may want to override this if you need to provide different
        event handlers depending on the incoming request.

        (Eg. logging some events, others get sent to EventBridge)
        """
        assert self.event_handler_class is not None, (
            "'%s' should either include a `event_handler_class` attribute, "
            "or override the `get_event_handler_class()` method."
            % self.__class__.__name__
        )

        return self.event_handler_class

    def _get_event(self, instance: Model = None, serializer: Serializer = None) -> Any:
        event_handler = self.get_event_handler()
        event = event_handler.construct_event(
            view=self, instance=instance, serializer=serializer
        )
        return event

    def _emit_event(self, event: Any):
        event_handler = self.get_event_handler()
        event_handler.emit_event(event=event)


class CreateModelEventMixin(mixins.CreateModelMixin, EventViewMixin):
    """
    Emit event when a model is created through a view.
    """

    emit_create_events = False

    def perform_create(self, serializer):
        """
        Do things
        :param serializer:
        :return:
        """
        with transaction.atomic():
            super().perform_create(serializer)
            if getattr(
                settings,
                "DRF_EVENTS_EMIT_CREATE_EVENTS",
                self.emit_create_events,
            ):
                event = self._get_event(instance=None, serializer=serializer)
                self._emit_event(event)


class DestroyModelEventMixin(mixins.DestroyModelMixin, EventViewMixin):
    emit_destroy_events = False

    def perform_destroy(self, instance):
        with transaction.atomic():
            if getattr(self, "DRF_EVENTS_DESTROY_EVENTS", self.emit_destroy_events):
                event = self._get_event(instance=instance, serializer=None)

            super().perform_destroy(instance=instance)

            if getattr(self, "DRF_EVENTS_DESTROY_EVENTS", self.emit_destroy_events):
                self._emit_event(event)


class UpdateModelEventMixin(mixins.UpdateModelMixin, EventViewMixin):
    emit_update_events = False

    def perform_update(self, serializer):
        with transaction.atomic():
            if getattr(
                settings, "DRF_EVENTS_EMIT_UPDATE_EVENTS", self.emit_update_events
            ):
                event = self._get_event(instance=None, serializer=serializer)
            super().perform_update(serializer)
            if getattr(
                settings, "DRF_EVENTS_EMIT_UPDATE_EVENTS", self.emit_update_events
            ):
                self._emit_event(event)
