from unittest.mock import patch

from django.test import TestCase
from faker import Faker

from tests.factories import (
    SimpleModelFactory,
    SimpleModelUuidPkFactory,
    ModelWithForeignKeyFactory,
    ModelWithManyToManyFieldFactory,
)


class ModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.faker = Faker()
        Faker.seed(0)
        cls.simple_model_factory_class = SimpleModelFactory
        cls.simple_model_uuid_pk_factory_class = SimpleModelUuidPkFactory
        cls.foreign_key_model_factory_class = ModelWithForeignKeyFactory
        cls.many_to_many_model_factory_class = ModelWithManyToManyFieldFactory
        super().setUpClass()


class TestModelViewSetCallsEventHandlerMethods(ModelTest):
    @patch("example_app.views.SimpleModelViewSet._emit_event")
    @patch("example_app.views.SimpleModelViewSet._get_event")
    def test_model_viewset_create_event(self, set_event_mock, emit_event_mock):
        char_field = self.faker.password()
        payload = {"char_field": char_field}
        self.client.post("/simple-model/", payload)
        set_event_mock.assert_called()
        emit_event_mock.assert_called()

    @patch("example_app.views.SimpleModelViewSet._emit_event")
    @patch("example_app.views.SimpleModelViewSet._get_event")
    def test_model_viewset_destroy_event(self, set_event_mock, emit_event_mock):
        instance = self.simple_model_factory_class.create()
        self.client.delete(f"/simple-model/{instance.pk}/")
        set_event_mock.assert_called()
        emit_event_mock.assert_called()

    @patch("example_app.views.SimpleModelViewSet._emit_event")
    @patch("example_app.views.SimpleModelViewSet._get_event")
    def test_model_viewset_partial_update_event(self, set_event_mock, emit_event_mock):
        instance = self.simple_model_factory_class.create()
        payload = {"boolean": False}
        self.client.patch(f"/simple-model/{instance.pk}/", json=payload)
        set_event_mock.assert_called()
        emit_event_mock.assert_called()
