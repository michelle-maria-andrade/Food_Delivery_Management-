"""
ANURODH FOOD DELIVERY SERVICES
Flask backend — Oracle SQL*Plus via cx_Oracle (oracledb)
"""

from flask import Flask, render_template, request, jsonify, session
import oracledb
import os
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ── Oracle connection config ───────────────────────────────
# Edit these to match your Oracle instance
DB_USER     = "michelle_dev"
DB_PASSWORD = "lovepucha3726"
DB_DSN      = "localhost:1521/XE"   # e.g. "localhost:1521/ORCL" or TNS alias

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
#  AUTH ROUTES
# ══════════════════════════════════════════════════════════════

@app.route("/api/auth/customer/register", methods=["POST"])
def customer_register():
    d = request.json
    required = ["name", "phone", "email", "address", "password"]
    if not all(d.get(k) for k in required):
        return jsonify({"error": "All fields are required"}), 400
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO customers (c_name, no, email, del_add, psswrd) VALUES (:1,:2,:3,:4,:5)",
            (d["name"], int(d["phone"]), d["email"], d["address"], d["password"])
        )
        con.commit()
        # fetch new acc_id
        cur.execute("SELECT acc_id, c_name FROM customers WHERE email=:1", (d["email"],))
        row = cur.fetchone()
        session["role"]   = "customer"
        session["email"]  = d["email"]
        session["acc_id"] = row[0]
        session["name"]   = row[1]
        cur.close(); con.close()
        return jsonify({"message": "Registered!", "name": row[1]})
    except oracledb.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/customer/login", methods=["POST"])
def customer_login():
    d = request.json
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT acc_id, c_name FROM customers WHERE email=:1 AND psswrd=:2",
            (d["email"], d["password"])
        )
        row = cur.fetchone()
        cur.close(); con.close()
        if row:
            session["role"]   = "customer"
            session["email"]  = d["email"]
            session["acc_id"] = row[0]
            session["name"]   = row[1]
            return jsonify({"message": "Login successful", "name": row[1]})
        return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/restaurant/register", methods=["POST"])
def restaurant_register():
    d = request.json
    required = ["name", "phone", "email", "address", "password"]
    if not all(d.get(k) for k in required):
        return jsonify({"error": "All fields are required"}), 400
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO restaurants (r_name, no, email, pick_add, psswrd) VALUES (:1,:2,:3,:4,:5)",
            (d["name"], int(d["phone"]), d["email"], d["address"], d["password"])
        )
        con.commit()
        cur.execute("SELECT r_id FROM restaurants WHERE email=:1", (d["email"],))
        row = cur.fetchone()
        session["role"]    = "restaurant"
        session["email"]   = d["email"]
        session["r_id"]    = row[0]
        session["r_name"]  = d["name"]
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
        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT r_id, r_name FROM restaurants WHERE email=:1 AND psswrd=:2",
            (d["email"], d["password"])
        )
        row = cur.fetchone()
        cur.close(); con.close()
        if row:
            session["role"]   = "restaurant"
            session["email"]  = d["email"]
            session["r_id"]   = row[0]
            session["r_name"] = row[1]
            return jsonify({"message": "Login successful", "name": row[1]})
        return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        "role":  session["role"],
        "name":  session.get("name") or session.get("r_name"),
        "email": session["email"]
    })


# ══════════════════════════════════════════════════════════════
#  RESTAURANT ROUTES
# ══════════════════════════════════════════════════════════════

