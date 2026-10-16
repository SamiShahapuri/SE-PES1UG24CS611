"""Manage food delivery orders and track daily revenue."""

import json
from datetime import datetime

# Global state
orders = {}
menu = {}
VALID_STATUSES = {
    "placed",
    "cooking",
    "out_for_delivery",
    "delivered",
}


def create_order(customer, items, order_history=None):
    """Create an order and return its ID."""
    if not customer or not customer.strip():
        raise ValueError("Customer name cannot be empty.")

    if not items:
        raise ValueError("Order must contain at least one item.")

    total = 0
    for item in items:
        if item not in menu:
            raise ValueError(f"Unknown menu item: {item}")
        total += menu[item]

    order_id = max(orders, default=0) + 1

    orders[order_id] = {
        "customer": customer,
        "items": items,
        "total": total,
        "status": "placed",
    }

    if order_history is not None:
        order_history.append(order_id)

    return order_id


def update_order_status(order_id, status):
    """Update the status of an existing order."""
    if order_id not in orders:
        print(f"Error: Order {order_id} does not exist.")
        return

    if status not in VALID_STATUSES:
        print(f"Error: Invalid order status '{status}'.")
        return

    orders[order_id]["status"] = status


def read_menu_config(file="menu.json"):
    """Load menu prices from a JSON configuration file."""
    try:
        with open(file, "r", encoding="utf-8") as menu_file:
            loaded_menu = json.load(menu_file)

        menu.clear()
        menu.update(loaded_menu)
    except (OSError, json.JSONDecodeError):
        menu.clear()
        menu.update({
            "pizza": 250,
            "burger": 150,
            "fries": 90,
            "coke": 40,
        })


def daily_revenue():
    """Calculate revenue from delivered orders."""
    revenue = 0
    for order in orders.values():
        if order["status"] == "delivered":
            revenue += order["total"]

    return revenue


def backup_orders(file="orders.json"):
    """Save orders to a JSON backup file."""
    with open(file, "w", encoding="utf-8") as backup_file:
        json.dump(orders, backup_file)


def restore_orders(file="orders.json"):
    """Restore orders from a JSON backup file."""
    with open(file, "r", encoding="utf-8") as backup_file:
        restored_orders = json.load(backup_file)

    orders.clear()
    orders.update({
        int(key): value
        for key, value in restored_orders.items()
    })


def print_queue():
    """Display all orders in the queue."""
    print(f"Order queue at {datetime.now()}")
    for order_id, order in orders.items():
        print(
            order_id,
            order["customer"],
            order["status"],
            order["total"],
        )


def main():
    """Run the food delivery queue demonstration."""
    read_menu_config()
    asha_order = create_order("Asha", ["pizza", "coke"])
    ravi_order = create_order("Ravi", ["burger", "fries"])

    update_order_status(asha_order, "delivered")
    update_order_status(ravi_order, "cooking")

    print("Revenue today:", daily_revenue())
    backup_orders()
    restore_orders()
    print_queue()


if __name__ == "__main__":
    main()
