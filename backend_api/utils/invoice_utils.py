from backend_api.models import Invoice


# ------------------------------
# Build prefix based on date
# ------------------------------
def get_invoice_prefix(date):
    prefix = date.strftime("%b").upper()       # JAN
    yydd = date.strftime("%y%d")               # 2507
    return f"{prefix}-{yydd}"                  # JAN-2507


# ----------------------------------------
# Get next invoice number (auto-generate)
# ----------------------------------------
def get_next_invoice_number(user, date):
    base = get_invoice_prefix(date)

    last_invoice = Invoice.objects.filter(
        user=user,
        invoice_number__startswith=base
    ).order_by("-invoice_number").first()

    if last_invoice:
        last4 = int(last_invoice.invoice_number[-4:])
        next_num = last4 + 1
    else:
        next_num = 1

    return f"{base}{next_num:04d}"


# ----------------------------------------
# Find missing numbers (for dropdown list)
# ----------------------------------------
def get_missing_invoice_numbers(user, date):
    base = get_invoice_prefix(date)

    invoices = Invoice.objects.filter(
        user=user,
        invoice_number__startswith=base
    ).values_list("invoice_number", flat=True)

    used = sorted([int(x[-4:]) for x in invoices])

    missing = []

    if used:
        for num in range(1, used[-1]):
            if num not in used:
                missing.append(f"{base}{num:04d}")

    return missing


# ----------------------------------------
# Validate manually-entered invoice number
# ----------------------------------------
def validate_user_invoice_number(user, date, invoice_number):
    base = get_invoice_prefix(date)

    # 1. Check prefix matches date
    if not invoice_number.startswith(base):
        raise ValueError(
            f"Invoice number must start with prefix '{base}'."
        )

    # 2. Check last 4 digits are numeric
    try:
        seq = int(invoice_number[-4:])
    except:
        raise ValueError("Invalid invoice number format. Must end with 4 digits.")

    # 3. Check if number already used by this user
    if Invoice.objects.filter(user=user, invoice_number=invoice_number).exists():
        raise ValueError(f"Invoice number {invoice_number} is already used.")
