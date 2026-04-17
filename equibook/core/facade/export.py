import io
import xlsxwriter
from equibook.core.facade import base


def export_transaction_history(user: base.User, periods=None, account=None):
    transactions = base.Transaction.objects.for_user(user)

    if periods:
        transactions = transactions.filter(period__in=periods)

    if account:
        transactions = transactions.filter(transaction_operation__account=account)

    transactions = (
        transactions
        .select_related("period")
        .prefetch_related("transaction_operation__account")
        .distinct()
    )

    transactions_list = list(transactions)

    distinct_period_ids = list(dict.fromkeys(t.period_id for t in transactions_list))
    use_period_colors = len(distinct_period_ids) > 1

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet("Transações")

    header_fmt = workbook.add_format({
        "bold": True,
        "bg_color": "#1e293b",
        "font_color": "#f8fafc",
    })

    stripe_colors = ["#EBF5FB", "#FDFEFE"]

    def make_fmts(bg_color=None):
        props = {"bg_color": bg_color} if bg_color else {}
        return (
            workbook.add_format(props),
            workbook.add_format({**props, "num_format": "#,##0.00"}),
        )

    if use_period_colors:
        period_fmts = {
            pid: make_fmts(stripe_colors[i % len(stripe_colors)])
            for i, pid in enumerate(distinct_period_ids)
        }
    else:
        default_fmts = make_fmts()

    columns = [
        ("ID", 8),
        ("Período", 22),
        ("Título", 30),
        ("Descrição", 40),
        ("Conta", 30),
        ("Tipo", 10),
        ("Valor", 15),
        ("Data", 12),
    ]

    for col, (header, width) in enumerate(columns):
        worksheet.write(0, col, header, header_fmt)
        worksheet.set_column(col, col, width)

    row = 1
    for transaction in transactions_list:
        period_label = (
            f"{transaction.period.start_date_dmy()} - {transaction.period.end_date_dmy()}"
        )
        text_fmt, money_fmt = (
            period_fmts[transaction.period_id] if use_period_colors else default_fmts
        )
        for op in transaction.transaction_operation.all():
            worksheet.write(row, 0, transaction.id, text_fmt)
            worksheet.write(row, 1, period_label, text_fmt)
            worksheet.write(row, 2, transaction.title, text_fmt)
            worksheet.write(row, 3, transaction.description, text_fmt)
            worksheet.write(row, 4, str(op.account), text_fmt)
            worksheet.write(row, 5, op.get_type_display(), text_fmt)
            worksheet.write(row, 6, float(op.value), money_fmt)
            worksheet.write(row, 7, op.date.strftime("%d/%m/%Y"), text_fmt)
            row += 1

    workbook.close()
    output.seek(0)
    return output
