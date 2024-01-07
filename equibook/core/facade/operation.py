from equibook.core.facade import base


def get_user_operationmeta(user: base.User) -> base.QuerySet[base.OperationMeta]:
    return base.OperationMeta.objects.filter(
        operation__in=base.Operation.objects.filter(transaction__user=user)
    )


def operation_meta_download(operation_meta: base.OperationMeta) -> base.HttpResponse:
    file_path = operation_meta.document.path

    if operation_meta.document:
        with open(file_path, "rb") as file:
            response = base.HttpResponse(
                file.read(), content_type="application/octet-stream"
            )
            response[
                "Content-Disposition"
            ] = f'attachment; filename="{operation_meta.document.name} - {base.datetime.now()}"'
            return response

    return base.HttpResponse(status_code=404)