@app.route("/api/restaurant/menu", methods=["GET"])
@login_required("restaurant")
def get_my_menu():
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT item_id, class, item_name, description, price FROM menu_items WHERE r_name=:1 ORDER BY class, item_name",
            (session["r_name"],)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        items = [{"id":r[0],"class":r[1],"name":r[2],"description":r[3],"price":float(r[4])} for r in rows]
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurant/menu", methods=["POST"])
@login_required("restaurant")
def add_menu_item():
    d = request.json
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO menu_items (r_name, class, item_name, description, price) VALUES (:1,:2,:3,:4,:5)",
            (session["r_name"], d["class"], d["name"], d.get("description",""), float(d["price"]))
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
        con = get_db()
        cur = con.cursor()
        cur.execute(
            """UPDATE menu_items SET class=:1, item_name=:2, description=:3, price=:4
               WHERE item_id=:5 AND r_name=:6""",
            (d["class"], d["name"], d.get("description",""), float(d["price"]), item_id, session["r_name"])
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
        con = get_db()
        cur = con.cursor()
        cur.execute("DELETE FROM menu_items WHERE item_id=:1 AND r_name=:2", (item_id, session["r_name"]))
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurant/orders/current")
@login_required("restaurant")
def restaurant_current_orders():
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT ord_id, c_name, food, total, TO_CHAR(ord_date,'DD Mon YYYY HH24:MI') FROM orders WHERE r_name=:1 AND status='incomplete' ORDER BY ord_date DESC",
            (session["r_name"],)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        orders = [{"id":r[0],"customer":r[1],"food":r[2],"total":float(r[3]),"date":r[4]} for r in rows]
        return jsonify(orders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurant/orders/previous")
@login_required("restaurant")
def restaurant_previous_orders():
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT ord_id, c_name, food, total, TO_CHAR(ord_date,'DD Mon YYYY HH24:MI') FROM orders WHERE r_name=:1 AND status='complete' ORDER BY ord_date DESC",
            (session["r_name"],)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        orders = [{"id":r[0],"customer":r[1],"food":r[2],"total":float(r[3]),"date":r[4]} for r in rows]
        return jsonify(orders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurant/orders/<int:ord_id>/complete", methods=["POST"])
@login_required("restaurant")
def mark_complete(ord_id):
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute("UPDATE orders SET status='complete' WHERE ord_id=:1 AND r_name=:2", (ord_id, session["r_name"]))
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Marked complete"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════════════════════════
#  CUSTOMER ROUTES
# ══════════════════════════════════════════════════════════════

@app.route("/api/restaurants")
def list_restaurants():
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT r_name, pick_add FROM restaurants ORDER BY r_name")
        rows = cur.fetchall()
        cur.close(); con.close()
        return jsonify([{"name": r[0], "address": r[1]} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurants/<r_name>/menu")
def restaurant_menu(r_name):
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT item_id, class, item_name, description, price FROM menu_items WHERE r_name=:1 ORDER BY class, item_name",
            (r_name,)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        return jsonify([{"id":r[0],"class":r[1],"name":r[2],"description":r[3],"price":float(r[4])} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── CART ──────────────────────────────────────────────────

@app.route("/api/cart")
@login_required("customer")
def get_cart():
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT cart_id, item_id, item_name, r_name, quantity, price FROM cart WHERE acc_id=:1",
            (session["acc_id"],)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        return jsonify([{"cart_id":r[0],"item_id":r[1],"name":r[2],"restaurant":r[3],"qty":r[4],"price":float(r[5])} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cart", methods=["POST"])
@login_required("customer")
def add_to_cart():
    d = request.json
    try:
        con = get_db()
        cur = con.cursor()
        # Check if same restaurant
        cur.execute("SELECT r_name FROM cart WHERE acc_id=:1 AND ROWNUM=1", (session["acc_id"],))
        row = cur.fetchone()
        if row and row[0] != d["r_name"]:
            cur.close(); con.close()
            return jsonify({"error": "cart_conflict", "existing_restaurant": row[0]}), 409

        # Upsert: if item already in cart, increment
        cur.execute("SELECT cart_id, quantity FROM cart WHERE acc_id=:1 AND item_id=:2", (session["acc_id"], d["item_id"]))
        existing = cur.fetchone()
        if existing:
            cur.execute("UPDATE cart SET quantity=quantity+:1 WHERE cart_id=:2", (d.get("qty",1), existing[0]))
        else:
            cur.execute(
                "INSERT INTO cart (acc_id,item_id,item_name,r_name,quantity,price) VALUES (:1,:2,:3,:4,:5,:6)",
                (session["acc_id"], d["item_id"], d["item_name"], d["r_name"], d.get("qty",1), float(d["price"]))
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
        con = get_db()
        cur = con.cursor()
        if d.get("qty", 1) < 1:
            cur.execute("DELETE FROM cart WHERE cart_id=:1 AND acc_id=:2", (cart_id, session["acc_id"]))
        else:
            cur.execute("UPDATE cart SET quantity=:1 WHERE cart_id=:2 AND acc_id=:3", (d["qty"], cart_id, session["acc_id"]))
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cart/<int:cart_id>", methods=["DELETE"])
@login_required("customer")
def remove_cart_item(cart_id):
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute("DELETE FROM cart WHERE cart_id=:1 AND acc_id=:2", (cart_id, session["acc_id"]))
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Removed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cart/clear", methods=["POST"])
@login_required("customer")
def clear_cart():
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute("DELETE FROM cart WHERE acc_id=:1", (session["acc_id"],))
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Cart cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── CHECKOUT / ORDERS ─────────────────────────────────────

@app.route("/api/checkout", methods=["POST"])
@login_required("customer")
def checkout():
    d = request.json
    try:
        con = get_db()
        cur = con.cursor()
        # Fetch cart items
        cur.execute(
            "SELECT item_name, r_name, quantity, price FROM cart WHERE acc_id=:1",
            (session["acc_id"],)
        )
        items = cur.fetchall()
        if not items:
            return jsonify({"error": "Cart is empty"}), 400

        r_name = items[0][1]
        food_str = ", ".join([f"{i[0]} x{i[2]}" for i in items])
        total    = sum(i[2] * i[3] for i in items)

        cur.execute(
            "INSERT INTO orders (acc_id,c_name,r_name,food,total) VALUES (:1,:2,:3,:4,:5)",
            (session["acc_id"], session["name"], r_name, food_str, total)
        )
        cur.execute("DELETE FROM cart WHERE acc_id=:1", (session["acc_id"],))
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Order placed!", "total": float(total), "restaurant": r_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/customer/orders")
@login_required("customer")
def customer_orders():
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT ord_id, r_name, food, total, status, TO_CHAR(ord_date,'DD Mon YYYY HH24:MI') FROM orders WHERE acc_id=:1 ORDER BY ord_date DESC",
            (session["acc_id"],)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        orders = [{"id":r[0],"restaurant":r[1],"food":r[2],"total":float(r[3]),"status":r[4],"date":r[5]} for r in rows]
        return jsonify(orders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
