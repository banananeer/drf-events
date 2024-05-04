from rest_framework.serializers import ModelSerializer

from example_app.models import (
    SimpleModel,
    ModelWithForeignKeyField,
    ModelWithManyToManyField,
    SimpleUuidPkModel,
)


class SimpleModelSerializer(ModelSerializer):
    class Meta:
        model = SimpleModel
        fields = "__all__"


class SimpleUuidPkSerializer(ModelSerializer):
    class Meta:
        model = SimpleUuidPkModel
        fields = "__all__"


class ModelWithForeignKeyFieldSerializer(ModelSerializer):
    class Meta:
        model = ModelWithForeignKeyField
        fields = "__all__"


class ModelWithManyToManyFieldSerializer(ModelSerializer):
    class Meta:
        model = ModelWithManyToManyField
        fields = "__all__"
