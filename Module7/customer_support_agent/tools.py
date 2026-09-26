import csv


# ==========================================
# TOOL 1: Get customer information
# ==========================================

def get_customer(customer_id):

    with open("data/customers.csv", "r") as file:

        customers = csv.DictReader(file)

        for customer in customers:

            if customer["customer_id"] == customer_id:
                return customer

    return None


# ==========================================
# TOOL 2: Get order information
# ==========================================

def get_order(order_id):

    with open("data/orders.csv", "r") as file:

        orders = csv.DictReader(file)

        for order in orders:

            if order["order_id"] == order_id:
                return order

    return None


# ==========================================
# TOOL 3: Get company refund policy
# ==========================================

def get_refund_policy():

    return """
ACME STORE REFUND POLICY

1. Damaged Products

Customers may request a full refund for products
that arrive damaged.

2. Refund Approval

Refunds of ₹1,000 or less may be processed automatically.

Refunds above ₹1,000 require human approval.

3. Refund Calculation

For an eligible damaged product, the refund amount
is equal to the purchase amount.

Products that are not eligible for a damaged-product
refund receive ₹0.

4. Missing Orders

Customers should contact support if an order has
not arrived within the expected delivery period.
"""


# ==========================================
# TOOL 4: Calculate refund
# ==========================================

def calculate_refund(order_id, amount, condition):

    amount = float(amount)

    if amount < 0:
        raise ValueError(
            "Order amount cannot be negative."
        )

    if condition.lower() == "damaged":

        return {
            "order_id": order_id,
            "eligible": True,
            "refund_amount": amount
        }

    return {
        "order_id": order_id,
        "eligible": False,
        "refund_amount": 0
    }


# ==========================================
# TOOL 5: Process refund
# ==========================================

def process_refund(order_id, amount):

    amount = float(amount)

    if amount <= 0:
        raise ValueError(
            "Refund amount must be greater than zero."
        )

    return {
        "status": "refund_processed",
        "order_id": order_id,
        "amount": amount
    }