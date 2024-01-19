import datetime
from datetime import date
from django.db import models
from django.contrib.auth import get_user_model
from equibook.core.managers import (
    AccountManager,
    TransactionManager,
    OperationManager,
    OperationMetaManager,
)

UserModel = get_user_model()


class Currency(models.IntegerChoices):
    BRL = 1, "BRL"
    USD = 2, "USD"
    EUR = 3, "EUR"
    JPY = 4, "JPY"
    GBP = 5, "GBP"
    CNY = 6, "CNY"


class Setting(models.Model):
    class Theme(models.IntegerChoices):
        LIGHT = 1, "Claro"
        DARK = 2, "Escuro"
        AUTO = 3, "Automático"

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="user_settings",
        verbose_name="Usuário",
    )

    entity = models.CharField(
        max_length=255,
        default="",
        verbose_name="Entidade",
    )

    base_currency = models.PositiveSmallIntegerField(
        choices=Currency.choices,
        default=Currency.BRL,
        verbose_name="Moeda base",
    )

    theme = models.PositiveSmallIntegerField(
        choices=Theme.choices,
        default=Theme.LIGHT,
        verbose_name="Tema",
    )

    current_currency = models.PositiveSmallIntegerField(
        choices=Currency.choices,
        default=Currency.BRL,
        verbose_name="Moeda atual",
    )

    exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        help_text="N BC/1 CC",
        verbose_name="Taxa de câmbio",
    )

    defined_first_period = models.BooleanField()

    def is_default_theme(self):
        if self.theme == self.Theme.AUTO:
            current_time = datetime.datetime.now().time()
            start_time = datetime.time(7, 0, 0)
            end_time = datetime.time(17, 30, 0)
            return start_time <= current_time <= end_time

        return self.theme == self.Theme.LIGHT

    def to_dict(self):
        return {
            "entity": self.entity,
            "base_currency": {
                "code": self.base_currency,
                "label": self.get_base_currency_display(),
            },
            "current_currency": {
                "code": self.current_currency,
                "label": self.get_current_currency_display(),
            },
            "exchange_rate": float(self.exchange_rate),
            "defined_first_period": self.defined_first_period,
            "theme": {
                "code": self.theme,
                "label": self.get_theme_display(),
            },
            "DARK_MODE": not self.is_default_theme(),
        }

    def __str__(self) -> str:
        return self.user.username

    class Meta:
        verbose_name = "Configuração"
        verbose_name_plural = "Configurações"


class OperationType(models.IntegerChoices):
    CREDIT = 1, "Crédito"
    DEBIT = 2, "Débito"


class TypeOfAccount(models.IntegerChoices):
    ASSET = 1, "Ativo"
    LIABILITY = 2, "Passivo"
    EQUITY = 3, "Patrimônio Líquido"
    SUBDIVISION = 4, "Subdivisão"
    REVENUE = 5, "Receitas"
    EXPENSE = 6, "Despesas"
    RESULT = 7, "Resultado"


class TypeOfBalance(models.IntegerChoices):
    CREDIT = 1, "Credor"
    DEBIT = 2, "Devedor"
    UNDEF = 3, "Indefinido"


class AccountingPeriod(models.Model):
    class Status(models.IntegerChoices):
        IN_PROGRESS = 1, "Em Curso"
        CLOSING_ACCOUNTS = 2, "Fechamento de Contas"
        CLOSED = 3, "Finalizado"

    status = models.PositiveSmallIntegerField(choices=Status.choices)

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="user_accounting_period",
        verbose_name="Usuário",
    )

    start_date = models.DateField()

    end_date = models.DateField()

    def in_progress(self) -> bool:
        return self.status == self.Status.IN_PROGRESS

    def closing_accounts(self) -> bool:
        return self.status == self.Status.CLOSING_ACCOUNTS

    def closed(self) -> bool:
        return self.status == self.Status.CLOSED

    def is_period_closeable(self) -> bool:
        return date.today() > self.end_date

    def days_to_close_period(self) -> int:
        return 0 if self.is_period_closeable() else (self.end_date - date.today()).days

    def start_date_dmy(self):
        return self.start_date.strftime("%d/%m/%Y")

    def end_date_dmy(self):
        return self.end_date.strftime("%d/%m/%Y")

    def __str__(self) -> str:
        return f"Period[{self.start_date}, {self.end_date}]"


