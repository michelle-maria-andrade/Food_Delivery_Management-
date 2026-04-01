import os
import uuid
from flask import Flask, render_template, request, jsonify, session, send_from_directory
import oracledb
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "anurodh_delivery_secret_2024_xk9"

# ── Oracle connection 
DB_USER     = "michelle_dev"
DB_PASSWORD = "lovepucha3726"
DB_DSN      = "localhost:1521/XE"

# ── Photo upload config 
UPLOAD_FOLDER   = os.path.join(app.static_folder, "uploads", "restaurant_photos")
ALLOWED_EXTS    = {"jpg", "jpeg", "png", "webp", "gif"}
MAX_PHOTO_BYTES = 5 * 1024 * 1024   # 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)


def allowed_photo(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS


# ── Auth helpers 
def login_required(role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if session.get("role") != role:
                return jsonify({"error": "Unauthorized"}), 401
            return f(*args, **kwargs)
        return wrapped
    return decorator



@app.route("/")
def index():
    return render_template("index.html")


#  AUTH — CUSTOMERS

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

#  AUTH — RESTAURANTS

@app.route("/api/auth/restaurant/register", methods=["POST"])
def restaurant_register():
    d = request.json
    if not all(d.get(k) for k in ["name", "phone", "email", "address", "password"]):
        return jsonify({"error": "All fields are required"}), 400
    zone = d.get("zone", "North")
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            "INSERT INTO restaurants (r_name, no, email, pick_add, psswrd, zone) VALUES (:1,:2,:3,:4,:5,:6)",
            (d["name"], int(d["phone"]), d["email"], d["address"], d["password"], zone)
        )
        con.commit()
        cur.execute("SELECT r_id FROM restaurants WHERE email=:1", (d["email"],))
        row = cur.fetchone()
        session.update(role="restaurant", email=d["email"], r_id=row[0], r_name=d["name"], r_zone=zone)
        cur.close(); con.close()
        return jsonify({"message": "Registered!", "name": d["name"], "zone": zone})
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
            "SELECT r_id, r_name, NVL(zone, 'North') FROM restaurants WHERE email=:1 AND psswrd=:2",
            (d["email"], d["password"])
        )
        row = cur.fetchone()
        cur.close(); con.close()
        if row:
            session.update(role="restaurant", email=d["email"], r_id=row[0], r_name=row[1], r_zone=row[2])
            return jsonify({"message": "Login successful", "name": row[1], "zone": row[2]})
        return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#  AUTH — DELIVERY PARTNERS

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
    payload = {
        "loggedIn":  True,
        "role":      session["role"],
        "name":      session.get("name") or session.get("r_name"),
        "email":     session["email"],
        "zone":      session.get("zone") or session.get("r_zone", "North"),
        "acc_id":    session.get("acc_id"),
        "driver_id": session.get("driver_id"),
        "r_id":      session.get("r_id")
    }
    if session.get("role") == "driver" and session.get("driver_id"):
        try:
            con = get_db(); cur = con.cursor()
            cur.execute(
                "SELECT driver_status FROM delivery_partners WHERE driver_id=:1",
                (session["driver_id"],)
            )
            row = cur.fetchone()
            cur.close(); con.close()
            payload["driver_status"] = row[0] if row else "Available"
        except Exception:
            payload["driver_status"] = "Available"
    return jsonify(payload)

#  DEBUG ROUTES

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


#  RESTAURANT PHOTO ROUTES

