# Generated by Django 4.2.7 on 2023-12-15 20:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_alter_account_options_alter_operationmeta_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccountingPeriod",
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
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
            ],
        ),
    ]
