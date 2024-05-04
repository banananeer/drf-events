import json

from rest_framework.viewsets import ModelViewSet

from drf_events.event_handlers.aws import EventBridgeEventHandler
from example_app.serializers import (
    SimpleModelSerializer,
    SimpleUuidPkSerializer,
    ModelWithForeignKeyFieldSerializer,
    ModelWithManyToManyFieldSerializer,
)
from tests.test_model_event_view import ModelTest


class TestEventBridgeEventHandlerSimpleModel(ModelTest):
    @classmethod
    def setUpClass(cls):
        cls.view = ModelViewSet()
        cls.maxDiff = None
        super().setUpClass()

    def test_create_event(self):
        self.maxDiff = None
        char_field = self.faker.password()
        payload = {"char_field": char_field}

        self.view.action = "create"
        serializer = SimpleModelSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        event_handler = EventBridgeEventHandler()
        event = event_handler.construct_event(
            view=self.view, serializer=serializer, instance=None
        )
        self.assertEqual(event.detail_type, "CREATE_SIMPLEMODEL")
        self.assertEqual(event.event_bus_name, "dev-bus")
        self.assertEqual(event.source, "this-project")
        self.assertEqual(json.dumps(serializer.data), event.detail)

    def test_destroy_event(self):
        self.view.action = "destroy"
        instance = self.simple_model_factory_class.create()

        event_handler = EventBridgeEventHandler()
        event = event_handler.construct_event(
            view=self.view, serializer=None, instance=instance
        )
        self.assertEqual(json.dumps({"id": instance.pk}), event.detail)

    def test_partial_update_event(self):
        char_field = self.faker.password()
        payload = {"char_field": char_field}
        instance = self.simple_model_factory_class.create()
        self.view.action = "partial_update"
        serializer = SimpleModelSerializer(data=payload, instance=instance)
        serializer.is_valid(raise_exception=True)

        event_handler = EventBridgeEventHandler()
        event = event_handler.construct_event(
            view=self.view, serializer=serializer, instance=None
        )
        self.assertEqual(
            json.dumps(
                {
                    "id": instance.pk,
                    "diff": {
                        "char_field": {"old": instance.char_field, "new": char_field}
                    },
                }
            ),
            event.detail,
        )
        self.assertEqual(event.detail_type, "PARTIAL_UPDATE_SIMPLEMODEL")


class TestEventBridgeEventHandlerSimpleUUidPkModel(ModelTest):
    @classmethod
    def setUpClass(cls):
        cls.view = ModelViewSet()
        cls.maxDiff = None
        super().setUpClass()

    def test_create_event(self):
        self.maxDiff = None
        self.view.action = "create"
        serializer = SimpleUuidPkSerializer(data={})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        event_handler = EventBridgeEventHandler()
        event = event_handler.construct_event(
            view=self.view, serializer=serializer, instance=None
        )
        self.assertEqual(json.dumps(serializer.data), event.detail)

    def test_destroy_event(self):
        self.view.action = "destroy"
        instance = self.simple_model_uuid_pk_factory_class.create()

        event_handler = EventBridgeEventHandler()
        event = event_handler.construct_event(
            view=self.view, serializer=None, instance=instance
        )
        self.assertEqual(json.dumps({"uuid": str(instance.pk)}), event.detail)


