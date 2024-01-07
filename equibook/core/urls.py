from equibook.core import views

app_name = "core"

urlpatterns = (
    views.transaction_urls
    + views.account_urls
    + views.operation_urls
    + views.accounting_period_urls
    + views.report_urls
    + views.settings_urls
)
