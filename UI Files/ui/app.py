"""
Flask UI:
- /publisher : simple form to create and publish orders (calls publisher code or direct Pub/Sub)
- /orders : list of orders with filters and duplicate badges
- /orders/<order_id> : order detail with items and event history
"""

from flask import Flask, render_template, request, redirect, url_for
import sqlite3, json, os, datetime as dt
from pathlib import Path
# optional direct publish using publisher module if runner wants; otherwise use publisher UI to call gcloud or CLI
# from publisher.publisher import publish_event

app = Flask(__name__)
DB_PATH = "../subscriber/db.sqlite3" if Path("../subscriber/db.sqlite3").exists() else "../subscriber/db.sqlite3"

def query(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

@app.route("/publisher", methods=["GET","POST"])
def publisher_page():
    if request.method == "POST":
        # collect form values
        order_id = request.form.get("order_id") or f"ORD-{int(dt.datetime.utcnow().timestamp())}"
        requester_name = request.form.get("requested_by_name")
        requester_email = request.form.get("requested_by_email")
        school = request.form.get("school")
        department = request.form.get("department")
        notes = request.form.get("notes")
        # items: simple textarea with JSON (for demo) or simple CSV
        items_text = request.form.get("items_json")
        try:
            items = json.loads(items_text)
        except:
            items = []
        event = {
            "order_id": order_id,
            "requested_by": {"name": requester_name, "email": requester_email},
            "school": school,
            "department": department,
            "items": items,
            "notes": notes,
            "status": "NEW"
        }
        # try publishing locally by calling publisher script (optional)
        # publish_event(event)  # uncomment if publisher module available in path
        # fallback: save event to DB for demo (simulate received pubsub)
        conn = sqlite3.connect("../subscriber/db.sqlite3")
        conn.execute("INSERT OR IGNORE INTO order_events(event_id, event_type, order_id, payload_json, published_at, received_at, is_duplicate) VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (str(int(dt.datetime.utcnow().timestamp()*1000)), "OrderCreated", order_id, json.dumps(event), dt.datetime.utcnow().isoformat()+"Z", dt.datetime.utcnow().isoformat()+"Z", 0))
        conn.commit()
        conn.close()
        return redirect(url_for("list_orders"))
    return render_template("publisher.html")

@app.route("/orders")
def list_orders():
    status = request.args.get("status")
    q = request.args.get("q")
    where = []
    params = []
    if status:
        where.append("status = ?")
        params.append(status)
    if q:
        where.append("(order_id LIKE ? OR requested_by_name LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%"])
    where_sql = " WHERE " + " AND ".join(where) if where else ""
    sql = f"SELECT order_id, requested_by_name, requested_by_email, school, department, status, created_at, last_updated FROM orders {where_sql} ORDER BY created_at DESC"
    rows = query(sql, params)
    return render_template("orders.html", rows=rows)

@app.route("/orders/<order_id>")
def show_order(order_id):
    order_rows = query("SELECT * FROM orders WHERE order_id=?", (order_id,))
    if not order_rows:
        return "Order not found", 404
    order = order_rows[0]
    items = query("SELECT * FROM order_items WHERE order_id=?", (order_id,))
    events = query("SELECT * FROM order_events WHERE order_id=? ORDER BY received_at DESC", (order_id,))
    return render_template("order_detail.html", order=order, items=items, events=events)

if __name__ == "__main__":
    app.run(debug=True)
