import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

# Set seed for reproducibility if needed
fake = Faker("en_US")

# --- CONFIGURATIONS ---
ORDER_COUNT = 50
UPDATE_COUNT = 150
# Path management using Pathlib for cross-platform compatibility
BASE_DIR = Path(__file__).parent.parent.parent
OUTPUT_PATH = BASE_DIR / "data" / "raw"


# --- LOGISTICS STATE MACHINE ---
NEXT_STEP_MAPPING = {
    "Pending": ["Processing", "Cancelled"],
    "Processing": ["Shipped"],
    "Shipped": ["Delivered"],
    "Delivered": [],
    "Cancelled": [],
}

# Simulated Product Catalog with weights and average prices
PRODUCT_CATALOG = [
    {"name": "Dell G15 Laptop", "weight_unit": 2.5, "price_avg": 4000.0},
    {"name": "Logitech MX Mouse", "weight_unit": 0.2, "price_avg": 350.0},
    {"name": "LG Ultrawide Monitor", "weight_unit": 4.5, "price_avg": 1800.0},
    {"name": "Keychron Keyboard", "weight_unit": 0.8, "price_avg": 700.0},
]


def generate_mock_data():
    """Generates synthetic logistics data including orders and status updates."""

    # Ensure directory exists
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    print(f"🚀 Starting data generation at: {OUTPUT_PATH}")

    orders_data = []
    order_tracking = {}
    start_id = random.randint(1000, 9000)

    # 1. GENERATE ORDERS
    for i in range(ORDER_COUNT):
        current_id = start_id + i
        # Generate sale date between 30 days ago and yesterday
        sale_date = fake.date_time_between(start_date="-30d", end_date="-1d")
        product = random.choice(PRODUCT_CATALOG)
        quantity = random.randint(1, 3)

        # Logistics-specific data
        origin = fake.city()
        destination = fake.city()
        total_weight = round(product["weight_unit"] * quantity, 2)
        shipping_fee = round(random.uniform(15.0, 150.0), 2)

        row = {
            "order_id": current_id,
            "customer_name": fake.name(),
            "product": product["name"],
            "quantity": quantity,
            "unit_price": round(
                random.uniform(product["price_avg"] * 0.8, product["price_avg"] * 1.2),
                2,
            ),
            "origin": origin,
            "destination": destination,
            "weight_kg": total_weight,
            "shipping_cost": shipping_fee,
            "status": "Pending",
            "sale_timestamp": sale_date.strftime("%Y-%m-%d %H:%M:%S"),
        }

        orders_data.append(row)
        order_tracking[current_id] = {"status": "Pending", "last_date": sale_date}

    # Save Orders CSV
    orders_file = OUTPUT_PATH / "orders.csv"
    with open(orders_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=orders_data[0].keys())
        writer.writeheader()
        writer.writerows(orders_data)

    print(f"✅ Orders generated: {orders_file}")

    # 2. GENERATE LOGISTICS UPDATES
    updates_data = []

    # Generate updates for available orders
    for _ in range(UPDATE_COUNT):
        available_ids = [
            k
            for k, v in order_tracking.items()
            if v["status"] not in ["Delivered", "Cancelled"]
        ]

        if not available_ids:
            print("⚠️ All orders finalized before reaching update limit.")
            break

        selected_id = random.choice(available_ids)
        current_data = order_tracking[selected_id]

        new_status = random.choice(NEXT_STEP_MAPPING[current_data["status"]])
        # Logistics delay: 4 hours to 3 days
        time_elapsed = timedelta(hours=random.randint(4, 72))
        event_date = current_data["last_date"] + time_elapsed

        # Prevent future dates
        if event_date > datetime.now():
            event_date = datetime.now()

        updates_data.append(
            {
                "order_id": selected_id,
                "status": new_status,
                "status_timestamp": event_date.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

        # Update tracking for next iterations
        order_tracking[selected_id]["status"] = new_status
        order_tracking[selected_id]["last_date"] = event_date

    # Save Updates CSV
    updates_file = OUTPUT_PATH / "logistics_updates.csv"
    with open(updates_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=updates_data[0].keys())
        writer.writeheader()
        writer.writerows(updates_data)

    print(f"✅ Success: {ORDER_COUNT} orders and {len(updates_data)} updates created.")


if __name__ == "__main__":
    generate_mock_data()
