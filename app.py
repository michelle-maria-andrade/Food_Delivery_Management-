"""
ANURODH FOOD DELIVERY SERVICES  —  Enterprise Edition
Flask backend — Oracle via python-oracledb

FIXES:
  • DBMS_LOB.SUBSTR on all food column reads (CLOB fix)
  • customer zone stored in session at register/login time
  • checkout passes acc_id correctly to stored procedure
  • /api/auth/me returns zone so frontend can restore it
  • driver_mark_delivered now checks IN ('incomplete','ready') not just 'incomplete'
  • driver_mark_failed  now checks IN ('incomplete','ready')
  • restaurant current orders shows only 'incomplete' (not 'ready' — those are handed off)
  • restaurant previous orders shows 'complete' AND 'failed'
  • new route /api/restaurant/orders/dispatched shows 'ready' orders (picked up, in transit)
"""

from flask import Flask, render_template, request, jsonify, session
import oracledb
from functools import wraps

app = Flask(__name__)
app.secret_key = "anurodh_delivery_secret_2024_xk9"

# ── Oracle connection ──────────────────────────────────────
DB_USER     = "michelle_dev"
DB_PASSWORD = "lovepucha3726"
DB_DSN      = "localhost:1521/XE"

def get_db():
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)


# ── Auth helpers ───────────────────────────────────────────
def login_required(role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if session.get("role") != role:
                return jsonify({"error": "Unauthorized"}), 401
            return f(*args, **kwargs)
        return wrapped
    return decorator


# ══════════════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


# ══════════════════════════════════════════════════════════════
#  AUTH — CUSTOMERS
# ══════════════════════════════════════════════════════════════

@app.route("/api/auth/customer/register", methods=["POST"])
def customer_register():
    d = request.json
    if not all(d.get(k) for k in ["name", "phone", "email", "address", "password"]):
        return jsonify({"error": "All fields are required"}), 400
    zone = d.get("zone", "North")
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """INSERT INTO customers (c_name, no, email, del_add, psswrd, zone)
               VALUES (:1, :2, :3, :4, :5, :6)""",
            (d["name"], int(d["phone"]), d["email"], d["address"], d["password"], zone)
        )
        con.commit()
        cur.execute("SELECT acc_id, c_name FROM customers WHERE email=:1", (d["email"],))
        row = cur.fetchone()
        session.update(role="customer", email=d["email"],
                       acc_id=row[0], name=row[1], zone=zone)
        cur.close(); con.close()
        return jsonify({"message": "Registered!", "name": row[1], "zone": zone})
    except oracledb.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/customer/login", methods=["POST"])
def customer_login():
    d = request.json
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """SELECT acc_id, c_name, NVL(zone, 'North')
               FROM   customers
               WHERE  email=:1 AND psswrd=:2""",
            (d["email"], d["password"])
        )
        row = cur.fetchone()
        cur.close(); con.close()
        if row:
            session.update(role="customer", email=d["email"],
                           acc_id=row[0], name=row[1], zone=row[2])
            return jsonify({"message": "Login successful", "name": row[1], "zone": row[2]})
        return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════════════════════════
#  AUTH — RESTAURANTS
# ══════════════════════════════════════════════════════════════

