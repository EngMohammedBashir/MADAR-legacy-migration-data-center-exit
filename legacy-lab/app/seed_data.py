import os
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "madar_legacy",
    "user": "madar_app",
    "password": os.environ["MADAR_DB_PASSWORD"],
}

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

statuses = [
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
                status = statuses[(shipment_number - 1) % len(statuses)]

                cur.execute(
                    """
                    INSERT INTO shipments
                        (customer_id, origin, destination, status)
                    VALUES (%s, %s, %s, %s)
                    RETURNING shipment_id;
                    """,
                    (customer_id, origin, destination, status),
                )

                shipment_id = cur.fetchone()[0]

                for event_type in ("CREATED", "PICKED_UP", status):
                    cur.execute(
                        """
                        INSERT INTO shipment_events (shipment_id, event_type)
                        VALUES (%s, %s);
                        """,
                        (shipment_id, event_type),
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
