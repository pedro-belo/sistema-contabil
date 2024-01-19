from django.db import models


class AccountManager(models.Manager):

    def from_user(self, user):
        return self.model.objects.filter(user=user)

    def get_asset(self, user):
        return self.model.objects.get(
            user=user, account_type=self.model.AccountTypeOfAccount.ASSET
        )

    def get_result(self, user):
        return self.model.objects.get(
            user=user, account_type=self.model.AccountTypeOfAccount.RESULT
        )

    def get_liability(self, user):
        return self.model.objects.get(
            user=user, account_type=self.model.AccountTypeOfAccount.LIABILITY
        )

    def get_equity(self, user):
        return self.model.objects.get(
            user=user, account_type=self.model.AccountTypeOfAccount.EQUITY
        )

    def get_revenue(self, user):
        return self.model.objects.get(
            user=user, account_type=self.model.AccountTypeOfAccount.REVENUE
        )

    def get_expense(self, user):
        return self.model.objects.get(
            user=user, account_type=self.model.AccountTypeOfAccount.EXPENSE
        )

    def for_user(self, user, include_root=True):
        queryset = self.get_queryset().filter(user=user)
        return (
            queryset
            if include_root
            else queryset.filter(
                account_type=self.model.AccountTypeOfAccount.SUBDIVISION
            )
        )


class TransactionManager(models.Manager):
    def for_user(self, user):
        return self.get_queryset().filter(user=user)

    def for_period(self, period, accounts=[]):
        queryset = self.get_queryset().filter(period=period)
        return (
            queryset.filter(transaction_operation__account__in=accounts)
            if accounts
            else queryset
        )


class OperationManager(models.Manager):
    def for_period(self, period):
        return self.get_queryset().filter(transaction__period=period)


class OperationMetaManager(models.Manager):
    def for_period(self, period):
        return self.get_queryset().filter(operation__transaction__period=period)

    def for_user(self, user):
        return self.get_queryset().filter(operation__transaction__user=user)
