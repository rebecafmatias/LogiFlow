import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker
from sqlalchemy import Column, DateTime, Integer, String, create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

# --- SETUP & PATHS ---
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
fake = Faker("en_US")
BASE_DIR = Path(__file__).parent.parent.parent
OUTPUT_PATH = BASE_DIR / "data" / "raw"
DB_PATH = BASE_DIR / "ingestion_state.db"

# --- SQLALCHEMY MODELS ---
Base = declarative_base()
# Added timeout to prevent "Database Locked" errors
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"timeout": 30})


# Enable WAL mode so you can use DBeaver without locking the script
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


Session = sessionmaker(bind=engine)


class OrderState(Base):
    __tablename__ = "order_state"
    order_id = Column(Integer, primary_key=True)
    status = Column(String)
    last_date = Column(DateTime)


# Create table if it doesn't exist
Base.metadata.create_all(engine)

# --- CONFIGURATIONS ---
NEW_ORDERS_COUNT = 10
CHANCE_OF_UPDATE = 0.5
PRODUCT_CATALOG = [
    {"name": "Dell G15 Laptop", "weight_unit": 2.5, "price_avg": 4000.0},
    {"name": "Logitech MX Mouse", "weight_unit": 0.2, "price_avg": 350.0},
    {"name": "LG Ultrawide Monitor", "weight_unit": 4.5, "price_avg": 1800.0},
    {"name": "Keychron Keyboard", "weight_unit": 0.8, "price_avg": 700.0},
]
NEXT_STEP_MAPPING = {
    "Pending": ["Processing", "Cancelled"],
    "Processing": ["Shipped"],
    "Shipped": ["Delivered"],
    "Delivered": [],
    "Cancelled": [],
}


def generate_mock_data():
    """Generates synthetic logistics data and maintains state via SQLite."""
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    session = Session()
    print(f"🚀 Database state: {DB_PATH}")

    orders_data = []
    updates_data = []

    # 1. GENERATE NEW ORDERS
    # Get the last ID from DB to continue the sequence
    last_order = session.query(OrderState).order_by(OrderState.order_id.desc()).first()
    start_id = (last_order.order_id + 1) if last_order else 1000

    for i in range(NEW_ORDERS_COUNT):
        current_id = start_id + i
        # GUARANTEE 1: Randomized seconds and microseconds on creation
        sale_date = datetime.now() - timedelta(
            days=random.randint(1, 5),
            minutes=random.randint(1, 60),
            seconds=random.randint(0, 59),
            microseconds=random.randint(0, 999999),
        )
        product = random.choice(PRODUCT_CATALOG)
        quantity = random.randint(1, 3)

        row = {
            "order_id": current_id,
            "customer_name": fake.name(),
            "product": product["name"],
            "quantity": quantity,
            "unit_price": round(
                random.uniform(product["price_avg"] * 0.8, product["price_avg"] * 1.2),
                2,
            ),
            "origin": fake.city(),
            "destination": fake.city(),
            "weight_kg": round(product["weight_unit"] * quantity, 2),
            "shipping_cost": round(random.uniform(15.0, 150.0), 2),
            "status": "Pending",
            "sale_timestamp": sale_date.strftime("%Y-%m-%d %H:%M:%S"),
        }
        orders_data.append(row)

        # Save initial state to DB
        new_order_state = OrderState(
            order_id=current_id, status="Pending", last_date=sale_date
        )
        session.add(new_order_state)

    # 2. UPDATE EXISTING ORDERS
    active_orders = (
        session.query(OrderState)
        .filter(OrderState.status.notin_(["Delivered", "Cancelled"]))
        .all()
    )

    for order in active_orders:
        # Only update if it's an old order and hits the probability
        if order.order_id < start_id and random.random() < CHANCE_OF_UPDATE:
            options = NEXT_STEP_MAPPING.get(order.status, [])
            if options:
                new_status = random.choice(options)

                # GUARANTEE 2: Forced delay with varied minutes and seconds
                random_delay = timedelta(
                    hours=random.randint(1, 24),
                    minutes=random.randint(1, 59),
                    seconds=random.randint(1, 59),
                )
                event_date = order.last_date + random_delay

                # Prevent timestamps from being in the future
                if event_date > datetime.now():
                    event_date = datetime.now()

                updates_data.append(
                    {
                        "order_id": order.order_id,
                        "status": new_status,
                        "status_timestamp": event_date.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )

                # Update state in DB
                order.status = new_status
                order.last_date = event_date

    session.commit()

    # --- SAVE FILES ---
    if orders_data:
        orders_file = OUTPUT_PATH / f"orders_{timestamp}.csv"
        with open(orders_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=orders_data[0].keys())
            writer.writeheader()
            writer.writerows(orders_data)
        print(f"✅ New orders: {len(orders_data)} -> {orders_file.name}")

    if updates_data:
        updates_file = OUTPUT_PATH / f"logistics_updates_{timestamp}.csv"
        with open(updates_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=updates_data[0].keys())
            writer.writeheader()
            writer.writerows(updates_data)
        print(f"✅ Logistics updates: {len(updates_data)} -> {updates_file.name}")

    session.close()


if __name__ == "__main__":
    generate_mock_data()
