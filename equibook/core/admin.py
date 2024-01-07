from django.contrib import admin
from equibook.core import models


@admin.register(models.AccountingPeriod)
class AccountingPeriodAdmin(admin.ModelAdmin):
    list_display = (
        "status",
        "user",
        "start_date",
        "end_date",
    )


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "balance_type",
        "account_type",
        "parent",
        "user",
    )


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "period",
        "title",
        "next",
    )


@admin.register(models.Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = (
        "transaction",
        "account",
        "value",
        "type",
        "date",
    )


@admin.register(models.OperationMeta)
class OperationMetaAdmin(admin.ModelAdmin):
    list_display = "operation", "description"


@admin.register(models.Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "entity",
        "base_currency",
        "current_currency",
        "exchange_rate",
        "defined_first_period",
    )
