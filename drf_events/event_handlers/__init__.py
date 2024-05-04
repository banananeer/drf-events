import logging
from abc import ABC, abstractmethod
from typing import Any

from django.db.models import Model
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet


logger = logging.getLogger(__name__)


class BaseEventHandler(ABC):
    """
    Event Handler base class.
    """

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
