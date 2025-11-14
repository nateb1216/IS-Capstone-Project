import json
import os
import datetime as dt
from google.cloud import pubsub_v1
from models import get_conn

# Hard-wired defaults to YOUR IDs; env vars still override if you set them.
PROJECT_ID = os.getenv("PROJECT_ID", "School-Supply-Orders-477323")
SUBSCRIPTION_ID = os.getenv("SUBSCRIPTION_ID", "School-Supplies")

conn = get_conn()

def record_event(payload, duplicate=False):
    conn.execute("""
      INSERT OR IGNORE INTO order_events(event_id, event_type, order_id, payload_json, published_at, received_at, is_duplicate)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        payload.get("event_id"),
        payload.get("event_type"),
        payload.get("order_id"),
        json.dumps(payload),
        payload.get("created_at"),
        dt.datetime.utcnow().isoformat()+"Z",
        1 if duplicate else 0
    ))
    if conn.total_changes == 0:
        conn.execute("UPDATE order_events SET is_duplicate=1 WHERE event_id=?", (payload.get("event_id"),))
    conn.commit()

def apply_order_created(p):
    conn.execute("""
      INSERT INTO orders(order_id, requested_by_name, requested_by_email, school, department, status, notes, created_at, last_updated)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(order_id) DO UPDATE SET
        requested_by_name=excluded.requested_by_name,
        requested_by_email=excluded.requested_by_email,
        school=excluded.school,
        department=excluded.department,
        status=excluded.status,
        notes=excluded.notes,
        last_updated=excluded.last_updated
    """, (
        p["order_id"],
        p.get("requested_by", {}).get("name"),
        p.get("requested_by", {}).get("email"),
        p.get("school"),
        p.get("department"),
        p.get("status", "NEW"),
        p.get("notes"),
        p.get("created_at"),
        dt.datetime.utcnow().isoformat()+"Z"
    ))
    conn.execute("DELETE FROM order_items WHERE order_id=?", (p["order_id"],))
    for it in p.get("items", []):
        qty = int(it.get("qty", 0))
        price = float(it.get("unit_price", 0.0))
        conn.execute("""
          INSERT INTO order_items(order_id, sku, name, qty, unit, unit_price, total)
          VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (p["order_id"], it.get("sku"), it.get("name"), qty, it.get("unit"), price, qty*price))
    conn.commit()

def handle_message(payload):
    # dedupe on event_id
    exists = conn.execute("SELECT 1 FROM order_events WHERE event_id=?", (payload.get("event_id"),)).fetchone()
    if exists:
        record_event(payload, duplicate=True)
        print(f"Duplicate event {payload.get('event_id')}")
        return

    etype = payload.get("event_type")
    if etype == "OrderCreated":
        if not payload.get("items"):
            print("Invalid OrderCreated (missing items) – will record event but not create order")
        else:
            apply_order_created(payload)
    elif etype == "OrderUpdated":
        conn.execute("UPDATE orders SET status=?, last_updated=? WHERE order_id=?",
                     (payload.get("status"), dt.datetime.utcnow().isoformat()+"Z", payload.get("order_id")))
        conn.commit()

    record_event(payload, duplicate=False)
    print(f"Processed {etype} for {payload.get('order_id')}")

def callback(message: pubsub_v1.subscriber.message.Message):
    try:
        payload = json.loads(message.data.decode("utf-8"))
    except Exception as e:
        print("JSON parse error; nacking:", e)
        message.nack()
        return

    if not payload.get("event_id") or not payload.get("order_id"):
        print("Invalid payload (missing event_id or order_id); nacking")
        message.nack()
        return

    try:
        handle_message(payload)
        message.ack()
    except Exception as e:
        print("Subscriber error; nacking:", e)
        message.nack()

if __name__ == "__main__":
    sub = pubsub_v1.SubscriberClient()
    path = sub.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)
    print("Listening on:", path)
    streaming_pull = sub.subscribe(path, callback=callback)
    try:
        streaming_pull.result()
    except KeyboardInterrupt:
        streaming_pull.cancel()
