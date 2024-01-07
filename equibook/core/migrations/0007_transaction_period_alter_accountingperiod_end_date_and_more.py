# Generated by Django 4.2.7 on 2023-12-16 11:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0006_accountingperiod_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="period",
            field=models.ForeignKey(
                default=4,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="period_transaction",
                to="core.accountingperiod",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="accountingperiod",
            name="end_date",
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="accountingperiod",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_accounting_period",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Usuário",
            ),
        ),
    ]