@app.route("/api/restaurant/photo", methods=["GET"])
@login_required("restaurant")
def get_restaurant_photo():
    """Return the current photo URL for the logged-in restaurant."""
    try:
        con = get_db(); cur = con.cursor()
        cur.execute("SELECT photo_url FROM restaurants WHERE r_id=:1", (session["r_id"],))
        row = cur.fetchone()
        cur.close(); con.close()
        photo_url = row[0] if row else None
        return jsonify({"photo_url": photo_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurant/photo", methods=["POST"])
@login_required("restaurant")
def upload_restaurant_photo():
    """
    Upload / replace cover photo for the logged-in restaurant.
    Accepts multipart/form-data with field name 'photo'.
    Stores file in static/uploads/restaurant_photos/<r_id>.<ext>
    and saves the relative URL to the restaurants table.
    """
    if "photo" not in request.files:
        return jsonify({"error": "No photo file provided"}), 400

    file = request.files["photo"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not allowed_photo(file.filename):
        return jsonify({"error": "File type not allowed. Use JPG, PNG, or WebP."}), 400

    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_PHOTO_BYTES:
        return jsonify({"error": "Photo must be under 5 MB"}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    # Use restaurant id as filename so old photos are automatically overwritten
    filename   = f"{session['r_id']}.{ext}"
    save_path  = os.path.join(UPLOAD_FOLDER, filename)

    # Remove any old photo files for this restaurant 
    for old in os.listdir(UPLOAD_FOLDER):
        if old.startswith(f"{session['r_id']}.") and old != filename:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, old))
            except OSError:
                pass

    file.save(save_path)
    photo_url = f"/static/uploads/restaurant_photos/{filename}"

    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            "UPDATE restaurants SET photo_url=:1 WHERE r_id=:2",
            (photo_url, session["r_id"])
        )
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Photo uploaded", "photo_url": photo_url})
    except Exception as e:
        try:
            os.remove(save_path)
        except OSError:
            pass
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurant/photo", methods=["DELETE"])
@login_required("restaurant")
def delete_restaurant_photo():
    """Remove the restaurant's cover photo."""
    try:
        con = get_db(); cur = con.cursor()
        cur.execute("SELECT photo_url FROM restaurants WHERE r_id=:1", (session["r_id"],))
        row = cur.fetchone()
        if row and row[0]:
            rel_path  = row[0].lstrip("/")
            full_path = os.path.join(app.root_path, "static", rel_path.replace("static/", "", 1))
            try:
                if os.path.exists(full_path):
                    os.remove(full_path)
            except OSError:
                pass
        cur.execute(
            "UPDATE restaurants SET photo_url=NULL WHERE r_id=:1", (session["r_id"],)
        )
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Photo removed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#  RESTAURANT ROUTES

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
    and the order moves to /dispatched.
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
            "driver":       r[5] or "Unknown",
            "driver_phone": r[6]
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurant/orders/dispatched")
@login_required("restaurant")
def restaurant_dispatched_orders():
    """Orders marked ready and picked up by driver — status = 'ready'."""
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
    """Restaurant marks food as READY FOR PICKUP. status: incomplete → ready."""
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


#  CUSTOMER ROUTES

@app.route("/api/restaurants")
def list_restaurants():
    """Return all restaurants with cover photo, categories, avg rating, and zone."""
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """SELECT r_id, r_name, pick_add, photo_url,
                      NVL(categories, ''),
                      ratings_sum, ratings_count,
                      NVL(zone, 'North')
               FROM   restaurants
               ORDER  BY r_name"""
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        result = []
        for r in rows:
            r_sum, r_cnt = (r[5] or 0), (r[6] or 0)
            avg = round(r_sum / r_cnt, 1) if r_cnt > 0 else 0.0
            cats_raw = r[4] or ""
            result.append({
                "id":           r[0],
                "name":         r[1],
                "address":      r[2],
                "photo_url":    r[3],
                "categories":   [c for c in cats_raw.split("|") if c],
                "avg_rating":   avg,
                "rating_count": r_cnt,
                "zone":         r[7]
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── RESTAURANT CATEGORIES ──────────────────────────────────────

ALLOWED_CATEGORIES = {
    "Italian", "Mexican", "Japanese", "Chinese", "Indian", "French",
    "Thai", "Mediterranean", "American", "Vietnamese", "Korean",
    "Middle Eastern", "Fast Food", "Cafe & Bakery", "Pub & Bar",
    "Brunch", "Dessert", "Vegan", "Vegetarian", "Gluten-Free",
    "Healthy", "Seafood", "Steakhouse", "Pizza", "Burgers",
    "Halal", "Organic"
}


@app.route("/api/restaurant/categories", methods=["GET"])
@login_required("restaurant")
def get_my_categories():
    """Return the logged-in restaurant's current categories."""
    try:
        con = get_db(); cur = con.cursor()
        cur.execute("SELECT NVL(categories,'') FROM restaurants WHERE r_id=:1", (session["r_id"],))
        row = cur.fetchone()
        cur.close(); con.close()
        cats = [c for c in (row[0] if row else "").split("|") if c]
        return jsonify({"categories": cats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/restaurant/categories", methods=["PUT"])
@login_required("restaurant")
def update_my_categories():
    """Replace the logged-in restaurant's category list (pipe-delimited column)."""
    d = request.json
    cats = list(dict.fromkeys(d.get("categories", [])))   # deduplicate, preserve order
    invalid = [c for c in cats if c not in ALLOWED_CATEGORIES]
    if invalid:
        return jsonify({"error": f"Invalid categories: {invalid}"}), 400
    cat_str = "|".join(cats)
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            "UPDATE restaurants SET categories=:1 WHERE r_id=:2",
            (cat_str or None, session["r_id"])
        )
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": "Categories updated", "categories": cats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── RESTAURANT RATINGS ─────────────────────────────────────────

@app.route("/api/orders/<int:ord_id>/rate", methods=["POST"])
@login_required("customer")
def rate_order(ord_id):
    """
    Customer submits a 1-5 star rating for a completed order.
    Rating stored in orders.rating; restaurant totals updated atomically.
    """
    d = request.json
    stars = d.get("stars")
    if not isinstance(stars, int) or stars < 1 or stars > 5:
        return jsonify({"error": "stars must be an integer 1–5"}), 400
    try:
        con = get_db(); cur = con.cursor()
        # Verify order belongs to customer, is complete, and not yet rated
        cur.execute(
            """SELECT r.r_id, o.rating
               FROM   orders o
               JOIN   restaurants r ON r.r_name = o.r_name
               WHERE  o.ord_id = :1 AND o.acc_id = :2 AND o.status = 'complete'""",
            (ord_id, session["acc_id"])
        )
        row = cur.fetchone()
        if not row:
            cur.close(); con.close()
            return jsonify({"error": "Order not found, not completed, or doesn't belong to you"}), 404
        r_id, existing_rating = row[0], row[1]
        if existing_rating is not None:
            cur.close(); con.close()
            return jsonify({"error": "You have already rated this order"}), 409
        # Save rating on the order row
        cur.execute("UPDATE orders SET rating=:1 WHERE ord_id=:2", (stars, ord_id))
        # Increment restaurant rolling totals
        cur.execute(
            """UPDATE restaurants
               SET ratings_sum   = ratings_sum   + :1,
                   ratings_count = ratings_count + 1
               WHERE r_id = :2""",
            (stars, r_id)
        )
        con.commit()
        # Return updated avg
        cur.execute(
            "SELECT ratings_sum, ratings_count FROM restaurants WHERE r_id=:1", (r_id,)
        )
        tot = cur.fetchone()
        cur.close(); con.close()
        r_sum, r_cnt = (tot[0] or 0), (tot[1] or 1)
        return jsonify({
            "message":      "Rating submitted ✓",
            "avg_rating":   round(r_sum / r_cnt, 1),
            "rating_count": r_cnt
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/orders/<int:ord_id>/rating")
@login_required("customer")
def get_order_rating(ord_id):
    """Check if this order has already been rated by the customer."""
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            "SELECT rating FROM orders WHERE ord_id=:1 AND acc_id=:2",
            (ord_id, session["acc_id"])
        )
        row = cur.fetchone()
        cur.close(); con.close()
        if not row:
            return jsonify({"rated": False, "stars": None})
        return jsonify({"rated": row[0] is not None, "stars": row[0]})
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

DELIVERY_CHARGE_SAME_ZONE    = 40   # KWD — customer and restaurant in same zone
DELIVERY_CHARGE_ADJ_ZONE     = 60   # KWD — one zone apart
DELIVERY_CHARGE_FAR_ZONE     = 100   # KWD — two or more zones apart

# Zone adjacency map — defines which zones are neighbours
ZONE_ADJACENCY = {
    "North":   {"North", "West", "Central", "East"},
    "South":   {"South", "West", "Central", "East"},
    "East":    {"East", "North", "South", "Central"},
    "West":    {"West", "North", "South", "Central"},
    "Central": {"Central", "North", "South", "East", "West"},
}

def delivery_charge_for_zones(customer_zone: str, restaurant_zone: str) -> float:
    """Return the delivery fee based on how far apart the zones are."""
    if customer_zone == restaurant_zone:
        return DELIVERY_CHARGE_SAME_ZONE
    if restaurant_zone in ZONE_ADJACENCY.get(customer_zone, set()):
        return DELIVERY_CHARGE_ADJ_ZONE
    return DELIVERY_CHARGE_FAR_ZONE

def _luhn_valid(number: str) -> bool:
    """Return True if `number` (digits only, 16 chars) passes Luhn check."""
    digits = [int(d) for d in number]
    total  = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


@app.route("/api/checkout", methods=["POST"])
@login_required("customer")
def checkout():
    body    = request.json or {}
    zone    = session.get("zone") or body.get("zone", "North")
    acc_id  = session["acc_id"]
    name    = session["name"]
    pay_mode = body.get("payment", "card")   # "card" | "inperson"

    # ── Card validation (server-side) ─────────────────────────
    if pay_mode == "card":
        raw = body.get("card_number", "").replace(" ", "").replace("-", "")
        if len(raw) != 16:
            return jsonify({"error": "Card number must be exactly 16 digits"}), 400
        if not raw.isdigit():
            return jsonify({"error": "Card number must contain digits only"}), 400
        if not _luhn_valid(raw):
            return jsonify({"error": "Invalid card number — Luhn checksum failed"}), 400

    try:
        con = get_db(); cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM cart WHERE acc_id=:1", (acc_id,))
        if cur.fetchone()[0] == 0:
            cur.close(); con.close()
            return jsonify({"error": "Your cart is empty"}), 400

        # ── Determine restaurant zone from cart ───────────────
        cur.execute("SELECT r_name FROM cart WHERE acc_id=:1 AND ROWNUM=1", (acc_id,))
        cart_row = cur.fetchone()
        restaurant_zone = "North"
        if cart_row:
            cur.execute(
                "SELECT NVL(zone,'North') FROM restaurants WHERE r_name=:1", (cart_row[0],)
            )
            rz = cur.fetchone()
            if rz:
                restaurant_zone = rz[0]

        # ── Compute delivery charge based on zone distance ────
        charge = delivery_charge_for_zones(zone, restaurant_zone)

        # ── Find an available driver in the restaurant zone first,
        #    then adjacent zones. Reject the order if none found ─────────
        zones_to_try = [restaurant_zone] + [
            z for z in ["North", "South", "East", "West", "Central"]
            if z != restaurant_zone and z in ZONE_ADJACENCY.get(restaurant_zone, set())
        ]
        assigned_driver_id = None
        assigned_driver_name = None
        for try_zone in zones_to_try:
            cur.execute(
                """SELECT driver_id, driver_name FROM delivery_partners
                   WHERE zone = :1 AND driver_status = 'Available'
                   AND ROWNUM = 1""",
                (try_zone,)
            )
            drv = cur.fetchone()
            if drv:
                assigned_driver_id, assigned_driver_name = drv[0], drv[1]
                break

        if not assigned_driver_id:
            cur.close(); con.close()
            return jsonify({
                "error": "No drivers are available in your area right now. Please try again in a few minutes."
            }), 503

        v_ord_id  = cur.var(oracledb.NUMBER)
        v_driver  = cur.var(oracledb.STRING)
        v_status  = cur.var(oracledb.STRING)
        v_message = cur.var(oracledb.STRING)
        cur.callproc("place_order_and_assign",
                     [acc_id, name, zone, v_ord_id, v_driver, v_status, v_message])
        status  = v_status.getvalue()
        message = v_message.getvalue()
        if status not in ("SUCCESS",):
            cur.close(); con.close()
            if status == "EMPTY_CART":
                return jsonify({"error": message}), 400
            return jsonify({"error": message or "Unknown error from stored procedure"}), 500

        ord_id = int(v_ord_id.getvalue())

        # ── Override the stored procedure's driver pick with our
        #    restaurant-zone-based selection ────────────────────────────────
        cur.execute(
            "UPDATE orders SET driver_id=:1 WHERE ord_id=:2",
            (assigned_driver_id, ord_id)
        )
        cur.execute(
            "UPDATE delivery_partners SET driver_status='Busy' WHERE driver_id=:1",
            (assigned_driver_id,)
        )

        # ── Persist payment mode and delivery charge ────────────
        cur.execute(
            """UPDATE orders
                  SET pay_mode        = :1,
                      delivery_charge = :2
                WHERE ord_id = :3""",
            (pay_mode, charge, ord_id)
        )
        # Recalculate grand total = food total + delivery charge
        cur.execute(
            "UPDATE orders SET total = total + :1 WHERE ord_id = :2",
            (charge, ord_id)
        )
        con.commit()
        cur.close(); con.close()
        return jsonify({
            "message":          message,
            "order_id":         ord_id,
            "driver":           assigned_driver_name,
            "delivery_charge":  charge,
            "restaurant_zone":  restaurant_zone,
            "customer_zone":    zone,
        })
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
                      dp.driver_name,
                      NVL(o.pay_mode, 'card'),
                      NVL(o.delivery_charge, 0)
               FROM   orders o
               LEFT JOIN delivery_partners dp ON dp.driver_id = o.driver_id
               WHERE  o.acc_id = :1
               ORDER  BY o.ord_date DESC""",
            (session["acc_id"],)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        return jsonify([{
            "id":              r[0],
            "restaurant":      r[1],
            "food":            r[2] or "",
            "total":           float(r[3]),
            "status":          r[4],
            "date":            r[5],
            "driver":          r[6] or "Unknown",
            "pay_mode":        r[7],
            "delivery_charge": float(r[8])
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#  DELIVERY PARTNER ROUTES

@app.route("/api/driver/orders")
@login_required("driver")
def driver_orders():
    """Active orders assigned to this driver (incomplete + ready)."""
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
                      TO_CHAR(o.dispatch_ts, 'DD Mon YYYY HH24:MI'),
                      NVL(o.pay_mode, 'card'),
                      NVL(o.cash_collected, 0)
               FROM   orders o
               WHERE  o.driver_id = :1
                 AND  o.status    IN ('incomplete', 'ready')
               ORDER  BY o.dispatch_ts DESC""",
            (session["driver_id"],)
        )
        rows = cur.fetchall()
        cur.close(); con.close()
        return jsonify([{
            "id":             r[0],
            "customer":       r[1],
            "restaurant":     r[2],
            "food":           r[3] or "",
            "total":          float(r[4]),
            "status":         r[5],
            "ordered":        r[6],
            "dispatched":     r[7],
            "pay_mode":       r[8],
            "cash_collected": int(r[9])
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


@app.route("/api/driver/orders/<int:ord_id>/collect_cash", methods=["POST"])
@login_required("driver")
def driver_collect_cash(ord_id):
    """Driver confirms cash was received for an in-person payment order."""
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """SELECT ord_id, total FROM orders
               WHERE  ord_id    = :1
                 AND  driver_id = :2
                 AND  pay_mode  = 'inperson'
                 AND  status    IN ('incomplete', 'ready')""",
            (ord_id, session["driver_id"])
        )
        row = cur.fetchone()
        if not row:
            cur.close(); con.close()
            return jsonify({"error": "Order not found, not in-person payment, or already completed"}), 404
        cur.execute(
            "UPDATE orders SET cash_collected = 1 WHERE ord_id = :1", (ord_id,)
        )
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": f"Cash received for Order #{ord_id} confirmed ✓"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/driver/earnings/today")
@login_required("driver")
def driver_today_earnings():
    """Return the driver's total delivery charges earned today."""
    try:
        con = get_db(); cur = con.cursor()
        cur.execute(
            """SELECT NVL(SUM(o.delivery_charge), 0)
               FROM   orders o
               JOIN   dispatch_audit da ON da.ord_id    = o.ord_id
                                       AND da.driver_id = o.driver_id
               WHERE  o.driver_id = :1
                 AND  o.status    = 'complete'
                 AND  TRUNC(da.delivery_ts) = TRUNC(SYSDATE)""",
            (session["driver_id"],)
        )
        total = float(cur.fetchone()[0])
        cur.close(); con.close()
        return jsonify({"today_earnings": round(total, 3)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/driver/orders/<int:ord_id>/delivered", methods=["POST"])
@login_required("driver")
def driver_mark_delivered(ord_id):
    """Driver confirms delivery — marks order complete and frees the driver."""
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
            "UPDATE orders SET status = 'complete' WHERE ord_id = :1", (ord_id,)
        )
        # Free the driver regardless of whether the DB trigger fires
        cur.execute(
            "UPDATE delivery_partners SET driver_status = 'Available' WHERE driver_id = :1",
            (session["driver_id"],)
        )
        # Fetch r_name for the audit row (required NOT NULL column)
        cur.execute("SELECT r_name FROM orders WHERE ord_id = :1", (ord_id,))
        r_name_row = cur.fetchone()
        r_name = r_name_row[0] if r_name_row else None

        # Ensure a dispatch_audit row exists so earnings queries pick up this delivery.
        # Use MERGE so we don't duplicate if a DB trigger already inserted one.
        cur.execute(
            """MERGE INTO dispatch_audit da
               USING (SELECT :1 AS ord_id, :2 AS driver_id FROM dual) src
               ON (da.ord_id = src.ord_id AND da.driver_id = src.driver_id)
               WHEN NOT MATCHED THEN
                 INSERT (ord_id, driver_id, r_name, delivery_ts)
                 VALUES (:3, :4, :5, SYSTIMESTAMP)""",
            (ord_id, session["driver_id"], ord_id, session["driver_id"], r_name)
        )
        # Recalculate and persist total_deliveries + avg_delivery_min on the driver row.
        # avg is computed from dispatch_audit so it stays accurate even if a DB trigger
        # already inserted the row above.
        cur.execute(
            """UPDATE delivery_partners dp
               SET dp.total_deliveries = (
                       SELECT COUNT(*)
                         FROM dispatch_audit da
                        WHERE da.driver_id = dp.driver_id
                          AND da.delivery_ts IS NOT NULL
                   ),
                   dp.avg_delivery_min = (
                       SELECT ROUND(AVG(
                                  EXTRACT(DAY    FROM (da.delivery_ts - CAST(o.ord_date AS TIMESTAMP))) * 1440 +
                                  EXTRACT(HOUR   FROM (da.delivery_ts - CAST(o.ord_date AS TIMESTAMP))) * 60 +
                                  EXTRACT(MINUTE FROM (da.delivery_ts - CAST(o.ord_date AS TIMESTAMP))) +
                                  EXTRACT(SECOND FROM (da.delivery_ts - CAST(o.ord_date AS TIMESTAMP))) / 60
                              ), 1)
                         FROM dispatch_audit da
                         JOIN orders o ON o.ord_id = da.ord_id
                        WHERE da.driver_id = dp.driver_id
                          AND da.delivery_ts IS NOT NULL
                          AND o.ord_date IS NOT NULL
                   )
             WHERE dp.driver_id = :1""",
            (session["driver_id"],)
        )
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": f"Order #{ord_id} delivered successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/driver/orders/<int:ord_id>/failed", methods=["POST"])
@login_required("driver")
def driver_mark_failed(ord_id):
    """Driver reports failed delivery — frees driver manually."""
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
        # Prevent going Offline while holding an active order
        if new_status == "Offline":
            cur.execute(
                """SELECT COUNT(*) FROM orders
                   WHERE driver_id = :1 AND status IN ('incomplete', 'ready')""",
                (session["driver_id"],)
            )
            if cur.fetchone()[0] > 0:
                cur.close(); con.close()
                return jsonify({
                    "error": "You have an active delivery. Complete or mark it as failed before going offline."
                }), 409
        cur.execute(
            "UPDATE delivery_partners SET driver_status=:1 WHERE driver_id=:2",
            (new_status, session["driver_id"])
        )
        con.commit()
        cur.close(); con.close()
        return jsonify({"message": f"Status updated to {new_status}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/admin/repair_unassigned", methods=["POST"])
def repair_unassigned_orders():
    """
    Finds every active order (incomplete/ready) with no driver assigned
    and attempts to assign an Available driver from the restaurant's zone
    (falling back to adjacent zones). Safe to call repeatedly — skips
    orders that genuinely have no driver available right now.
    Returns a summary of what was fixed and what is still unassigned.
    """
    try:
        con = get_db(); cur = con.cursor()

        # Fetch all active unassigned orders with their restaurant zone
        cur.execute("""
            SELECT o.ord_id, o.r_name, NVL(r.zone, 'North')
              FROM orders o
              JOIN restaurants r ON r.r_name = o.r_name
             WHERE o.driver_id IS NULL
               AND o.status IN ('incomplete', 'ready')
             ORDER BY o.ord_date ASC
        """)
        unassigned = cur.fetchall()

        fixed = []
        still_unassigned = []

        for ord_id, r_name, restaurant_zone in unassigned:
            zones_to_try = [restaurant_zone] + [
                z for z in ["North", "South", "East", "West", "Central"]
                if z != restaurant_zone and z in ZONE_ADJACENCY.get(restaurant_zone, set())
            ]
            assigned_driver_id = None
            assigned_driver_name = None
            for try_zone in zones_to_try:
                cur.execute(
                    """SELECT driver_id, driver_name FROM delivery_partners
                       WHERE zone = :1 AND driver_status = 'Available'
                       AND ROWNUM = 1""",
                    (try_zone,)
                )
                drv = cur.fetchone()
                if drv:
                    assigned_driver_id, assigned_driver_name = drv[0], drv[1]
                    break

            if assigned_driver_id:
                cur.execute(
                    "UPDATE orders SET driver_id = :1 WHERE ord_id = :2",
                    (assigned_driver_id, ord_id)
                )
                cur.execute(
                    "UPDATE delivery_partners SET driver_status = 'Busy' WHERE driver_id = :1",
                    (assigned_driver_id,)
                )
                fixed.append({"order_id": ord_id, "restaurant": r_name,
                               "driver": assigned_driver_name, "zone": restaurant_zone})
            else:
                still_unassigned.append({"order_id": ord_id, "restaurant": r_name,
                                          "zone": restaurant_zone})

        con.commit()
        cur.close(); con.close()
        return jsonify({
            "fixed":            fixed,
            "still_unassigned": still_unassigned,
            "fixed_count":      len(fixed),
            "unassigned_count": len(still_unassigned)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#  RESTAURANT ANALYTICS

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

#  GLOBAL LOGISTICS DASHBOARD

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


# ── MAP PNG BACKGROUND ────────────────────────────────────────

MAP_PNG_PATH = os.path.join(app.static_folder, "uploads", "map_bg.png")

@app.route("/api/admin/map", methods=["POST"])
def upload_map_png():
    """Upload a custom PNG to use as the zone-map background."""
    if "map" not in request.files:
        return jsonify({"error": "No file provided (field: map)"}), 400
    f = request.files["map"]
    if not f.filename.lower().endswith(".png"):
        return jsonify({"error": "Only PNG files are accepted"}), 400
    os.makedirs(os.path.dirname(MAP_PNG_PATH), exist_ok=True)
    f.save(MAP_PNG_PATH)
    return jsonify({"message": "Map updated", "url": "/static/uploads/map_bg.png"})


@app.route("/api/admin/map", methods=["GET"])
def get_map_png():
    """Return the URL of the current custom map PNG, or null."""
    exists = os.path.isfile(MAP_PNG_PATH)
    return jsonify({"url": "/static/uploads/map_bg.png" if exists else None})


if __name__ == "__main__":
    app.run(debug=True, port=5000)