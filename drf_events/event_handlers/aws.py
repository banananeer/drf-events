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
    FIELD_TYPES_TO_CONVERT_TO_STRING = (UUID, date, datetime)

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
            detail = self._get_serializer_diff(serializer=serializer)
        else:
            detail = self._convert_serializer_data_to_json_safe(serializer=serializer)
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

    def _get_serializer_diff(self, serializer: ModelSerializer) -> dict:
        diff = {}

        if isinstance(serializer.instance.pk, UUID):
            pk = str(serializer.instance.pk)
        else:
            pk = serializer.instance.pk

        for field_name in serializer.validated_data:
            field = serializer.instance._meta.get_field(field_name)  # noqa
            old_value = getattr(serializer.instance, field_name)
            new_value = serializer.validated_data[field_name]
            if isinstance(field, ManyToManyField):
                field_identifier = getattr(
                    serializer.instance, f"EVENT_{field_name}_IDENTIFIER".upper(), "pk"
                )

                _ = []
                for related_model in old_value.all():
                    value = getattr(related_model, field_identifier)
                    if isinstance(value, self.FIELD_TYPES_TO_CONVERT_TO_STRING):
                        value = str(value)
                    _.append(value)

                logger.debug(_)
                old_value = sorted(_)
                logger.debug(f"Old values are {old_value}")

                _ = []
                for related_model in new_value.all():
                    value = getattr(related_model, field_identifier)
                    if isinstance(value, self.FIELD_TYPES_TO_CONVERT_TO_STRING):
                        value = str(value)
                    _.append(value)

                logger.debug(_)
                new_value = sorted(_)
                logger.debug(f"New values are {old_value}")

            elif isinstance(field, ForeignKey):
                if old_value:
                    old_value = old_value.pk

                if new_value:
                    new_value = new_value.pk

            if isinstance(old_value, self.FIELD_TYPES_TO_CONVERT_TO_STRING):
                old_value = str(old_value)

            if isinstance(new_value, self.FIELD_TYPES_TO_CONVERT_TO_STRING):
                new_value = str(new_value)

            if old_value == new_value:
                continue

            diff.update({field_name: {"old": old_value, "new": new_value}})

        if diff:
            diff = {serializer.instance._meta.pk.name: pk, "diff": diff}  # noqa
        else:
            diff = None

        return diff

    @classmethod
    def _convert_serializer_data_to_json_safe(cls, serializer: ModelSerializer):
        detail = serializer.data
        for k in detail:
            if isinstance(detail[k], cls.FIELD_TYPES_TO_CONVERT_TO_STRING):
                detail[k] = str(detail[k])
            elif isinstance(detail[k], list):
                for item in detail[k]:
                    if isinstance(item, cls.FIELD_TYPES_TO_CONVERT_TO_STRING):
                        detail[k] = str(item)
            else:
                detail[k] = serializer.data[k]
        return detail
