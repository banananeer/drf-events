# Generated by Django 5.0.4 on 2024-04-28 20:42

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("example_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SimpleUuidPkModel",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ModelWithManyToManyField",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "many_to_many_field",
                    models.ManyToManyField(to="example_app.simpleuuidpkmodel"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ModelWithForeignKeyField",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "foreign_key_field",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="example_app.simpleuuidpkmodel",
                    ),
                ),
            ],
        ),
    ]
