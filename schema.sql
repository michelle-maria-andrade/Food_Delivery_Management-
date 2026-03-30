-- ============================================================
--  ANURODH FOOD DELIVERY SERVICES — Full Schema
--  Oracle Database (tested on Oracle XE 21c)
--
--  Run this file as your schema user in SQL*Plus:
--    SQL> @anurodh_schema.sql
--
--  Order of creation:
--    1. Tables (in dependency order)
--    2. Sequences (auto-handled by GENERATED ALWAYS in XE 21c,
--       but explicit sequences included for older Oracle versions)
--    3. Indexes
--    4. Stored Procedure — place_order_and_assign
--    5. Trigger         — trg_order_complete
--    6. Sample seed data (one restaurant, one driver, one customer)
-- ============================================================


-- ============================================================
--  CLEANUP  (drop everything if re-running)
-- ============================================================

BEGIN
    FOR t IN (
        SELECT table_name FROM user_tables
        WHERE  table_name IN (
            'DISPATCH_AUDIT','ORDERS','CART',
            'MENU_ITEMS','CUSTOMERS','RESTAURANTS','DELIVERY_PARTNERS'
        )
    ) LOOP
        EXECUTE IMMEDIATE 'DROP TABLE ' || t.table_name || ' CASCADE CONSTRAINTS';
    END LOOP;
END;
/

BEGIN
    FOR p IN (
        SELECT object_name FROM user_objects
        WHERE  object_type = 'PROCEDURE'
          AND  object_name = 'PLACE_ORDER_AND_ASSIGN'
    ) LOOP
        EXECUTE IMMEDIATE 'DROP PROCEDURE ' || p.object_name;
    END LOOP;
END;
/

BEGIN
    FOR tr IN (
        SELECT trigger_name FROM user_triggers
        WHERE  trigger_name = 'TRG_ORDER_COMPLETE'
    ) LOOP
        EXECUTE IMMEDIATE 'DROP TRIGGER ' || tr.trigger_name;
    END LOOP;
END;
/


-- ============================================================
--  TABLE 1: CUSTOMERS
-- ============================================================

CREATE TABLE customers (
    acc_id   NUMBER          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    c_name   VARCHAR2(200)   NOT NULL,
    no       NUMBER(15)      NOT NULL,
    email    VARCHAR2(200)   NOT NULL UNIQUE,
    del_add  VARCHAR2(500)   NOT NULL,
    psswrd   VARCHAR2(200)   NOT NULL,
    zone     VARCHAR2(20)    DEFAULT 'North'
                             CHECK (zone IN ('North','South','East','West','Central'))
);


-- ============================================================
--  TABLE 2: RESTAURANTS
-- ============================================================

CREATE TABLE restaurants (
    r_id     NUMBER          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    r_name   VARCHAR2(200)   NOT NULL UNIQUE,
    no       NUMBER(15)      NOT NULL,
    email    VARCHAR2(200)   NOT NULL UNIQUE,
    pick_add VARCHAR2(500)   NOT NULL,
    psswrd   VARCHAR2(200)   NOT NULL
);


-- ============================================================
--  TABLE 3: DELIVERY PARTNERS
-- ============================================================

CREATE TABLE delivery_partners (
    driver_id        NUMBER        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    driver_name      VARCHAR2(200) NOT NULL,
    no               NUMBER(15)    NOT NULL,
    email            VARCHAR2(200) NOT NULL UNIQUE,
    psswrd           VARCHAR2(200) NOT NULL,
    zone             VARCHAR2(20)  DEFAULT 'North'
                                   CHECK (zone IN ('North','South','East','West','Central')),
    driver_status    VARCHAR2(20)  DEFAULT 'Available'
                                   CHECK (driver_status IN ('Available','Busy','Offline')),
    total_deliveries NUMBER(10)    DEFAULT 0,
    avg_delivery_min NUMBER(10,2)  DEFAULT 0
);


-- ============================================================
--  TABLE 4: MENU ITEMS
-- ============================================================

CREATE TABLE menu_items (
    item_id     NUMBER         GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    r_name      VARCHAR2(200)  NOT NULL,
    class       VARCHAR2(50)   NOT NULL
                               CHECK (class IN ('Appetizer','Main','Dessert','Drink')),
    item_name   VARCHAR2(200)  NOT NULL,
    description VARCHAR2(500),
    price       NUMBER(10,3)   NOT NULL CHECK (price >= 0),

    CONSTRAINT fk_menu_restaurant
        FOREIGN KEY (r_name) REFERENCES restaurants (r_name)
        ON DELETE CASCADE
);


-- ============================================================
--  TABLE 5: CART
-- ============================================================

