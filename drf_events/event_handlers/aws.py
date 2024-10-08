import json
from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

import boto3
from django.db.models import Model, ManyToManyField, ForeignKey
from django.conf import settings
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from drf_events import BaseEventHandler
from drf_events.event_handlers import logger
from drf_events.exceptions import (
    EventNotSentException,
    CannotDetermineInstanceClassName,
)


@dataclass
class EventBridgeEvent:
    """
    Event representing a payload to call the
    """

    detail: str
    detail_type: str
    source: str
    event_bus_name: str


class EventBridgeEventHandler(BaseEventHandler):

    def construct_event(
        self,
        *,
        view: ModelViewSet,
        serializer: ModelSerializer = None,
        instance: Model = None,
    ) -> EventBridgeEvent:
        logger.debug(view.action)

        if serializer and serializer.instance:
            instance_class_name = serializer.instance.__class__.__name__
        elif instance:
            instance_class_name = instance.__class__.__name__
        else:
            raise CannotDetermineInstanceClassName

        if view.action == "destroy":
            if isinstance(instance.pk, self.FIELD_TYPES_TO_CONVERT_TO_STRING):
                pk = str(instance.pk)
            else:
                pk = instance.pk
            detail = {instance._meta.pk.name: pk}
        elif view.action in ["update", "partial_update"]:
            detail = self.get_serializer_diff(serializer=serializer)
        else:
            detail = self._convert_dict_data_to_json_safe(serializer.data)
        logger.debug(detail)
        event = EventBridgeEvent(
            detail=json.dumps(detail),
            detail_type=f"{view.action}_{instance_class_name}".upper(),
            source=settings.DRF_EVENTS["aws"]["eventbridge"]["source"],
            event_bus_name=settings.DRF_EVENTS["aws"]["eventbridge"]["eventbus"],
        )
        return event

    def emit_event(self, *, eventbridge_event: EventBridgeEvent) -> None:
        client = boto3.client(
            "events",
            region_name=settings.DRF_EVENTS["aws"]["eventbridge"]["region_name"],
        )

        response = client.put_events(
            Entries=[
                {
                    "Source": eventbridge_event.source,
                    "DetailType": eventbridge_event.detail_type,
                    "Detail": eventbridge_event.detail,
                    "EventBusName": eventbridge_event.event_bus_name,
                },
            ],
            EndpointId="string",
        )

        if response["FailedEntryCount"] != 0:
            raise EventNotSentException
