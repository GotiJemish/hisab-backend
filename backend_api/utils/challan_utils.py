from backend_api.models import Challan


# ------------------------------
# Build prefix based on date
# ------------------------------
def get_challan_prefix(date):
    prefix = date.strftime("%b").upper()  # JAN
    yydd = date.strftime("%y%d")  # 2507
    return f"CH-{prefix}-{yydd}"  # CH-JAN-2507


# ----------------------------------------
# Get next challan number (auto-generate)
# ----------------------------------------
def get_next_challan_number(user, date):
    base = get_challan_prefix(date)

    last_challan = (
        Challan.objects.filter(user=user, invoice_number__startswith=base)
        .order_by("-invoice_number")
        .first()
    )

    if last_challan:
        last4 = int(last_challan.invoice_number[-4:])
        next_num = last4 + 1
    else:
        next_num = 1

    return f"{base}{next_num:04d}"


# ----------------------------------------
# Find missing numbers (for dropdown list)
# ----------------------------------------
def get_missing_challan_numbers(user, date):
    base = get_challan_prefix(date)

    challans = Challan.objects.filter(
        user=user, invoice_number__startswith=base
    ).values_list("invoice_number", flat=True)

    used = sorted([int(x[-4:]) for x in challans])

    missing = []

    if used:
        for num in range(1, used[-1]):
            if num not in used:
                missing.append(f"{base}{num:04d}")

    return missing


# ----------------------------------------
# Validate manually-entered challan number
# ----------------------------------------
def validate_user_challan_number(user, date, challan_number, exclude_id=None):
    base = get_challan_prefix(date)

    # 1. Check prefix matches date
    if not challan_number.startswith(base):
        raise ValueError(f"Challan number must start with prefix '{base}'.")

    # 2. Check last 4 digits are numeric
    try:
        int(challan_number[-4:])
    except ValueError:
        raise ValueError("Invalid challan number format. Must end with 4 digits.")

    # 3. Check if number already used by this user
    query = Challan.objects.filter(user=user, invoice_number=challan_number)
    if exclude_id:
        query = query.exclude(id=exclude_id)
    if query.exists():
        raise ValueError(f"Challan number {challan_number} is already used.")
