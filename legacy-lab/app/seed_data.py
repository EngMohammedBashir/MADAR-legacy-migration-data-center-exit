import os
from datetime import datetime, timedelta

import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "madar_legacy",
    "user": "madar_app",
    "password": os.environ["MADAR_DB_PASSWORD"],
}

BASE_TIME = datetime(2026, 8, 1, 8, 0, 0)

customers = [
    ("Riyadh Medical Supplies", "Riyadh"),
    ("Najd Industrial Services", "Riyadh"),
    ("Jeddah Trading Company", "Jeddah"),
    ("Red Sea Retail Group", "Jeddah"),
    ("Eastern Energy Services", "Dammam"),
    ("Gulf Equipment Company", "Dammam"),
    ("Qassim Food Distribution", "Qassim"),
    ("Madinah Hospitality Group", "Madinah"),
    ("Makkah Commercial Services", "Makkah"),
    ("Tabuk Construction Supply", "Tabuk"),
]

routes = [
    ("Riyadh", "Jeddah"),
    ("Jeddah", "Dammam"),
    ("Dammam", "Riyadh"),
    ("Riyadh", "Madinah"),
    ("Jeddah", "Makkah"),
]

status_flow = [
    "CREATED",
    "PICKED_UP",
    "IN_TRANSIT",
    "OUT_FOR_DELIVERY",
    "DELIVERED",
]

conn = psycopg2.connect(**DB_CONFIG)
conn.autocommit = False

try:
    with conn.cursor() as cur:
        cur.execute(
            "TRUNCATE shipment_events, shipments, customers "
            "RESTART IDENTITY CASCADE;"
        )

        for company_name, region in customers:
            cur.execute(
                "INSERT INTO customers (company_name, region) VALUES (%s, %s);",
                (company_name, region),
            )

        shipment_number = 0

        for customer_id in range(1, 11):
            for route_index in range(5):
                shipment_number += 1
                origin, destination = routes[route_index]
                status_index = (shipment_number - 1) % len(status_flow)
                status = status_flow[status_index]
                created_at = BASE_TIME + timedelta(hours=shipment_number * 6)
                updated_at = created_at + timedelta(hours=status_index * 8)

                cur.execute(
                    """
                    INSERT INTO shipments
                        (customer_id, origin, destination, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING shipment_id;
                    """,
                    (customer_id, origin, destination, status, created_at, updated_at),
                )

                shipment_id = cur.fetchone()[0]

                # Record every workflow stage reached by each shipment. With ten
                # shipments at each of the five status depths, the event total is
                # deterministically 10 * (1 + 2 + 3 + 4 + 5) = 150.
                for event_index, event_type in enumerate(
                    status_flow[: status_index + 1]
                ):
                    event_time = created_at + timedelta(hours=event_index * 8)
                    cur.execute(
                        """
                        INSERT INTO shipment_events
                            (shipment_id, event_type, event_time)
                        VALUES (%s, %s, %s);
                        """,
                        (shipment_id, event_type, event_time),
                    )

    conn.commit()
    print("MADAR deterministic seed completed.")
    print("Customers: 10")
    print("Shipments: 50")
    print("Shipment events: 150")

except Exception:
    conn.rollback()
    raise

finally:
    conn.close()
