from equibook.core import facade
from . import base


class OperationCreateView(base.FormView):
    form_class = base.OperationForm
    template_name = "core/operation/create.html"

    def accounts_for_user(self):
        return facade.Account.objects.for_user(
            self.request.user, include_root=False
        ).order_by("root_type", "name")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"accounts": self.accounts_for_user()})
        return kwargs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["transaction"] = base.get_transaction(self)
        return context_data

    def form_valid(self, form):
        operation = form.save(commit=False)
        operation.transaction = base.get_transaction(self)
        operation.save()
        return base.redirect("core:transaction-list")


class OperationDeleteView(base.DeleteView):
    def get_queryset(self):
        return facade.Operation.objects.for_period(self.period)

    def get(self, *args, **kwargs):
        raise base.PageNotFound()

    def get_success_url(self) -> str:
        return base.reverse("core:transaction-list")


class OperationMetaCreateView(base.FormView):
    form_class = base.OperationMetaForm
    template_name = "core/operation_meta/create.html"

    def get_operation(self):
        try:
            return facade.Operation.objects.for_period(self.period).get(
                pk=self.kwargs["pk"]
            )
        except facade.Operation.DoesNotExist:
            raise base.PageNotFound()

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["transaction"] = self.get_operation().transaction
        return context_data

    def form_valid(self, form: base.OperationMetaForm) -> base.DjHttpResponse:
        operation_meta = form.save(commit=False)
        operation_meta.operation = self.get_operation()
        operation_meta.save()
        return base.redirect(
            "core:transaction-detail", pk=operation_meta.operation.transaction.id
        )


class OperationMetaDeleteView(base.DeleteView):
    def get_queryset(self):
        return facade.OperationMeta.objects.for_period(self.period)

    def get(self, *args, **kwargs):
        raise base.PageNotFound()

    def get_success_url(self) -> str:
        return base.reverse(
            "core:transaction-detail", args=[self.object.transaction.id]
        )


class OperationMetaGetDocumentView(base.DetailView):
    def get_queryset(self):
        return facade.OperationMeta.objects.for_user(self.request.user)

    def get(self, request, *args, **kwargs):
        return facade.operation_meta_download(self.get_object())


url_patterns = [
    base.path(
        "operation/<int:transaction_id>/create/",
        OperationCreateView.as_view(),
        name="operation-create",
    ),
    base.path(
        "operation/<int:pk>/delete/",
        OperationDeleteView.as_view(),
        name="operation-delete",
    ),
    base.path(
        "operation/<int:pk>/meta/create/",
        OperationMetaCreateView.as_view(),
        name="operation-meta-create",
    ),
    base.path(
        "operation/<int:pk>/meta/delete/",
        OperationMetaDeleteView.as_view(),
        name="operation-meta-delete",
    ),
    base.path(
        "operation/<int:pk>/meta/download/",
        OperationMetaGetDocumentView.as_view(),
        name="operation-meta-download",
    ),
]