class Account(models.Model):
    AccountTypeOfBalance = TypeOfBalance
    AccountTypeOfAccount = TypeOfAccount

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="user_accounts",
        verbose_name="Usuário",
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Nome",
    )

    balance_type = models.PositiveSmallIntegerField(
        choices=TypeOfBalance.choices,
        verbose_name="Tipo de Saldo",
    )

    account_type = models.PositiveSmallIntegerField(
        choices=TypeOfAccount.choices,
        verbose_name="Tipo de Conta",
    )

    parent = models.ForeignKey(
        "Account",
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Conta Pai",
        blank=True,
    )

    # Performance reanson
    root_type = models.PositiveSmallIntegerField(
        choices=TypeOfAccount.choices, null=True
    )

    objects: AccountManager = AccountManager()

    def __str__(self) -> str:
        return " • ".join([account.name for account in self.get_path()])

    def get_individual_balance(self):
        operations = self.account_operation.all()
        debit_sum = operations.filter(type=OperationType.DEBIT).aggregate(
            debit_sum=models.Sum("value", default=0)
        )["debit_sum"]

        credit_sum = operations.filter(type=OperationType.CREDIT).aggregate(
            credit_sum=models.Sum("value", default=0)
        )["credit_sum"]

        if self.account_type not in [
            TypeOfAccount.ASSET,
            TypeOfAccount.EQUITY,
            TypeOfAccount.LIABILITY,
            TypeOfAccount.EXPENSE,
            TypeOfAccount.REVENUE,
            TypeOfAccount.SUBDIVISION,
        ]:
            raise ValueError("Operação não definida")

        return (
            (debit_sum - credit_sum)
            if self.balance_type == TypeOfBalance.DEBIT
            else credit_sum - debit_sum
        )

    def total_operation_balance(self):
        result = 0

        for operation in self.account_operation.values("type", "value"):
            if self.balance_type == TypeOfBalance.CREDIT:
                if operation["type"] == OperationType.CREDIT:
                    result += operation["value"]
                elif operation["type"] == OperationType.DEBIT:
                    result -= operation["value"]
                else:
                    raise ValueError

            elif self.balance_type == TypeOfBalance.DEBIT:
                if operation["type"] == OperationType.DEBIT:
                    result += operation["value"]
                elif operation["type"] == OperationType.CREDIT:
                    result -= operation["value"]
                else:
                    raise ValueError
            else:
                raise ValueError

        return result

    def total_account_balance(self):
        result = 0
        for account in self.account_set.all():
            result += account.total_account_balance()

        return result + self.total_operation_balance()

    def can_remove(self):
        if self.account_type != TypeOfAccount.SUBDIVISION:
            return False

        if self.account_operation.count() > 0:
            return False

        if self.account_set.count() > 0:
            return False

        return True

    def get_path(self, self_include=True, reverse=True):
        path = [self] if self_include else []
        parent = self.parent

        while parent:
            path.append(parent)
            parent = parent.parent

        if reverse:
            path.reverse()

        return path

    def get_children(self):
        result = [self]

        for account in self.account_set.all():
            result.extend(account.get_children())

        return result

    class Meta:
        verbose_name = "Conta"
        verbose_name_plural = "Contas"


class Transaction(models.Model):
    period = models.ForeignKey(
        "AccountingPeriod",
        on_delete=models.CASCADE,
        related_name="period_transaction",
    )

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="user_transactions",
        verbose_name="Usuário",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Título",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descrição",
    )

    archived = models.BooleanField(default=False)

    next = models.OneToOneField(
        "Transaction",
        on_delete=models.PROTECT,
        related_name="previous",
        null=True,
    )

    def get_balance(self):
        values = self.transaction_operation.values("value", "type")
        credit_sum = values.filter(type=OperationType.CREDIT).aggregate(
            v_sum=models.Sum("value", default=0)
        )["v_sum"]
        debit_sum = values.filter(type=OperationType.DEBIT).aggregate(
            v_sum=models.Sum("value", default=0)
        )["v_sum"]

        return {
            "instance": self,
            "debit_sum": debit_sum,
            "credit_sum": credit_sum,
            "is_balanced": (debit_sum - credit_sum) == 0,
        }

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    objects: TransactionManager = TransactionManager()

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"


class Operation(models.Model):
    transaction = models.ForeignKey(
        "Transaction",
        on_delete=models.CASCADE,
        related_name="transaction_operation",
        verbose_name="Transação",
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="account_operation",
        verbose_name="Conta",
    )

    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor",
    )

    type = models.PositiveSmallIntegerField(
        choices=OperationType.choices,
        verbose_name="Tipo de Operação",
    )

    date = models.DateField(verbose_name="Data")

    objects: OperationManager = OperationManager()

    def is_credit(self):
        return self.type == OperationType.CREDIT

    def is_debit(self):
        return self.type == OperationType.DEBIT

    def __str__(self) -> str:
        return f"{self.transaction} => {self.get_type_display()} em {self.account} de {self.value}"

    class Meta:
        verbose_name = "Operação"
        verbose_name_plural = "Operações"


class OperationMeta(models.Model):
    operation = models.ForeignKey(
        "Operation", on_delete=models.CASCADE, related_name="operation_meta"
    )
    description = models.TextField(blank=False)
    document = models.FileField(blank=True)

    objects: OperationMetaManager = OperationMetaManager()

    @property
    def transaction(self):
        return self.operation.transaction

    class Meta:
        verbose_name = "Detalhe da Operação"
        verbose_name_plural = "Detalhes das Operações"
