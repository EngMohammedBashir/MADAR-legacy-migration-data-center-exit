import os

from flask import Flask, jsonify, render_template, request
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "database": "madar_legacy",
    "user": "madar_app",
    "password": os.environ["MADAR_DB_PASSWORD"],
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


@app.get("/")
def dashboard():
    return render_template("dashboard.html")


@app.get("/api/health")
def health():
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        conn.close()
        return jsonify({"status": "ok", "service": "madar-legacy-app", "database": "connected", "environment": "on-premises", "host": "MADAR-LEGACY-01"})
    except Exception as exc:
        return jsonify({"status": "error", "service": "madar-legacy-app", "database": "unavailable", "message": str(exc)}), 503


@app.get("/api/summary")
def summary():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    (SELECT COUNT(*) FROM customers) AS customers,
                    (SELECT COUNT(*) FROM shipments) AS shipments,
                    (SELECT COUNT(*) FROM shipments WHERE status = 'IN_TRANSIT') AS in_transit,
                    (SELECT COUNT(*) FROM shipments WHERE status = 'DELIVERED') AS delivered,
                    (SELECT COUNT(*) FROM shipment_events) AS events;
            """)
            return jsonify(cur.fetchone())
    finally:
        conn.close()


@app.get("/api/customers")
def customers():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT c.customer_id, c.company_name, c.region, COUNT(s.shipment_id) AS shipment_count
                FROM customers c
                LEFT JOIN shipments s ON s.customer_id = c.customer_id
                GROUP BY c.customer_id, c.company_name, c.region
                ORDER BY c.customer_id;
            """)
            return jsonify(cur.fetchall())
    finally:
        conn.close()


@app.get("/api/shipments")
def shipments():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT s.shipment_id, s.customer_id, c.company_name, s.origin, s.destination,
                       s.status, s.created_at, s.updated_at
                FROM shipments s
                JOIN customers c ON c.customer_id = s.customer_id
                ORDER BY s.shipment_id;
            """)
            return jsonify(cur.fetchall())
    finally:
        conn.close()


@app.get("/api/shipments/<int:shipment_id>/events")
def shipment_events(shipment_id):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT event_id, shipment_id, event_type, event_time
                FROM shipment_events
                WHERE shipment_id = %s
                ORDER BY event_id;
            """, (shipment_id,))
            return jsonify(cur.fetchall())
    finally:
        conn.close()


@app.patch("/api/shipments/<int:shipment_id>/status")
def update_shipment_status(shipment_id):
    payload = request.get_json(silent=True) or {}
    new_status = payload.get("status")
    allowed_statuses = {"CREATED", "PICKED_UP", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED"}

    if new_status not in allowed_statuses:
        return jsonify({"status": "error", "message": "Invalid shipment status"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT shipment_id, status FROM shipments WHERE shipment_id = %s;", (shipment_id,))
            shipment = cur.fetchone()
            if shipment is None:
                conn.rollback()
                return jsonify({"status": "error", "message": "Shipment not found"}), 404

            old_status = shipment["status"]
            cur.execute("""
                UPDATE shipments
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE shipment_id = %s
                RETURNING shipment_id, status, updated_at;
            """, (new_status, shipment_id))
            updated_shipment = cur.fetchone()

            cur.execute("""
                INSERT INTO shipment_events (shipment_id, event_type)
                VALUES (%s, %s)
                RETURNING event_id, shipment_id, event_type, event_time;
            """, (shipment_id, new_status))
            new_event = cur.fetchone()

        conn.commit()
        return jsonify({
            "status": "ok",
            "message": "Shipment status updated",
            "previous_status": old_status,
            "shipment": updated_shipment,
            "event": new_event,
        })
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"status": "error", "message": "Internal application error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