@app.route("/api/auth/restaurant/register", methods=["POST"])
def restaurant_register():
    d = request.json
    if not all(d.get(k) for k in ["name", "phone", "email", "address", "password"]):
        return jsonify({"error": "All fields are required"}), 400
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            "INSERT INTO restaurants (r_name, no, email, pick_add, psswrd) VALUES (:1,:2,:3,:4,:5)",
            (d["name"], int(d["phone"]), d["email"], d["address"], d["password"])
        )
        con.commit()
        cur.execute("SELECT r_id FROM restaurants WHERE email=:1", (d["email"],))
        row = cur.fetchone()
        session.update(role="restaurant", email=d["email"], r_id=row[0], r_name=d["name"])
        cur.close(); con.close()
        return jsonify({"message": "Registered!", "name": d["name"]})
    except oracledb.IntegrityError:
        return jsonify({"error": "Email or restaurant name already registered"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/restaurant/login", methods=["POST"])
def restaurant_login():
    d = request.json
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            "SELECT r_id, r_name FROM restaurants WHERE email=:1 AND psswrd=:2",
            (d["email"], d["password"])
        )
        row = cur.fetchone()
        cur.close(); con.close()
        if row:
            session.update(role="restaurant", email=d["email"], r_id=row[0], r_name=row[1])
            return jsonify({"message": "Login successful", "name": row[1]})
        return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════════════════════════
#  AUTH — DELIVERY PARTNERS
# ══════════════════════════════════════════════════════════════

@app.route("/api/auth/driver/register", methods=["POST"])
def driver_register():
    d = request.json
    if not all(d.get(k) for k in ["name", "phone", "email", "password"]):
        return jsonify({"error": "All fields are required"}), 400
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """INSERT INTO delivery_partners (driver_name, no, email, psswrd, zone)
               VALUES (:1, :2, :3, :4, :5)""",
            (d["name"], int(d["phone"]), d["email"], d["password"], d.get("zone", "North"))
        )
        con.commit()
        cur.execute(
            "SELECT driver_id, driver_name FROM delivery_partners WHERE email=:1", (d["email"],)
        )
        row = cur.fetchone()
        session.update(role="driver", email=d["email"], driver_id=row[0], name=row[1])
        cur.close(); con.close()
        return jsonify({"message": "Registered!", "name": row[1]})
    except oracledb.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/driver/login", methods=["POST"])
def driver_login():
    d = request.json
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            "SELECT driver_id, driver_name FROM delivery_partners WHERE email=:1 AND psswrd=:2",
            (d["email"], d["password"])
        )
        row = cur.fetchone()
        cur.close(); con.close()
        if row:
            session.update(role="driver", email=d["email"], driver_id=row[0], name=row[1])
            return jsonify({"message": "Login successful", "name": row[1]})
        return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Shared logout / me ────────────────────────────────────

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@app.route("/api/auth/me")
def me():
    if "role" not in session:
        return jsonify({"loggedIn": False})
    return jsonify({
        "loggedIn": True,
        "role":     session["role"],
        "name":     session.get("name") or session.get("r_name"),
        "email":    session["email"],
        "zone":     session.get("zone", "North"),
        "acc_id":   session.get("acc_id")
    })


# ══════════════════════════════════════════════════════════════
#  DEBUG ROUTES
# ══════════════════════════════════════════════════════════════

