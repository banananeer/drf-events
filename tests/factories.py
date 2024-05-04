import factory
from factory.django import DjangoModelFactory

from example_app.models import (
    SimpleModel,
    SimpleUuidPkModel,
    ModelWithForeignKeyField,
    ModelWithManyToManyField,
)


class SimpleModelFactory(DjangoModelFactory):
    class Meta:
        model = SimpleModel

    char_field = factory.Faker("password")
    date = factory.Faker("date")
    datetime = factory.Faker("date_time")
    boolean = factory.Faker("boolean")


class SimpleModelUuidPkFactory(DjangoModelFactory):
    class Meta:
        model = SimpleUuidPkModel


class ModelWithForeignKeyFactory(DjangoModelFactory):
    class Meta:
        model = ModelWithForeignKeyField

    foreign_key_field = factory.SubFactory(SimpleModelUuidPkFactory)


class ModelWithManyToManyFieldFactory(DjangoModelFactory):
    class Meta:
        model = ModelWithManyToManyField

    @factory.post_generation
    def many_to_many_field(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for related_model in extracted:
                self.many_to_many_field.add(related_model)