CREATE TABLE cart (
    cart_id   NUMBER         GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    acc_id    NUMBER         NOT NULL,
    item_id   NUMBER         NOT NULL,
    item_name VARCHAR2(200)  NOT NULL,
    r_name    VARCHAR2(200)  NOT NULL,
    quantity  NUMBER(5)      DEFAULT 1 NOT NULL CHECK (quantity > 0),
    price     NUMBER(10,3)   NOT NULL CHECK (price >= 0),

    CONSTRAINT fk_cart_customer
        FOREIGN KEY (acc_id) REFERENCES customers (acc_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_cart_item
        FOREIGN KEY (item_id) REFERENCES menu_items (item_id)
        ON DELETE CASCADE
);


-- ============================================================
--  TABLE 6: ORDERS
--
--  status lifecycle:
--    'incomplete' → order placed, kitchen preparing
--    'ready'      → kitchen done, driver picking up
--    'complete'   → driver delivered to customer
--    'failed'     → driver could not deliver
-- ============================================================

CREATE TABLE orders (
    ord_id      NUMBER          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    acc_id      NUMBER          NOT NULL,
    c_name      VARCHAR2(200)   NOT NULL,
    r_name      VARCHAR2(200)   NOT NULL,
    food        CLOB            NOT NULL,
    total       NUMBER(10,2)    NOT NULL CHECK (total >= 0),
    status      VARCHAR2(20)    DEFAULT 'incomplete'
                                CHECK (status IN ('incomplete','ready','complete','failed')),
    driver_id   NUMBER,
    ord_date    DATE            DEFAULT SYSDATE,
    dispatch_ts TIMESTAMP,
    delivery_ts TIMESTAMP,

    CONSTRAINT fk_order_customer
        FOREIGN KEY (acc_id) REFERENCES customers (acc_id),

    CONSTRAINT fk_order_restaurant
        FOREIGN KEY (r_name) REFERENCES restaurants (r_name),

    CONSTRAINT fk_order_driver
        FOREIGN KEY (driver_id) REFERENCES delivery_partners (driver_id)
);


-- ============================================================
--  TABLE 7: DISPATCH AUDIT
--
--  One row per driver assignment.
--  delivery_ts is stamped by trg_order_complete when status → 'complete'.
-- ============================================================

CREATE TABLE dispatch_audit (
    audit_id    NUMBER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ord_id      NUMBER      NOT NULL,
    driver_id   NUMBER      NOT NULL,
    r_name      VARCHAR2(200),
    dispatch_ts TIMESTAMP   DEFAULT SYSTIMESTAMP,
    delivery_ts TIMESTAMP,

    CONSTRAINT fk_audit_order
        FOREIGN KEY (ord_id) REFERENCES orders (ord_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_audit_driver
        FOREIGN KEY (driver_id) REFERENCES delivery_partners (driver_id)
);


-- ============================================================
--  INDEXES  (speed up the most common lookups)
-- ============================================================

CREATE INDEX idx_cart_acc        ON cart          (acc_id);
CREATE INDEX idx_orders_acc      ON orders        (acc_id);
CREATE INDEX idx_orders_rname    ON orders        (r_name);
CREATE INDEX idx_orders_driver   ON orders        (driver_id);
CREATE INDEX idx_orders_status   ON orders        (status);
CREATE INDEX idx_audit_order     ON dispatch_audit(ord_id);
CREATE INDEX idx_audit_driver    ON dispatch_audit(driver_id);
CREATE INDEX idx_menu_rname      ON menu_items    (r_name);
CREATE INDEX idx_dp_zone_status  ON delivery_partners (zone, driver_status);


-- ============================================================
--  STORED PROCEDURE: PLACE_ORDER_AND_ASSIGN
--
--  Called by Flask /api/checkout.
--  In a single transaction:
--    1. Validates cart is not empty
--    2. Reads cart contents into food string + total
--    3. Inserts the order
--    4. Clears the cart
--    5. Finds best available driver (zone-preferred, then any)
--    6. Assigns driver, stamps dispatch_ts, logs to dispatch_audit
--    7. COMMITs everything
-- ============================================================

CREATE OR REPLACE PROCEDURE place_order_and_assign (
    p_acc_id  IN  customers.acc_id%TYPE,
    p_c_name  IN  customers.c_name%TYPE,
    p_zone    IN  VARCHAR2 DEFAULT 'North',
    p_ord_id  OUT orders.ord_id%TYPE,
    p_driver  OUT VARCHAR2,
    p_status  OUT VARCHAR2,
    p_message OUT VARCHAR2
)
AS
    -- Prefer a driver in the same zone; fall back to any available driver
    CURSOR cur_zone_driver IS
        SELECT driver_id, driver_name
          FROM delivery_partners
         WHERE driver_status = 'Available'
           AND zone          = p_zone
         ORDER BY total_deliveries ASC
           FOR UPDATE SKIP LOCKED;

    CURSOR cur_any_driver IS
        SELECT driver_id, driver_name
          FROM delivery_partners
         WHERE driver_status = 'Available'
         ORDER BY total_deliveries ASC
           FOR UPDATE SKIP LOCKED;

    CURSOR cur_cart IS
        SELECT item_name, quantity, price, r_name
          FROM cart
         WHERE acc_id = p_acc_id;

    v_driver_id   delivery_partners.driver_id%TYPE   := NULL;
    v_driver_name delivery_partners.driver_name%TYPE := 'UNASSIGNED';
    v_r_name      cart.r_name%TYPE;
    v_food        VARCHAR2(4000) := '';
    v_total       NUMBER(10,2)   := 0;
    v_sep         VARCHAR2(2)    := '';
    v_cart_count  NUMBER;

    TYPE t_cart_row IS RECORD (
        item_name cart.item_name%TYPE,
        quantity  cart.quantity%TYPE,
        price     cart.price%TYPE,
        r_name    cart.r_name%TYPE
    );
    v_row t_cart_row;
BEGIN
    -- 1. Guard: cart must not be empty
    SELECT COUNT(*) INTO v_cart_count
      FROM cart
     WHERE acc_id = p_acc_id;

    IF v_cart_count = 0 THEN
        p_status  := 'EMPTY_CART';
        p_message := 'Cannot place order: cart is empty.';
        p_driver  := 'UNASSIGNED';
        RETURN;
    END IF;

    -- 2. Build food string + total from cart BEFORE clearing it
    OPEN cur_cart;
    LOOP
        FETCH cur_cart INTO v_row;
        EXIT WHEN cur_cart%NOTFOUND;
        v_r_name := v_row.r_name;
        v_food   := v_food || v_sep || v_row.item_name || ' x' || v_row.quantity;
        v_total  := v_total + (v_row.quantity * v_row.price);
        v_sep    := ', ';
    END LOOP;
    CLOSE cur_cart;

    -- 3. Insert order
    INSERT INTO orders (acc_id, c_name, r_name, food, total, status)
    VALUES (p_acc_id, p_c_name, v_r_name, v_food, v_total, 'incomplete')
    RETURNING ord_id INTO p_ord_id;

    -- 4. Clear the cart NOW (after order is safely inserted)
    DELETE FROM cart WHERE acc_id = p_acc_id;

    -- 5. Find best driver — zone first, then any
    OPEN cur_zone_driver;
    FETCH cur_zone_driver INTO v_driver_id, v_driver_name;
    CLOSE cur_zone_driver;

    IF v_driver_id IS NULL THEN
        OPEN cur_any_driver;
        FETCH cur_any_driver INTO v_driver_id, v_driver_name;
        CLOSE cur_any_driver;
    END IF;

    -- 6. Assign driver if found
    IF v_driver_id IS NOT NULL THEN
        UPDATE delivery_partners
           SET driver_status = 'Busy'
         WHERE driver_id = v_driver_id;

        UPDATE orders
           SET driver_id   = v_driver_id,
               dispatch_ts = SYSTIMESTAMP
         WHERE ord_id = p_ord_id;

        INSERT INTO dispatch_audit (ord_id, driver_id, r_name, dispatch_ts)
        VALUES (p_ord_id, v_driver_id, v_r_name, SYSTIMESTAMP);
    END IF;

    -- 7. Commit the whole transaction
    COMMIT;

    p_driver  := v_driver_name;
    p_status  := 'SUCCESS';
    p_message := 'Order #' || p_ord_id || ' placed. Driver: ' || v_driver_name;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        p_ord_id  := NULL;
        p_driver  := 'UNASSIGNED';
        p_status  := 'ERROR';
        p_message := SQLERRM;
END place_order_and_assign;
/


-- ============================================================
--  TRIGGER: TRG_ORDER_COMPLETE
--
--  Fires AFTER UPDATE on orders when status changes to 'complete'.
--  Handles:
--    • Stamping delivery_ts on dispatch_audit
--    • Setting driver back to 'Available'
--    • Incrementing total_deliveries
--    • Recalculating avg_delivery_min (rolling average)
-- ============================================================

CREATE OR REPLACE TRIGGER trg_order_complete
AFTER UPDATE OF status ON orders
FOR EACH ROW
WHEN (NEW.status = 'complete' AND OLD.status != 'complete')
DECLARE
    v_driver_id   delivery_partners.driver_id%TYPE := :NEW.driver_id;
    v_dispatch_ts dispatch_audit.dispatch_ts%TYPE;
    v_minutes     NUMBER;
BEGIN
    -- Nothing to do if no driver was assigned
    IF v_driver_id IS NULL THEN
        RETURN;
    END IF;

    -- Stamp delivery time on audit log
    UPDATE dispatch_audit
       SET delivery_ts = SYSTIMESTAMP
     WHERE ord_id    = :NEW.ord_id
       AND driver_id = v_driver_id;

    -- Calculate delivery duration in minutes
    SELECT dispatch_ts
      INTO v_dispatch_ts
      FROM dispatch_audit
     WHERE ord_id    = :NEW.ord_id
       AND driver_id = v_driver_id
       AND ROWNUM    = 1;

    v_minutes :=   EXTRACT(DAY    FROM (SYSTIMESTAMP - v_dispatch_ts)) * 1440
                 + EXTRACT(HOUR   FROM (SYSTIMESTAMP - v_dispatch_ts)) * 60
                 + EXTRACT(MINUTE FROM (SYSTIMESTAMP - v_dispatch_ts))
                 + EXTRACT(SECOND FROM (SYSTIMESTAMP - v_dispatch_ts)) / 60;

    -- Free driver and update rolling stats
    UPDATE delivery_partners
       SET driver_status    = 'Available',
           total_deliveries = total_deliveries + 1,
           avg_delivery_min = ROUND(
               (avg_delivery_min * total_deliveries + v_minutes)
               / (total_deliveries + 1),
           2)
     WHERE driver_id = v_driver_id;

EXCEPTION
    WHEN OTHERS THEN
        -- Log error but do not block the status update
        DBMS_OUTPUT.PUT_LINE('trg_order_complete error: ' || SQLERRM);
END trg_order_complete;
/


-- ============================================================
--  SEED DATA
--  One of each: restaurant, delivery partner, customer
--  Passwords stored as plain text here for demo purposes only.
--  Use hashed passwords in any real deployment.
-- ============================================================

-- Restaurant
INSERT INTO restaurants (r_name, no, email, pick_add, psswrd)
VALUES ('KFC', 22276001, 'kfc@gmail.com', 'Al Safa St, Kuwait City', 'kfc123');

-- Delivery partner (zone: North, starts Available)
INSERT INTO delivery_partners (driver_name, no, email, psswrd, zone, driver_status)
VALUES ('Ahmed Al-Rashidi', 55001234, 'ahmed@driver.com', 'driver123', 'North', 'Available');

-- Customer (zone: North)
INSERT INTO customers (c_name, no, email, del_add, psswrd, zone)
VALUES ('Onas', 55009999, 'onas@gmail.com', 'Marina Heights, Flat 4B, North Zone, Kuwait', 'onas123', 'North');

-- Menu items for KFC
INSERT INTO menu_items (r_name, class, item_name, description, price)
VALUES ('KFC', 'Main', 'PeriPeri Chicken Burger', 'Spicy peri peri glazed chicken fillet', 1.500);

INSERT INTO menu_items (r_name, class, item_name, description, price)
VALUES ('KFC', 'Main', 'PeriPeri Fries', 'Seasoned fries with peri peri dust', 0.750);

INSERT INTO menu_items (r_name, class, item_name, description, price)
VALUES ('KFC', 'Drink', 'Pepsi', 'Chilled Pepsi 500ml', 0.250);

INSERT INTO menu_items (r_name, class, item_name, description, price)
VALUES ('KFC', 'Appetizer', 'Coleslaw', 'Creamy KFC coleslaw', 0.350);

INSERT INTO menu_items (r_name, class, item_name, description, price)
VALUES ('KFC', 'Dessert', 'Chocolate Mousse', 'Rich chocolate mousse cup', 0.500);

COMMIT;


-- ============================================================
--  VERIFY  — quick sanity check after running the script
-- ============================================================

SELECT 'customers'        AS tbl, COUNT(*) AS rows FROM customers       UNION ALL
SELECT 'restaurants'      AS tbl, COUNT(*) AS rows FROM restaurants     UNION ALL
SELECT 'delivery_partners'AS tbl, COUNT(*) AS rows FROM delivery_partners UNION ALL
SELECT 'menu_items'       AS tbl, COUNT(*) AS rows FROM menu_items      UNION ALL
SELECT 'cart'             AS tbl, COUNT(*) AS rows FROM cart             UNION ALL
SELECT 'orders'           AS tbl, COUNT(*) AS rows FROM orders           UNION ALL
SELECT 'dispatch_audit'   AS tbl, COUNT(*) AS rows FROM dispatch_audit;