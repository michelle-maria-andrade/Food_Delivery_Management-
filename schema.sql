-- ============================================================
--  ANURODH DELIVERY SERVICES - Oracle SQL*Plus Schema
--  Run this in SQL*Plus before starting the app
-- ============================================================

-- Drop existing tables (order matters due to FK constraints)
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE orders CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE cart CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE customers CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE restaurants CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- ── CUSTOMERS ──────────────────────────────────────────────
CREATE TABLE customers (
    acc_id    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    c_name    VARCHAR2(100)  NOT NULL,
    no        NUMBER(15)     NOT NULL,
    email     VARCHAR2(150)  NOT NULL UNIQUE,
    del_add   VARCHAR2(255)  NOT NULL,
    psswrd    VARCHAR2(255)  NOT NULL
);

-- ── RESTAURANTS ────────────────────────────────────────────
CREATE TABLE restaurants (
    r_id      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    r_name    VARCHAR2(100)  NOT NULL UNIQUE,
    no        NUMBER(15)     NOT NULL,
    email     VARCHAR2(150)  NOT NULL UNIQUE,
    pick_add  VARCHAR2(255)  NOT NULL,
    psswrd    VARCHAR2(255)  NOT NULL
);

-- ── MENU ITEMS (single unified table, keyed by restaurant) ─
CREATE TABLE menu_items (
    item_id     NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    r_name      VARCHAR2(100)  NOT NULL,
    class       VARCHAR2(20)   NOT NULL,   -- Appetizer/Main/Dessert/Drink
    item_name   VARCHAR2(100)  NOT NULL,
    description VARCHAR2(255),
    price       NUMBER(8,2)    NOT NULL,
    CONSTRAINT fk_menu_rest FOREIGN KEY (r_name)
        REFERENCES restaurants(r_name) ON DELETE CASCADE
);

-- ── CART (session-scoped via customer email) ───────────────
CREATE TABLE cart (
    cart_id    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    acc_id     NUMBER         NOT NULL,
    item_id    NUMBER         NOT NULL,
    item_name  VARCHAR2(100)  NOT NULL,
    r_name     VARCHAR2(100)  NOT NULL,
    quantity   NUMBER         NOT NULL,
    price      NUMBER(8,2)    NOT NULL,
    CONSTRAINT fk_cart_cust FOREIGN KEY (acc_id)
        REFERENCES customers(acc_id) ON DELETE CASCADE,
    CONSTRAINT fk_cart_item FOREIGN KEY (item_id)
        REFERENCES menu_items(item_id) ON DELETE CASCADE
);

-- ── ORDERS ─────────────────────────────────────────────────
CREATE TABLE orders (
    ord_id     NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    acc_id     NUMBER         NOT NULL,
    c_name     VARCHAR2(100)  NOT NULL,
    r_name     VARCHAR2(100)  NOT NULL,
    food       CLOB           NOT NULL,
    total      NUMBER(10,2)   NOT NULL,
    status     VARCHAR2(20)   DEFAULT 'incomplete',
    ord_date   DATE           DEFAULT SYSDATE,
    CONSTRAINT fk_ord_cust FOREIGN KEY (acc_id)
        REFERENCES customers(acc_id) ON DELETE CASCADE
);

-- ── SEQUENCES (for display purposes) ──────────────────────
-- Oracle IDENTITY columns handle auto-increment above

COMMIT;

PROMPT Schema created successfully.
