import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "troque-esta-chave-no-render")

DB_PATH = os.environ.get("DB_PATH", "oferta_play.db")
WHATSAPP = os.environ.get("WHATSAPP_NUMBER", "")  # Ex.: 5598999999999
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "troque-a-senha")

DEFAULT_PRODUCTS = [
    ("Canva Pro", "Acesso Canva Pro por 30 dias", 5.00, "🎨"),
    ("GPT Go", "Acesso ao GPT Go", 10.00, "🤖"),
    ("Netflix Premium", "Tela Netflix Premium", 12.00, "🎬"),
    ("Disney+", "Tela Disney+", 7.00, "🏰"),
]

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        icon TEXT DEFAULT '🛍️',
        active INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        total REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        whatsapp_message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id)
    );
    """)
    if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO products(name,description,price,icon) VALUES(?,?,?,?)",
            DEFAULT_PRODUCTS
        )
    conn.commit()
    conn.close()

init_db()

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    conn = db()
    products = conn.execute(
        "SELECT * FROM products WHERE active=1 ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template("index.html", products=products)

@app.route("/api/products")
def api_products():
    conn = db()
    products = [dict(x) for x in conn.execute(
        "SELECT * FROM products WHERE active=1 ORDER BY id DESC"
    ).fetchall()]
    conn.close()
    return jsonify(products)

@app.post("/api/orders")
def create_order():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    items = data.get("items") or []
    if not name or not phone or not items:
        return jsonify({"error": "Informe nome, telefone e produtos."}), 400

    conn = db()
    total = 0
    normalized = []
    for item in items:
        try:
            pid, qty = int(item["id"]), max(1, int(item["quantity"]))
        except Exception:
            conn.close()
            return jsonify({"error": "Carrinho inválido."}), 400
        p = conn.execute("SELECT * FROM products WHERE id=? AND active=1", (pid,)).fetchone()
        if not p:
            conn.close()
            return jsonify({"error": "Produto não encontrado."}), 400
        total += p["price"] * qty
        normalized.append((p, qty))

    lines = [f"Olá! Quero fazer um pedido na Oferta Play.", f"Cliente: {name}", f"Telefone: {phone}", ""]
    for p, qty in normalized:
        lines.append(f"- {p['name']} x{qty}: R$ {p['price']*qty:.2f}".replace(".", ","))
    lines += ["", f"Total: R$ {total:.2f}".replace(".", ",")]

    cur = conn.execute(
        "INSERT INTO orders(customer_name,customer_phone,total,status,whatsapp_message) VALUES(?,?,?,?,?)",
        (name, phone, total, "pending", "\n".join(lines))
    )
    oid = cur.lastrowid
    for p, qty in normalized:
        conn.execute(
            "INSERT INTO order_items(order_id,product_id,product_name,price,quantity) VALUES(?,?,?,?,?)",
            (oid, p["id"], p["name"], p["price"], qty)
        )
    conn.commit()
    conn.close()

    import urllib.parse
    msg = urllib.parse.quote("\n".join(lines))
    wa_url = f"https://wa.me/{WHATSAPP}?text={msg}" if WHATSAPP else ""
    return jsonify({"order_id": oid, "total": total, "whatsapp_url": wa_url})

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("username") == ADMIN_USER and request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Usuário ou senha inválidos.")
    return render_template("login.html")

@app.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

@app.route("/admin", methods=["GET"])
@admin_required
def admin_dashboard():
    conn = db()
    products = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 100").fetchall()
    sales = conn.execute("SELECT COALESCE(SUM(total),0) FROM orders WHERE status IN ('paid','completed')").fetchone()[0]
    conn.close()
    return render_template("admin.html", products=products, orders=orders, sales=sales)

@app.post("/admin/products")
@admin_required
def admin_add_product():
    conn = db()
    conn.execute(
        "INSERT INTO products(name,description,price,icon) VALUES(?,?,?,?)",
        (request.form["name"], request.form["description"], float(request.form["price"]), request.form.get("icon","🛍️"))
    )
    conn.commit(); conn.close()
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/products/<int:pid>/toggle")
@admin_required
def admin_toggle_product(pid):
    conn = db()
    conn.execute("UPDATE products SET active=1-active WHERE id=?", (pid,))
    conn.commit(); conn.close()
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/products/<int:pid>/delete")
@admin_required
def admin_delete_product(pid):
    conn = db()
    conn.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit(); conn.close()
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/orders/<int:oid>/status")
@admin_required
def admin_order_status(oid):
    status = request.form.get("status","pending")
    if status not in {"pending","paid","completed","cancelled"}:
        status = "pending"
    conn = db()
    conn.execute("UPDATE orders SET status=? WHERE id=?", (status, oid))
    conn.commit(); conn.close()
    return redirect(url_for("admin_dashboard"))

@app.get("/status")
def status():
    return {"status":"online","service":"Oferta Play","version":"2.0"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
