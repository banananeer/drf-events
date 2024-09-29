import logging
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any
from uuid import UUID

from django.db.models import Model, ManyToManyField, ForeignKey
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet


logger = logging.getLogger(__name__)


class BaseEventHandler(ABC):
    """
    Event Handler base class.
    """
    FIELD_TYPES_TO_CONVERT_TO_STRING = (UUID, date, datetime)

    @abstractmethod
    def construct_event(
        self,
        *,
        view: ModelViewSet,
        serializer: ModelSerializer = None,
        instance: Model = None,
    ) -> Any:
        """
        this

        :param view: ModelViewSet
        :param serializer: ModelSerializer
        :param instance: Model

        :return: Any
        """
        raise NotImplemented

    @abstractmethod
    def emit_event(self, *, event: Any) -> None:
        """
        Method to emit an event

        :param event: Any

        :return: None
        """
        raise NotImplementedError

    def get_serializer_diff(self, serializer: ModelSerializer) -> dict:
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
    def _convert_dict_data_to_json_safe(cls, data: dict):
        for k in data:
            if isinstance(data[k], cls.FIELD_TYPES_TO_CONVERT_TO_STRING):
                data[k] = str(data[k])
            elif isinstance(data[k], list):
                for item in data[k]:
                    if isinstance(item, cls.FIELD_TYPES_TO_CONVERT_TO_STRING):
                        data[k] = str(item)
            else:
                data[k] = data[k]
        return data