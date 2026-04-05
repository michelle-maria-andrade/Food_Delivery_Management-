# Anurodh Food Delivery System
### Oracle SQL*Plus + Flask + Web GUI

---

## Project Structure

```
anurodh/
├── app.py              ← Flask backend (all API routes)
├── schema.sql          ← Oracle DDL — run this first
├── requirements.txt    ← Python dependencies
├── templates/
│   └── index.html      ← Full SPA frontend (HTML/CSS/JS)
└── README.md
```

---

## Setup Instructions

### Step 1 — Run the Oracle Schema

Open SQL*Plus and connect:
```
sqlplus your_username/your_password@localhost/XEPDB1
```

Then run:
```sql
@schema.sql
```

This creates the tables:
- `customers`
- `restaurants`
- `menu_items`  ← replaces the old per-restaurant tables (e.g. `mcdonalds_menu`)
- `cart`
- `orders`

> ⚠️  **Key change from old schema:** The old system created a separate table for each restaurant's menu (e.g. `KFC_menu`). The new system uses a single unified `menu_items` table with an `r_name` column — much cleaner for Oracle.

---

### Step 2 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

You need:
- `flask` — web framework
- `oracledb` — Oracle's official Python driver (replaces `cx_Oracle`, no Oracle Client required for Thin mode)

---

### Step 3 — Configure Your Database

Open `app.py` and edit lines 18–20:

```python
DB_USER     = "your_username"      # your Oracle username
DB_PASSWORD = "your_password"      # your Oracle password
DB_DSN      = "localhost/XE"   # your DSN or connection string
```

Common DSN formats:
- `localhost/XEPDB1`           — Oracle XE (local)
- `localhost:1521/ORCL`        — Oracle Standard
- `myserver.example.com/PROD`  — Remote server

---

### Step 4 — Run the App

```bash
python app.py
```

Then open your browser and go to:
```
http://localhost:5000
```

---

## What Changed From Your Original Code

| Old (MySQL / CLI)            | New (Oracle / Web GUI)               |
|-----------------------------|--------------------------------------|
| `mysql.connector`           | `oracledb` (Oracle thin driver)      |
| Per-restaurant menu tables  | Single `menu_items` table with `r_name` |
| `auto_increment`            | `GENERATED ALWAYS AS IDENTITY` (Oracle) |
| Terminal menus with `input()`| React-style SPA in the browser       |
| `prettytable`               | HTML tables with live sorting        |
| Global variables for state  | Flask sessions + REST API            |
| SQL f-string injection risk | Parameterized queries (`:1,:2,...`)  |

---

## Features

**Customers:**
- Register / Login
- Browse all restaurants
- View restaurant menus (grouped by category)
- Add to cart (with conflict detection if switching restaurants)
- Edit cart (change quantities, remove items)
- Checkout with Credit/Debit/In-Person payment
- View order history

**Restaurants:**
- Register / Login
- Dashboard with live stats (active orders, revenue)
- View & mark active orders as complete
- Full menu management (Add / Edit / Delete items)
- View completed order history

---

## Notes

- Passwords are stored as plaintext to match your original system. For production, hash them with `bcrypt`.
- The `oracledb` driver in Thin mode does **not** require Oracle Instant Client to be installed.
- If you're using Oracle 11g or older, replace `GENERATED ALWAYS AS IDENTITY` with sequences + triggers.