class TestEventBridgeEventHandlerForeignKeyModel(ModelTest):
    @classmethod
    def setUpClass(cls):
        cls.view = ModelViewSet()
        cls.maxDiff = None
        super().setUpClass()

    def test_create_event(self):
        self.maxDiff = None
        self.view.action = "create"
        foreign_key_model = self.simple_model_uuid_pk_factory_class.create()
        serializer = ModelWithForeignKeyFieldSerializer(
            data={"foreign_key_field": foreign_key_model.pk}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        event_handler = EventBridgeEventHandler()
        event = event_handler.construct_event(
            view=self.view, serializer=serializer, instance=None
        )
        detail = {}
        for k in serializer.data:
            if isinstance(
                serializer.data[k], event_handler.FIELD_TYPES_TO_CONVERT_TO_STRING
            ):
                print("converting {k} to string".format(k=k))
                detail[k] = str(serializer.data[k])
            else:
                detail[k] = serializer.data[k]

        self.assertEqual(json.dumps(detail), event.detail)

    def test_destroy_event(self):
        self.view.action = "destroy"
        instance = self.simple_model_uuid_pk_factory_class.create()

        event_handler = EventBridgeEventHandler()
        event = event_handler.construct_event(
            view=self.view, serializer=None, instance=instance
        )
        self.assertEqual(json.dumps({"uuid": str(instance.pk)}), event.detail)

    def test_partial_update_event(self):
        instance1 = self.simple_model_uuid_pk_factory_class.create()
        instance2 = self.simple_model_uuid_pk_factory_class.create()

        foreign_key_instance = self.foreign_key_model_factory_class.create(
            foreign_key_field=instance1
        )

        self.view.action = "partial_update"
        payload = {"foreign_key_field": instance2.pk}
        serializer = ModelWithForeignKeyFieldSerializer(
            data=payload, instance=foreign_key_instance
        )
        serializer.is_valid(raise_exception=True)

        event_handler = EventBridgeEventHandler()
        event = event_handler.construct_event(
            view=self.view, serializer=serializer, instance=None
        )
        self.assertEqual(
            json.dumps(
                {
                    "id": foreign_key_instance.pk,
                    "diff": {
                        "foreign_key_field": {
                            "old": str(instance1.pk),
                            "new": str(instance2.pk),
                        }
                    },
                }
            ),
            event.detail,
        )
        self.assertEqual(event.detail_type, "PARTIAL_UPDATE_MODELWITHFOREIGNKEYFIELD")


class TestEventBridgeEventHandlerManyToManyModel(ModelTest):
    @classmethod
    def setUpClass(cls):
        cls.view = ModelViewSet()
        cls.maxDiff = None
        super().setUpClass()

    def test_create_event(self):
        self.maxDiff = None
        self.view.action = "create"
        simple_model_uuid_pk = self.simple_model_uuid_pk_factory_class.create()
        serializer = ModelWithManyToManyFieldSerializer(
            data={"many_to_many_field": [simple_model_uuid_pk.pk]}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        event_handler = EventBridgeEventHandler()
        event = event_handler.construct_event(
            view=self.view, serializer=serializer, instance=None
        )
        detail = event_handler._convert_serializer_data_to_json_safe(serializer)
        self.assertEqual(json.dumps(detail), event.detail)

    def test_destroy_event(self):
        self.view.action = "destroy"
        instance = self.simple_model_uuid_pk_factory_class.create()

        event_handler = EventBridgeEventHandler()
        event = event_handler.construct_event(
            view=self.view, serializer=None, instance=instance
        )
        self.assertEqual(json.dumps({"uuid": str(instance.pk)}), event.detail)

    def test_partial_update_event(self):
        instance1 = self.simple_model_uuid_pk_factory_class.create()
        instance2 = self.simple_model_uuid_pk_factory_class.create()

        foreign_key_instance = self.foreign_key_model_factory_class.create(
            foreign_key_field=instance1
        )

        self.view.action = "partial_update"
        payload = {"foreign_key_field": instance2.pk}
        serializer = ModelWithForeignKeyFieldSerializer(
            data=payload, instance=foreign_key_instance
        )
        serializer.is_valid(raise_exception=True)

        event_handler = EventBridgeEventHandler()
        event = event_handler.construct_event(
            view=self.view, serializer=serializer, instance=None
        )
        self.assertEqual(
            json.dumps(
                {
                    "id": foreign_key_instance.pk,
                    "diff": {
                        "foreign_key_field": {
                            "old": str(instance1.pk),
                            "new": str(instance2.pk),
                        }
                    },
                }
            ),
            event.detail,
        )
        self.assertEqual(event.detail_type, "PARTIAL_UPDATE_MODELWITHFOREIGNKEYFIELD")