@app.route("/api/debug/cart")
def debug_cart():
    if session.get("role") != "customer":
        return jsonify({"error": "Must be logged in as customer"}), 401
    try:
        con = get_db(); cur = con.cursor()
        acc_id = session.get("acc_id")
        cur.execute("SELECT cart_id, item_name, quantity, price FROM cart WHERE acc_id=:1", (acc_id,))
        rows = cur.fetchall()
        cur.execute("SELECT COUNT(*) FROM cart WHERE acc_id=:1", (acc_id,))
        count = cur.fetchone()[0]
        cur.close(); con.close()
        return jsonify({
            "session_acc_id": acc_id,
            "session_name":   session.get("name"),
            "session_zone":   session.get("zone"),
            "cart_row_count": count,
            "cart_items": [
                {"cart_id": r[0], "item": r[1], "qty": r[2], "price": float(r[3])}
                for r in rows
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/debug/session")
def debug_session():
    return jsonify(dict(session))


# ══════════════════════════════════════════════════════════════
#  RESTAURANT ROUTES
# ══════════════════════════════════════════════════════════════

@app.route("/api/restaurant/menu", methods=["GET"])
@login_required("restaurant")
def get_my_menu():
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """SELECT item_id, class, item_name, description, price
               FROM   menu_items WHERE r_name=:1 ORDER BY class, item_name""",
            (session["r_name"],)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        return jsonify([{"id": r[0], "class": r[1], "name": r[2],
                         "description": r[3], "price": float(r[4])} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurant/menu", methods=["POST"])
@login_required("restaurant")
def add_menu_item():
    d = request.json
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            "INSERT INTO menu_items (r_name, class, item_name, description, price) VALUES (:1,:2,:3,:4,:5)",
            (session["r_name"], d["class"], d["name"], d.get("description", ""), float(d["price"]))
        )
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Item added"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurant/menu/<int:item_id>", methods=["PUT"])
@login_required("restaurant")
def update_menu_item(item_id):
    d = request.json
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """UPDATE menu_items SET class=:1, item_name=:2, description=:3, price=:4
               WHERE item_id=:5 AND r_name=:6""",
            (d["class"], d["name"], d.get("description", ""),
             float(d["price"]), item_id, session["r_name"])
        )
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurant/menu/<int:item_id>", methods=["DELETE"])
@login_required("restaurant")
def delete_menu_item(item_id):
    try:
        con = get_db(); cur = con.cursor()
        cur.execute("DELETE FROM menu_items WHERE item_id=:1 AND r_name=:2",
                    (item_id, session["r_name"]))
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurant/orders/current")
@login_required("restaurant")
def restaurant_current_orders():
    """
    Orders still being prepared in the kitchen — status = 'incomplete' only.
    Once the restaurant taps 'Ready for Pickup', status becomes 'ready'
    and the order moves to /dispatched — disappearing from this view.
    """
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """SELECT o.ord_id,
                      o.c_name,
                      DBMS_LOB.SUBSTR(o.food, 4000, 1),
                      o.total,
                      TO_CHAR(o.ord_date, 'DD Mon YYYY HH24:MI'),
                      dp.driver_name,
                      dp.no
               FROM   orders o
               LEFT JOIN delivery_partners dp ON dp.driver_id = o.driver_id
               WHERE  o.r_name = :1
                 AND  o.status = 'incomplete'
               ORDER  BY o.ord_date DESC""",
            (session["r_name"],)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        return jsonify([{
            "id":           r[0],
            "customer":     r[1],
            "food":         r[2] or "",
            "total":        float(r[3]),
            "date":         r[4],
            "driver":       r[5] or "Assigning\u2026",
            "driver_phone": r[6]
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurant/orders/dispatched")
@login_required("restaurant")
def restaurant_dispatched_orders():
    """
    Orders marked ready and picked up by driver — status = 'ready'.
    These are out for delivery. Restaurant can see them but can't act on them.
    """
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """SELECT o.ord_id,
                      o.c_name,
                      DBMS_LOB.SUBSTR(o.food, 4000, 1),
                      o.total,
                      TO_CHAR(o.ord_date, 'DD Mon YYYY HH24:MI'),
                      dp.driver_name,
                      dp.no
               FROM   orders o
               LEFT JOIN delivery_partners dp ON dp.driver_id = o.driver_id
               WHERE  o.r_name = :1
                 AND  o.status = 'ready'
               ORDER  BY o.ord_date DESC""",
            (session["r_name"],)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        return jsonify([{
            "id":           r[0],
            "customer":     r[1],
            "food":         r[2] or "",
            "total":        float(r[3]),
            "date":         r[4],
            "driver":       r[5] or "Unknown",
            "driver_phone": r[6]
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurant/orders/previous")
@login_required("restaurant")
def restaurant_previous_orders():
    """Completed and failed orders."""
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """SELECT ord_id,
                      c_name,
                      DBMS_LOB.SUBSTR(food, 4000, 1),
                      total,
                      status,
                      TO_CHAR(ord_date, 'DD Mon YYYY HH24:MI')
               FROM   orders
               WHERE  r_name = :1
                 AND  status IN ('complete', 'failed')
               ORDER  BY ord_date DESC""",
            (session["r_name"],)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        return jsonify([{
            "id": r[0], "customer": r[1], "food": r[2] or "",
            "total": float(r[3]), "status": r[4], "date": r[5]
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurant/orders/<int:ord_id>/complete", methods=["POST"])
@login_required("restaurant")
def mark_complete(ord_id):
    """
    Restaurant marks food as READY FOR PICKUP.
    Status goes from 'incomplete' → 'ready'.
    The order disappears from the kitchen view and appears in dispatched.
    The order only becomes 'complete' when the DRIVER marks it delivered.
    """
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            "UPDATE orders SET status='ready' WHERE ord_id=:1 AND r_name=:2 AND status='incomplete'",
            (ord_id, session["r_name"])
        )
        if cur.rowcount == 0:
            cur.close(); con.close()
            return jsonify({"error": "Order not found or already dispatched"}), 404
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Order marked ready for pickup — driver notified"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════════════════════════
#  CUSTOMER ROUTES
# ══════════════════════════════════════════════════════════════

@app.route("/api/restaurants")
def list_restaurants():
    try:
        con = get_db(); cur = con.cursor()
        cur.execute("SELECT r_name, pick_add FROM restaurants ORDER BY r_name")
        rows = cur.fetchall()
        cur.close(); con.close()
        return jsonify([{"name": r[0], "address": r[1]} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurants/<r_name>/menu")
def restaurant_menu(r_name):
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """SELECT item_id, class, item_name, description, price
               FROM   menu_items WHERE r_name=:1 ORDER BY class, item_name""",
            (r_name,)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        return jsonify([{"id": r[0], "class": r[1], "name": r[2],
                         "description": r[3], "price": float(r[4])} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── CART ──────────────────────────────────────────────────

@app.route("/api/cart")
@login_required("customer")
def get_cart():
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            "SELECT cart_id, item_id, item_name, r_name, quantity, price FROM cart WHERE acc_id=:1",
            (session["acc_id"],)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        return jsonify([{"cart_id": r[0], "item_id": r[1], "name": r[2],
                         "restaurant": r[3], "qty": r[4], "price": float(r[5])} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cart", methods=["POST"])
@login_required("customer")
def add_to_cart():
    d = request.json
    try:
        con = get_db(); cur = con.cursor()
        cur.execute("SELECT r_name FROM cart WHERE acc_id=:1 AND ROWNUM=1", (session["acc_id"],))
        row = cur.fetchone()
        if row and row[0] != d["r_name"]:
            cur.close(); con.close()
            return jsonify({"error": "cart_conflict", "existing_restaurant": row[0]}), 409
        cur.execute("SELECT cart_id, quantity FROM cart WHERE acc_id=:1 AND item_id=:2",
                    (session["acc_id"], d["item_id"]))
        existing = cur.fetchone()
        if existing:
            cur.execute("UPDATE cart SET quantity=quantity+:1 WHERE cart_id=:2",
                        (d.get("qty", 1), existing[0]))
        else:
            cur.execute(
                "INSERT INTO cart (acc_id, item_id, item_name, r_name, quantity, price) VALUES (:1,:2,:3,:4,:5,:6)",
                (session["acc_id"], d["item_id"], d["item_name"], d["r_name"],
                 d.get("qty", 1), float(d["price"]))
            )
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Added to cart"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cart/<int:cart_id>", methods=["PUT"])
@login_required("customer")
def update_cart_item(cart_id):
    d = request.json
    try:
        con = get_db(); cur = con.cursor()
        if d.get("qty", 1) < 1:
            cur.execute("DELETE FROM cart WHERE cart_id=:1 AND acc_id=:2",
                        (cart_id, session["acc_id"]))
        else:
            cur.execute("UPDATE cart SET quantity=:1 WHERE cart_id=:2 AND acc_id=:3",
                        (d["qty"], cart_id, session["acc_id"]))
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cart/<int:cart_id>", methods=["DELETE"])
@login_required("customer")
def remove_cart_item(cart_id):
    try:
        con = get_db(); cur = con.cursor()
        cur.execute("DELETE FROM cart WHERE cart_id=:1 AND acc_id=:2",
                    (cart_id, session["acc_id"]))
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Removed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cart/clear", methods=["POST"])
@login_required("customer")
def clear_cart():
    try:
        con = get_db(); cur = con.cursor()
        cur.execute("DELETE FROM cart WHERE acc_id=:1", (session["acc_id"],))
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Cart cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── CHECKOUT ──────────────────────────────────────────────

@app.route("/api/checkout", methods=["POST"])
@login_required("customer")
def checkout():
    zone   = session.get("zone") or (request.json or {}).get("zone", "North")
    acc_id = session["acc_id"]
    name   = session["name"]
    try:
        con = get_db(); cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM cart WHERE acc_id=:1", (acc_id,))
        if cur.fetchone()[0] == 0:
            cur.close(); con.close()
            return jsonify({"error": "Your cart is empty"}), 400
        v_ord_id  = cur.var(oracledb.NUMBER)
        v_driver  = cur.var(oracledb.STRING)
        v_status  = cur.var(oracledb.STRING)
        v_message = cur.var(oracledb.STRING)
        cur.callproc("place_order_and_assign",
                     [acc_id, name, zone, v_ord_id, v_driver, v_status, v_message])
        cur.close(); con.close()
        status  = v_status.getvalue()
        message = v_message.getvalue()
        if status == "SUCCESS":
            return jsonify({
                "message":  message,
                "order_id": int(v_ord_id.getvalue()),
                "driver":   v_driver.getvalue() or "Assigning\u2026",
            })
        elif status == "EMPTY_CART":
            return jsonify({"error": message}), 400
        else:
            return jsonify({"error": message or "Unknown error from stored procedure"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/customer/orders")
@login_required("customer")
def customer_orders():
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """SELECT o.ord_id,
                      o.r_name,
                      DBMS_LOB.SUBSTR(o.food, 4000, 1),
                      o.total,
                      o.status,
                      TO_CHAR(o.ord_date, 'DD Mon YYYY HH24:MI'),
                      dp.driver_name
               FROM   orders o
               LEFT JOIN delivery_partners dp ON dp.driver_id = o.driver_id
               WHERE  o.acc_id = :1
               ORDER  BY o.ord_date DESC""",
            (session["acc_id"],)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        return jsonify([{
            "id":         r[0],
            "restaurant": r[1],
            "food":       r[2] or "",
            "total":      float(r[3]),
            "status":     r[4],
            "date":       r[5],
            "driver":     r[6] or "Assigning\u2026"
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════════════════════════
#  DELIVERY PARTNER ROUTES
# ══════════════════════════════════════════════════════════════

@app.route("/api/driver/orders")
@login_required("driver")
def driver_orders():
    """
    Active orders assigned to this driver.
    Shows both 'incomplete' (being prepared) and 'ready' (pick up now).
    """
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """SELECT o.ord_id,
                      o.c_name,
                      o.r_name,
                      DBMS_LOB.SUBSTR(o.food, 4000, 1),
                      o.total,
                      o.status,
                      TO_CHAR(o.ord_date,    'DD Mon YYYY HH24:MI'),
                      TO_CHAR(o.dispatch_ts, 'DD Mon YYYY HH24:MI')
               FROM   orders o
               WHERE  o.driver_id = :1
                 AND  o.status    IN ('incomplete', 'ready')
               ORDER  BY o.dispatch_ts DESC""",
            (session["driver_id"],)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        return jsonify([{
            "id":         r[0],
            "customer":   r[1],
            "restaurant": r[2],
            "food":       r[3] or "",
            "total":      float(r[4]),
            "status":     r[5],
            "ordered":    r[6],
            "dispatched": r[7]
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/driver/orders/history")
@login_required("driver")
def driver_order_history():
    """All completed orders delivered by this driver."""
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """SELECT o.ord_id,
                      o.c_name,
                      o.r_name,
                      DBMS_LOB.SUBSTR(o.food, 4000, 1),
                      o.total,
                      TO_CHAR(o.ord_date,     'DD Mon YYYY HH24:MI'),
                      TO_CHAR(da.delivery_ts, 'DD Mon YYYY HH24:MI')
               FROM   orders o
               JOIN   dispatch_audit da ON da.ord_id    = o.ord_id
                                       AND da.driver_id = o.driver_id
               WHERE  o.driver_id = :1
                 AND  o.status    = 'complete'
               ORDER  BY da.delivery_ts DESC""",
            (session["driver_id"],)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        return jsonify([{
            "id":           r[0],
            "customer":     r[1],
            "restaurant":   r[2],
            "food":         r[3] or "",
            "total":        float(r[4]),
            "ordered":      r[5],
            "delivered_at": r[6] or "\u2014"
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/driver/orders/<int:ord_id>/delivered", methods=["POST"])
@login_required("driver")
def driver_mark_delivered(ord_id):
    """
    Driver confirms delivery.
    Checks status IN ('incomplete','ready') — not just 'incomplete'.
    Sets status = 'complete' which fires TRG_ORDER_COMPLETE:
      - driver_status → 'Available'
      - delivery_ts stamped on dispatch_audit
      - avg_delivery_min + total_deliveries updated
    """
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """SELECT ord_id FROM orders
               WHERE  ord_id    = :1
                 AND  driver_id = :2
                 AND  status    IN ('incomplete', 'ready')""",
            (ord_id, session["driver_id"])
        )
        if not cur.fetchone():
            cur.close(); con.close()
            return jsonify({"error": "Order not found or already completed"}), 404
        cur.execute(
            "UPDATE orders SET status = 'complete' WHERE ord_id = :1",
            (ord_id,)
        )
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": f"Order #{ord_id} delivered successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/driver/orders/<int:ord_id>/failed", methods=["POST"])
@login_required("driver")
def driver_mark_failed(ord_id):
    """
    Driver reports failed delivery.
    Sets status = 'failed' and manually frees the driver
    (trigger only fires for 'complete', not 'failed').
    """
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """SELECT ord_id FROM orders
               WHERE  ord_id    = :1
                 AND  driver_id = :2
                 AND  status    IN ('incomplete', 'ready')""",
            (ord_id, session["driver_id"])
        )
        if not cur.fetchone():
            cur.close(); con.close()
            return jsonify({"error": "Order not found or already completed"}), 404
        cur.execute(
            "UPDATE orders SET status = 'failed' WHERE ord_id = :1", (ord_id,)
        )
        cur.execute(
            "UPDATE delivery_partners SET driver_status = 'Available' WHERE driver_id = :1",
            (session["driver_id"],)
        )
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": f"Order #{ord_id} marked as failed. You are now available."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/driver/status", methods=["PUT"])
@login_required("driver")
def update_driver_status():
    d = request.json
    new_status = d.get("status")
    if new_status not in ("Available", "Offline"):
        return jsonify({"error": "Status must be 'Available' or 'Offline'"}), 400
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            "UPDATE delivery_partners SET driver_status=:1 WHERE driver_id=:2",
            (new_status, session["driver_id"])
        )
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": f"Status updated to {new_status}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════════════════════════
#  RESTAURANT ANALYTICS
# ══════════════════════════════════════════════════════════════

@app.route("/api/restaurant/analytics")
@login_required("restaurant")
def restaurant_analytics():
    try:
        con = get_db(); cur = con.cursor()
        cur.execute("""
            SELECT TO_CHAR(ord_date, 'DD Mon'), COUNT(ord_id), ROUND(SUM(total),2)
              FROM orders
             WHERE r_name=:1 AND ord_date >= SYSDATE-30
             GROUP BY TO_CHAR(ord_date,'DD Mon'), TRUNC(ord_date)
             ORDER BY TRUNC(ord_date)
        """, (session["r_name"],))
        daily = [{"day": r[0], "orders": r[1], "revenue": float(r[2])} for r in cur.fetchall()]

        cur.execute("""
            SELECT mi.item_name, COUNT(o.ord_id), ROUND(SUM(o.total),2)
              FROM orders o
              JOIN menu_items mi ON INSTR(o.food, mi.item_name) > 0
             WHERE o.r_name=:1 AND o.status='complete'
             GROUP BY mi.item_name ORDER BY 2 DESC FETCH FIRST 5 ROWS ONLY
        """, (session["r_name"],))
        top_items = [{"name": r[0], "count": r[1], "revenue": float(r[2])} for r in cur.fetchall()]

        cur.execute("""
            SELECT COUNT(ord_id),
                   ROUND(SUM(total),2),
                   ROUND(AVG(total),2),
                   SUM(CASE WHEN status='complete'   THEN 1 ELSE 0 END),
                   SUM(CASE WHEN status='incomplete' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN status='ready'      THEN 1 ELSE 0 END),
                   SUM(CASE WHEN status='failed'     THEN 1 ELSE 0 END)
              FROM orders WHERE r_name=:1
        """, (session["r_name"],))
        row = cur.fetchone()
        summary = {
            "total_orders":  row[0] or 0,
            "total_revenue": float(row[1] or 0),
            "avg_order":     float(row[2] or 0),
            "completed":     row[3] or 0,
            "pending":       row[4] or 0,
            "in_transit":    row[5] or 0,
            "failed":        row[6] or 0
        }

        cur.execute("""
            SELECT dp.driver_name, dp.zone, COUNT(da.audit_id), ROUND(dp.avg_delivery_min,1)
              FROM dispatch_audit da
              JOIN delivery_partners dp ON dp.driver_id = da.driver_id
              JOIN orders o             ON o.ord_id     = da.ord_id
             WHERE o.r_name=:1
             GROUP BY dp.driver_name, dp.zone, dp.avg_delivery_min
             ORDER BY 3 DESC
        """, (session["r_name"],))
        drivers = [{"name": r[0], "zone": r[1], "deliveries": r[2],
                    "avg_min": float(r[3] or 0)} for r in cur.fetchall()]

        cur.close(); con.close()
        return jsonify({"summary": summary, "daily": daily,
                        "top_items": top_items, "drivers": drivers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════════════════════════
#  GLOBAL LOGISTICS DASHBOARD
# ══════════════════════════════════════════════════════════════

@app.route("/api/dashboard")
def logistics_dashboard():
    try:
        con = get_db(); cur = con.cursor()
        cur.execute("""
            SELECT r.r_name, r.pick_add,
                   COUNT(o.ord_id), ROUND(SUM(o.total),2), ROUND(AVG(o.total),2)
              FROM restaurants r
             INNER JOIN orders o ON o.r_name=r.r_name AND o.status='complete'
             GROUP BY r.r_name, r.pick_add
            HAVING COUNT(o.ord_id) >= 1
             ORDER BY 4 DESC
        """)
        restaurants = [{"name": r[0], "address": r[1], "total_orders": r[2],
                        "total_revenue": float(r[3]), "avg_order": float(r[4])}
                       for r in cur.fetchall()]

        cur.execute("""
            SELECT dp.driver_name, dp.zone, dp.total_deliveries, dp.avg_delivery_min
              FROM delivery_partners dp
             INNER JOIN dispatch_audit da ON da.driver_id = dp.driver_id
             INNER JOIN orders o          ON o.ord_id=da.ord_id AND o.status='complete'
             GROUP BY dp.driver_name, dp.zone, dp.total_deliveries, dp.avg_delivery_min
            HAVING dp.total_deliveries >= 1
             ORDER BY dp.avg_delivery_min ASC
        """)
        drivers = [{"name": r[0], "zone": r[1], "total_deliveries": r[2],
                    "avg_delivery_min": float(r[3]) if r[3] else 0}
                   for r in cur.fetchall()]

        cur.close(); con.close()
        return jsonify({"restaurants": restaurants, "drivers": drivers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)