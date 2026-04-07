from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import random
import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_cs2_cases_secret_key_2026"

DB_PATH = "site.db"

ITEMS = [
    {
        "name": "Glock-18 | Vogue",
        "rarity": "common",
        "price": 4.50,
        "chance": 24,
        "image": "https://images.unsplash.com/photo-1542751110-97427bbecf20?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "name": "USP-S | Cortex",
        "rarity": "common",
        "price": 7.90,
        "chance": 20,
        "image": "https://images.unsplash.com/photo-1511512578047-dfb367046420?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "name": "AK-47 | Redline",
        "rarity": "rare",
        "price": 14.20,
        "chance": 18,
        "image": "https://images.unsplash.com/photo-1560253023-3ec5d502959f?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "name": "M4A1-S | Decimator",
        "rarity": "rare",
        "price": 18.80,
        "chance": 14,
        "image": "https://images.unsplash.com/photo-1547394765-185e1e68f34e?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "name": "AWP | Neo-Noir",
        "rarity": "epic",
        "price": 39.50,
        "chance": 10,
        "image": "https://images.unsplash.com/photo-1548686304-89d188a80029?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "name": "Desert Eagle | Printstream",
        "rarity": "epic",
        "price": 62.00,
        "chance": 8,
        "image": "https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "name": "Karambit | Doppler",
        "rarity": "legendary",
        "price": 420.00,
        "chance": 4,
        "image": "https://images.unsplash.com/photo-1511884642898-4c92249e20b6?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "name": "Butterfly Knife | Fade",
        "rarity": "legendary",
        "price": 680.00,
        "chance": 2,
        "image": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?q=80&w=1200&auto=format&fit=crop"
    },
]

CASES = [
    {
        "id": 1,
        "name": "Neon Case",
        "price": 10,
        "color1": "#2563eb",
        "color2": "#7c3aed",
        "description": "Бюджетный кейс",
        "items": ITEMS
    },
    {
        "id": 2,
        "name": "Inferno Case",
        "price": 25,
        "color1": "#dc2626",
        "color2": "#f97316",
        "description": "Средний кейс",
        "items": ITEMS
    },
    {
        "id": 3,
        "name": "Elite Case",
        "price": 50,
        "color1": "#f59e0b",
        "color2": "#eab308",
        "description": "Дорогой кейс",
        "items": ITEMS
    }
]

RARITY_LABELS = {
    "common": "Обычный",
    "rare": "Редкий",
    "epic": "Эпический",
    "legendary": "Легендарный",
}

RARITY_COLORS = {
    "common": "#9ca3af",
    "rare": "#60a5fa",
    "epic": "#c084fc",
    "legendary": "#fbbf24",
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 100.0,
            is_admin INTEGER NOT NULL DEFAULT 0,
            last_daily_bonus TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            rarity TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            rarity TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT,
            source TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS contract_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            result_name TEXT NOT NULL,
            result_rarity TEXT NOT NULL,
            result_price REAL NOT NULL,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS upgrade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            source_name TEXT NOT NULL,
            target_name TEXT NOT NULL,
            success INTEGER NOT NULL,
            created_at TEXT
        )
    """)

    conn.commit()

    cur.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    admin = cur.fetchone()
    if not admin:
        cur.execute("""
            INSERT INTO users (username, password_hash, balance, is_admin, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "admin",
            generate_password_hash("admin123"),
            1000.0,
            1,
            datetime.utcnow().isoformat()
        ))
        conn.commit()

    conn.close()


def get_case_by_id(case_id):
    for c in CASES:
        if c["id"] == case_id:
            return c
    return None


def weighted_choice(items):
    expanded = []
    for item in items:
        expanded.extend([item] * item["chance"])
    return random.choice(expanded)


def get_item_by_name(name):
    for item in ITEMS:
        if item["name"] == name:
            return item
    return None


def enrich_item(row):
    return {
        "id": row["id"],
        "name": row["item_name"],
        "rarity": row["rarity"],
        "price": float(row["price"]),
        "image": row["image"],
        "color": RARITY_COLORS.get(row["rarity"], "#ffffff"),
        "rarity_label": RARITY_LABELS.get(row["rarity"], row["rarity"]),
        "created_at": row["created_at"],
    }


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row


def login_required():
    return current_user() is not None


def admin_required():
    user = current_user()
    return user and int(user["is_admin"]) == 1


def get_balance(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return float(row["balance"]) if row else 0.0


def set_balance(user_id, value):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = ? WHERE id = ?", (value, user_id))
    conn.commit()
    conn.close()


def add_balance(user_id, amount):
    new_balance = get_balance(user_id) + amount
    set_balance(user_id, new_balance)
    return new_balance


def get_inventory(user_id, rarity="", search=""):
    conn = get_db()
    cur = conn.cursor()

    query = """
        SELECT * FROM inventory
        WHERE user_id = ?
    """
    params = [user_id]

    if rarity:
        query += " AND rarity = ?"
        params.append(rarity)

    if search:
        query += " AND LOWER(item_name) LIKE ?"
        params.append(f"%{search.lower()}%")

    query += " ORDER BY id DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [enrich_item(r) for r in rows]


def get_inventory_all(user_id):
    return get_inventory(user_id, "", "")


def add_item_to_inventory(user_id, item):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO inventory (user_id, item_name, rarity, price, image, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        item["name"],
        item["rarity"],
        item["price"],
        item["image"],
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()


def delete_inventory_item(user_id, item_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM inventory WHERE id = ? AND user_id = ?", (item_id, user_id))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_inventory_item(user_id, item_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventory WHERE id = ? AND user_id = ?", (item_id, user_id))
    row = cur.fetchone()
    conn.close()
    return row


def add_history(user_id, item, source="case"):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO history (user_id, item_name, rarity, price, image, source, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        item["name"],
        item["rarity"],
        item["price"],
        item["image"],
        source,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()


def get_history(user_id, limit=10):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM history
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (user_id, limit))
    rows = cur.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "name": row["item_name"],
            "rarity": row["rarity"],
            "price": float(row["price"]),
            "image": row["image"],
            "source": row["source"],
            "color": RARITY_COLORS.get(row["rarity"], "#fff"),
            "rarity_label": RARITY_LABELS.get(row["rarity"], row["rarity"]),
        })
    return result


def sell_inventory_item(user_id, item_id):
    row = get_inventory_item(user_id, item_id)
    if not row:
        return None
    price = float(row["price"])
    if not delete_inventory_item(user_id, item_id):
        return None
    new_balance = add_balance(user_id, price)
    return new_balance


def sell_all_inventory(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(price), 0) AS total FROM inventory WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    total = float(row["total"]) if row else 0.0
    cur.execute("DELETE FROM inventory WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    new_balance = add_balance(user_id, total)
    return total, new_balance


def get_profile_stats(user_id):
    inventory = get_inventory_all(user_id)
    history = get_history(user_id, 999)
    total_inventory_value = round(sum(i["price"] for i in inventory), 2)
    total_opened = len(history)
    best_drop = max(history, key=lambda x: x["price"]) if history else None
    return {
        "inventory_count": len(inventory),
        "inventory_value": total_inventory_value,
        "total_opened": total_opened,
        "best_drop": best_drop
    }


def can_claim_daily_bonus(user):
    last = user["last_daily_bonus"]
    if not last:
        return True, 0
    last_dt = datetime.fromisoformat(last)
    next_time = last_dt + timedelta(hours=24)
    now = datetime.utcnow()
    if now >= next_time:
        return True, 0
    left = next_time - now
    return False, int(left.total_seconds())


BASE_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }}</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:Inter,Arial,sans-serif}
body{
    background:
    radial-gradient(circle at top left, rgba(124,58,237,.15), transparent 25%),
    radial-gradient(circle at top right, rgba(37,99,235,.12), transparent 25%),
    linear-gradient(180deg,#070b14,#0d1322);
    color:#fff;min-height:100vh
}
a{text-decoration:none;color:inherit}
.container{max-width:1400px;margin:0 auto;padding:24px}
.topbar{
    position:sticky;top:0;z-index:50;
    display:flex;justify-content:space-between;align-items:center;
    padding:18px 24px;background:rgba(7,11,20,.8);
    border-bottom:1px solid rgba(255,255,255,.08);backdrop-filter:blur(12px)
}
.logo{font-size:30px;font-weight:900}
.logo span{
    background:linear-gradient(90deg,#60a5fa,#c084fc);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent
}
.nav{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.nav a,.pill,.btn{
    border:1px solid rgba(255,255,255,.08);
    background:rgba(255,255,255,.05);
    padding:10px 14px;border-radius:14px
}
.btn{cursor:pointer;color:#fff;font-weight:800}
.btn-blue{background:linear-gradient(90deg,#2563eb,#7c3aed);border:none}
.btn-green{background:linear-gradient(90deg,#16a34a,#22c55e);border:none}
.btn-red{background:linear-gradient(90deg,#dc2626,#ef4444);border:none}
.btn-gold{background:linear-gradient(90deg,#d97706,#f59e0b);border:none}
.card{
    background:rgba(255,255,255,.045);
    border:1px solid rgba(255,255,255,.08);
    border-radius:24px;padding:20px;
    box-shadow:0 20px 60px rgba(0,0,0,.22)
}
.title{font-size:30px;font-weight:900;margin-bottom:16px}
.subtitle{color:#94a3b8;margin-bottom:16px}
.grid{display:grid;gap:18px}
.grid-3{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.grid-2{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.input,.select{
    width:100%;padding:14px 16px;border-radius:14px;
    background:#0f172a;border:1px solid rgba(255,255,255,.08);color:#fff
}
.form-group{margin-bottom:14px}
.label{display:block;margin-bottom:8px;color:#cbd5e1;font-weight:700}
.notice{
    padding:14px 16px;border-radius:14px;margin-bottom:16px;
    background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08)
}
.cases-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}
.case-card{
    border-radius:24px;padding:18px;background:rgba(255,255,255,.045);
    border:1px solid rgba(255,255,255,.08)
}
.case-glow{
    height:170px;border-radius:20px;display:flex;align-items:center;justify-content:center;
    font-size:28px;font-weight:900;margin-bottom:14px
}
.case-name{font-size:22px;font-weight:900;margin-bottom:8px}
.case-desc{color:#cbd5e1;font-size:14px;min-height:40px;margin-bottom:10px}
.case-price{color:#fbbf24;font-weight:900;font-size:18px;margin-bottom:14px}
.roulette-wrap,.inventory-wrap,.history-wrap{margin-top:24px}
.roulette-area{
    position:relative;height:190px;background:#0b1220;border-radius:20px;
    overflow:hidden;border:1px solid rgba(255,255,255,.08)
}
.pointer{
    position:absolute;left:50%;top:0;transform:translateX(-50%);
    width:8px;height:100%;z-index:5;
    background:linear-gradient(180deg,#f59e0b,#ef4444)
}
.roulette-track{
    display:flex;align-items:center;gap:14px;height:100%;padding:0 14px;
    transition:transform 6s cubic-bezier(.08,.7,.15,1)
}
.drop-card{
    min-width:220px;height:140px;border-radius:18px;overflow:hidden;
    background:#111827;border:2px solid transparent
}
.drop-image,.inventory-image{
    height:90px;background-size:cover;background-position:center
}
.drop-info,.inventory-content{padding:12px}
.rarity{font-size:12px;font-weight:800;margin-bottom:6px}
.drop-name{font-size:15px;font-weight:900;line-height:1.2;margin-bottom:6px}
.drop-price{color:#fbbf24;font-weight:800}
.result-box{
    margin-top:16px;min-height:74px;border-radius:18px;padding:18px;
    display:flex;align-items:center;justify-content:center;text-align:center;
    background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);color:#cbd5e1
}
.inventory-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}
.inventory-item{
    border-radius:20px;overflow:hidden;background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.08)
}
.inventory-image{height:120px}
.inventory-actions{display:flex;gap:10px;margin-top:10px}
.small-btn{
    flex:1;border:none;padding:10px 12px;border-radius:12px;cursor:pointer;
    font-weight:800;color:#fff
}
.empty-box{
    color:#94a3b8;border:1px dashed rgba(255,255,255,.1);border-radius:18px;
    padding:18px;background:rgba(255,255,255,.03)
}
.filters{display:grid;grid-template-columns:1fr 180px 180px;gap:12px}
.stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.stat-box{padding:16px;border-radius:18px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08)}
.stat-title{font-size:13px;color:#94a3b8;margin-bottom:8px}
.stat-value{font-size:24px;font-weight:900}
.history-list{display:flex;flex-direction:column;gap:10px}
.history-item{padding:14px;border-radius:16px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08)}
.hero{display:grid;grid-template-columns:1.2fr .8fr;gap:20px;margin-bottom:20px}
.mt16{margin-top:16px}
.mt24{margin-top:24px}
.flex{display:flex;gap:12px;flex-wrap:wrap}
.table{width:100%;border-collapse:collapse}
.table th,.table td{padding:12px;border-bottom:1px solid rgba(255,255,255,.08);text-align:left}
.badge{padding:6px 10px;border-radius:999px;background:rgba(255,255,255,.06);display:inline-block}
@media(max-width:1100px){
    .hero{grid-template-columns:1fr}
    .filters{grid-template-columns:1fr}
}
@media(max-width:700px){
    .topbar{padding:16px}
    .container{padding:16px}
}
</style>
</head>
<body>
<div class="topbar">
    <a href="/" class="logo">CS2 <span>CASES</span></a>
    <div class="nav">
        <a href="/">Главная</a>
        {% if user %}
            <a href="/profile">Профиль</a>
            <a href="/inventory">Инвентарь</a>
            <a href="/upgrade">Апгрейд</a>
            <a href="/contract">Контракт</a>
            <a href="/daily">Daily</a>
            {% if user["is_admin"] == 1 %}
                <a href="/admin">Админка</a>
            {% endif %}
            <div class="pill">Баланс: <span style="color:#fbbf24">${{ "%.2f"|format(user["balance"]) }}</span></div>
            <a href="/logout" class="btn btn-red">Выйти</a>
        {% else %}
            <a href="/login">Вход</a>
            <a href="/register" class="btn btn-blue">Регистрация</a>
        {% endif %}
    </div>
</div>

<div class="container">
    {{ body|safe }}
</div>

<script>
function showToast(msg){
    alert(msg);
}
</script>
</body>
</html>
"""


def render_page(title, body, **kwargs):
    user = current_user()
    return render_template_string(BASE_HTML, title=title, body=body, user=user, **kwargs)


@app.before_request
def before_request():
    init_db()


@app.route("/")
def index():
    user = current_user()

    body = """
    <div class="hero">
        <div class="card">
            <div class="title">Открывай кейсы и выбивай дорогие скины</div>
            <div class="subtitle">Тут уже есть аккаунты, профиль, фильтр инвентаря, апгрейд, контракт, daily bonus и админка.</div>
            {% if not user %}
                <div class="flex">
                    <a href="/register" class="btn btn-blue">Создать аккаунт</a>
                    <a href="/login" class="btn">Войти</a>
                </div>
                <div class="notice mt16">Тестовый админ: <b>admin</b> / <b>admin123</b></div>
            {% else %}
                <div class="notice">Ты вошёл как <b>{{ user["username"] }}</b></div>
            {% endif %}
        </div>

        <div class="card">
            <div class="title" style="font-size:24px">Редкости</div>
            <div class="history-list">
                <div class="history-item"><span style="color:#9ca3af;font-weight:900">Обычный</span> — самый частый</div>
                <div class="history-item"><span style="color:#60a5fa;font-weight:900">Редкий</span> — норм</div>
                <div class="history-item"><span style="color:#c084fc;font-weight:900">Эпический</span> — хороший</div>
                <div class="history-item"><span style="color:#fbbf24;font-weight:900">Легендарный</span> — жир</div>
            </div>
        </div>
    </div>

    <div class="card">
        <div class="title">Кейсы</div>
        {% if not user %}
            <div class="notice">Чтобы открывать кейсы, сначала зарегистрируйся или войди.</div>
        {% endif %}
        <div class="cases-grid">
            {% for case in cases %}
            <div class="case-card">
                <div class="case-glow" style="background:linear-gradient(135deg, {{ case.color1 }}, {{ case.color2 }});">
                    {{ case.name }}
                </div>
                <div class="case-name">{{ case.name }}</div>
                <div class="case-desc">{{ case.description }}</div>
                <div class="case-price">$ {{ case.price }}</div>
                {% if user %}
                    <button class="btn btn-blue" style="width:100%" onclick="openCase({{ case.id }}, '{{ case.name }}')">Открыть кейс</button>
                {% else %}
                    <a href="/login" class="btn btn-blue" style="display:block;text-align:center">Войти чтобы открыть</a>
                {% endif %}
            </div>
            {% endfor %}
        </div>

        {% if user %}
        <div class="roulette-wrap mt24">
            <div class="title" style="font-size:24px">Открытие кейса</div>
            <div class="subtitle" id="selectedCaseText">Выбери кейс</div>
            <div class="roulette-area">
                <div class="pointer"></div>
                <div class="roulette-track" id="rouletteTrack"></div>
            </div>
            <div class="result-box" id="resultBox">Тут появится твой дроп</div>
        </div>
        {% endif %}
    </div>

    {% if user %}
    <script>
    let spinning = false;

    function rarityLabel(rarity){
        if(rarity==="common") return "Обычный";
        if(rarity==="rare") return "Редкий";
        if(rarity==="epic") return "Эпический";
        return "Легендарный";
    }

    function rarityColor(rarity){
        if(rarity==="common") return "#9ca3af";
        if(rarity==="rare") return "#60a5fa";
        if(rarity==="epic") return "#c084fc";
        return "#fbbf24";
    }

    function createDropCard(item){
        const color = rarityColor(item.rarity);
        const label = rarityLabel(item.rarity);
        return `
            <div class="drop-card" style="border-color:${color}">
                <div class="drop-image" style="background-image:url('${item.image}')"></div>
                <div class="drop-info">
                    <div class="rarity" style="color:${color}">${label}</div>
                    <div class="drop-name">${item.name}</div>
                    <div class="drop-price">$ ${Number(item.price).toFixed(2)}</div>
                </div>
            </div>
        `;
    }

    function buildRoulette(items, winnerIndex){
        const track = document.getElementById("rouletteTrack");
        track.style.transition = "none";
        track.style.transform = "translateX(0px)";
        track.innerHTML = items.map(createDropCard).join("");

        setTimeout(() => {
            const cardWidth = 234;
            const areaWidth = document.querySelector(".roulette-area").offsetWidth;
            const pointerOffset = areaWidth / 2 - cardWidth / 2;
            const moveX = (winnerIndex * cardWidth) - pointerOffset;
            track.style.transition = "transform 6s cubic-bezier(.08,.7,.15,1)";
            track.style.transform = `translateX(-${moveX}px)`;
        }, 50);
    }

    async function openCase(caseId, caseName){
        if(spinning) return;
        spinning = true;
        document.getElementById("selectedCaseText").textContent = "Открывается: " + caseName;
        document.getElementById("resultBox").textContent = "Кейс открывается...";

        const res = await fetch("/open_case", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({case_id: caseId})
        });

        const data = await res.json();
        if(!data.success){
            document.getElementById("resultBox").textContent = data.error;
            spinning = false;
            return;
        }

        buildRoulette(data.roulette_items, data.winner_index);

        setTimeout(() => {
            document.getElementById("resultBox").innerHTML =
                `Тебе выпало: <span style="color:${data.item.color}">${data.item.name}</span> — $${Number(data.item.price).toFixed(2)}`;
            spinning = false;
            setTimeout(() => location.reload(), 1200);
        }, 6200);
    }
    </script>
    {% endif %}
    """
    return render_page("CS2 Cases", body, cases=CASES, user=user)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("index"))

    error = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if len(username) < 3:
            error = "Логин минимум 3 символа."
        elif len(password) < 4:
            error = "Пароль минимум 4 символа."
        else:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE username = ?", (username,))
            exists = cur.fetchone()
            if exists:
                error = "Такой логин уже существует."
            else:
                cur.execute("""
                    INSERT INTO users (username, password_hash, balance, is_admin, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    username,
                    generate_password_hash(password),
                    100.0,
                    0,
                    datetime.utcnow().isoformat()
                ))
                conn.commit()
                conn.close()

                conn = get_db()
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE username = ?", (username,))
                user = cur.fetchone()
                conn.close()
                session["user_id"] = user["id"]
                return redirect(url_for("index"))
            conn.close()

    body = """
    <div class="card" style="max-width:520px;margin:0 auto">
        <div class="title">Регистрация</div>
        {% if error %}<div class="notice">{{ error }}</div>{% endif %}
        <form method="post">
            <div class="form-group">
                <label class="label">Логин</label>
                <input class="input" name="username" placeholder="Введите логин">
            </div>
            <div class="form-group">
                <label class="label">Пароль</label>
                <input class="input" type="password" name="password" placeholder="Введите пароль">
            </div>
            <button class="btn btn-blue" style="width:100%">Создать аккаунт</button>
        </form>
    </div>
    """
    return render_page("Регистрация", body, error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("index"))

    error = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()

        if not user or not check_password_hash(user["password_hash"], password):
            error = "Неверный логин или пароль."
        else:
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

    body = """
    <div class="card" style="max-width:520px;margin:0 auto">
        <div class="title">Вход</div>
        {% if error %}<div class="notice">{{ error }}</div>{% endif %}
        <form method="post">
            <div class="form-group">
                <label class="label">Логин</label>
                <input class="input" name="username" placeholder="Введите логин">
            </div>
            <div class="form-group">
                <label class="label">Пароль</label>
                <input class="input" type="password" name="password" placeholder="Введите пароль">
            </div>
            <button class="btn btn-blue" style="width:100%">Войти</button>
        </form>
        <div class="notice mt16">Тестовый админ: admin / admin123</div>
    </div>
    """
    return render_page("Вход", body, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/profile")
def profile():
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    stats = get_profile_stats(user["id"])
    can_claim, seconds_left = can_claim_daily_bonus(user)

    best_drop = stats["best_drop"]
    best_drop_name = best_drop["name"] if best_drop else "Пока нет"
    best_drop_price = f'${best_drop["price"]:.2f}' if best_drop else "-"

    hours = seconds_left // 3600
    minutes = (seconds_left % 3600) // 60

    body = """
    <div class="card">
        <div class="title">Профиль</div>
        <div class="subtitle">Аккаунт: <b>{{ user["username"] }}</b></div>

        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-title">Баланс</div>
                <div class="stat-value">${{ "%.2f"|format(user["balance"]) }}</div>
            </div>
            <div class="stat-box">
                <div class="stat-title">Предметов</div>
                <div class="stat-value">{{ stats["inventory_count"] }}</div>
            </div>
            <div class="stat-box">
                <div class="stat-title">Стоимость инвентаря</div>
                <div class="stat-value">${{ "%.2f"|format(stats["inventory_value"]) }}</div>
            </div>
            <div class="stat-box">
                <div class="stat-title">Открыто кейсов / дропов</div>
                <div class="stat-value">{{ stats["total_opened"] }}</div>
            </div>
            <div class="stat-box">
                <div class="stat-title">Лучший дроп</div>
                <div class="stat-value" style="font-size:18px">{{ best_drop_name }}</div>
                <div class="subtitle" style="margin:8px 0 0 0">{{ best_drop_price }}</div>
            </div>
            <div class="stat-box">
                <div class="stat-title">Daily бонус</div>
                {% if can_claim %}
                    <div class="stat-value" style="font-size:18px">Можно забрать</div>
                {% else %}
                    <div class="stat-value" style="font-size:18px">{{ hours }}ч {{ minutes }}м</div>
                {% endif %}
            </div>
        </div>

        <div class="flex mt24">
            <a href="/inventory" class="btn btn-blue">Мой инвентарь</a>
            <a href="/daily" class="btn btn-gold">Daily bonus</a>
            <a href="/upgrade" class="btn">Апгрейд</a>
            <a href="/contract" class="btn">Контракт</a>
        </div>
    </div>
    """
    return render_page("Профиль", body, user=user, stats=stats, can_claim=can_claim, hours=hours, minutes=minutes)


@app.route("/inventory")
def inventory():
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    rarity = request.args.get("rarity", "").strip()
    search = request.args.get("search", "").strip()
    items = get_inventory(user["id"], rarity, search)

    body = """
    <div class="card inventory-wrap">
        <div class="title">Инвентарь</div>

        <form method="get" class="filters">
            <input class="input" name="search" value="{{ search }}" placeholder="Поиск по названию">
            <select class="select" name="rarity">
                <option value="">Все редкости</option>
                <option value="common" {% if rarity=="common" %}selected{% endif %}>Обычный</option>
                <option value="rare" {% if rarity=="rare" %}selected{% endif %}>Редкий</option>
                <option value="epic" {% if rarity=="epic" %}selected{% endif %}>Эпический</option>
                <option value="legendary" {% if rarity=="legendary" %}selected{% endif %}>Легендарный</option>
            </select>
            <button class="btn btn-blue">Фильтр</button>
        </form>

        <div class="mt16 flex">
            <button class="btn btn-red" onclick="sellAll()">Продать всё</button>
        </div>

        <div class="mt24" id="inventoryArea">
            {% if items %}
                <div class="inventory-grid">
                    {% for item in items %}
                    <div class="inventory-item">
                        <div class="inventory-image" style="background-image:url('{{ item.image }}')"></div>
                        <div class="inventory-content">
                            <div class="rarity" style="color:{{ item.color }}">{{ item.rarity_label }}</div>
                            <div class="drop-name">{{ item.name }}</div>
                            <div class="drop-price">$ {{ "%.2f"|format(item.price) }}</div>
                            <div class="inventory-actions">
                                <button class="small-btn" style="background:#dc2626" onclick="sellItem({{ item.id }})">Продать</button>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="empty-box">Ничего не найдено.</div>
            {% endif %}
        </div>
    </div>

    <script>
    async function sellItem(itemId){
        const res = await fetch("/sell_item", {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({item_id:itemId})
        });
        const data = await res.json();
        if(!data.success){ alert(data.error); return; }
        location.reload();
    }

    async function sellAll(){
        const res = await fetch("/sell_all", {method:"POST"});
        const data = await res.json();
        if(!data.success){ alert(data.error); return; }
        location.reload();
    }
    </script>
    """
    return render_page("Инвентарь", body, items=items, rarity=rarity, search=search)


@app.route("/daily", methods=["GET", "POST"])
def daily():
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    message = ""
    error = ""

    if request.method == "POST":
        can_claim, seconds_left = can_claim_daily_bonus(user)
        if not can_claim:
            hours = seconds_left // 3600
            minutes = (seconds_left % 3600) // 60
            error = f"Ещё нельзя. Осталось {hours}ч {minutes}м."
        else:
            reward = random.choice([15, 20, 25, 30, 40, 50])
            add_balance(user["id"], reward)

            conn = get_db()
            cur = conn.cursor()
            cur.execute("UPDATE users SET last_daily_bonus = ? WHERE id = ?", (
                datetime.utcnow().isoformat(),
                user["id"]
            ))
            conn.commit()
            conn.close()

            message = f"Ты забрал daily bonus: ${reward}"

    user = current_user()
    can_claim, seconds_left = can_claim_daily_bonus(user)
    hours = seconds_left // 3600
    minutes = (seconds_left % 3600) // 60

    body = """
    <div class="card" style="max-width:700px;margin:0 auto">
        <div class="title">Daily bonus</div>
        {% if message %}<div class="notice">{{ message }}</div>{% endif %}
        {% if error %}<div class="notice">{{ error }}</div>{% endif %}

        {% if can_claim %}
            <div class="subtitle">Можно забрать бонус прямо сейчас.</div>
            <form method="post">
                <button class="btn btn-gold" style="width:100%">Забрать бонус</button>
            </form>
        {% else %}
            <div class="notice">Следующий бонус через {{ hours }}ч {{ minutes }}м</div>
        {% endif %}
    </div>
    """
    return render_page("Daily bonus", body, can_claim=can_claim, message=message, error=error, hours=hours, minutes=minutes)


@app.route("/upgrade", methods=["GET", "POST"])
def upgrade():
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    inventory_items = get_inventory_all(user["id"])
    message = ""
    error = ""
    result = None

    if request.method == "POST":
        source_id = request.form.get("source_id")
        target_name = request.form.get("target_name", "").strip()

        if not source_id or not target_name:
            error = "Выбери исходный предмет и цель."
        else:
            source_row = get_inventory_item(user["id"], int(source_id))
            target_item = get_item_by_name(target_name)

            if not source_row:
                error = "Исходный предмет не найден."
            elif not target_item:
                error = "Цель не найдена."
            else:
                source_price = float(source_row["price"])
                target_price = float(target_item["price"])

                if target_price <= source_price:
                    error = "Цель должна быть дороже исходного предмета."
                else:
                    chance = max(5, min(85, round((source_price / target_price) * 100)))
                    roll = random.randint(1, 100)
                    success = roll <= chance

                    conn = get_db()
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO upgrade_history (user_id, source_name, target_name, success, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        user["id"],
                        source_row["item_name"],
                        target_name,
                        1 if success else 0,
                        datetime.utcnow().isoformat()
                    ))
                    conn.commit()
                    conn.close()

                    delete_inventory_item(user["id"], int(source_id))

                    if success:
                        add_item_to_inventory(user["id"], target_item)
                        add_history(user["id"], target_item, "upgrade")
                        result = {
                            "success": True,
                            "text": f"Успех. Ты апнул до {target_item['name']}",
                            "chance": chance
                        }
                    else:
                        result = {
                            "success": False,
                            "text": "Неудача. Предмет сгорел.",
                            "chance": chance
                        }

    targets = sorted(ITEMS, key=lambda x: x["price"])

    body = """
    <div class="card" style="max-width:900px;margin:0 auto">
        <div class="title">Апгрейд</div>
        <div class="subtitle">Выбираешь свой предмет и предмет, до которого хочешь апнуться. Если не повезёт — исходный предмет сгорит.</div>

        {% if error %}<div class="notice">{{ error }}</div>{% endif %}
        {% if result %}
            <div class="notice">
                <b>{{ result["text"] }}</b><br>
                Шанс был: {{ result["chance"] }}%
            </div>
        {% endif %}

        <form method="post">
            <div class="form-group">
                <label class="label">Твой предмет</label>
                <select class="select" name="source_id">
                    <option value="">Выбери предмет</option>
                    {% for item in inventory_items %}
                        <option value="{{ item.id }}">{{ item.name }} — ${{ "%.2f"|format(item.price) }}</option>
                    {% endfor %}
                </select>
            </div>

            <div class="form-group">
                <label class="label">Цель апгрейда</label>
                <select class="select" name="target_name">
                    <option value="">Выбери цель</option>
                    {% for item in targets %}
                        <option value="{{ item.name }}">{{ item.name }} — ${{ "%.2f"|format(item.price) }}</option>
                    {% endfor %}
                </select>
            </div>

            <button class="btn btn-blue" style="width:100%">Запустить апгрейд</button>
        </form>
    </div>
    """
    return render_page("Апгрейд", body, inventory_items=inventory_items, targets=targets, error=error, result=result)


@app.route("/contract", methods=["GET", "POST"])
def contract():
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    inventory_items = get_inventory_all(user["id"])
    message = ""
    error = ""
    result = None

    if request.method == "POST":
        ids = request.form.getlist("item_ids")

        if len(ids) < 3:
            error = "Нужно выбрать минимум 3 предмета."
        else:
            selected_rows = []
            total_price = 0.0

            for item_id in ids[:10]:
                row = get_inventory_item(user["id"], int(item_id))
                if row:
                    selected_rows.append(row)
                    total_price += float(row["price"])

            if len(selected_rows) < 3:
                error = "Не удалось собрать предметы для контракта."
            else:
                min_target = total_price / len(selected_rows)
                possible = [i for i in ITEMS if i["price"] >= min_target]

                if not possible:
                    possible = ITEMS[:]

                result_item = random.choice(possible)

                for row in selected_rows:
                    delete_inventory_item(user["id"], row["id"])

                add_item_to_inventory(user["id"], result_item)
                add_history(user["id"], result_item, "contract")

                conn = get_db()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO contract_history (user_id, result_name, result_rarity, result_price, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    user["id"],
                    result_item["name"],
                    result_item["rarity"],
                    result_item["price"],
                    datetime.utcnow().isoformat()
                ))
                conn.commit()
                conn.close()

                result = {
                    "name": result_item["name"],
                    "price": result_item["price"],
                    "rarity_label": RARITY_LABELS.get(result_item["rarity"], result_item["rarity"]),
                    "color": RARITY_COLORS.get(result_item["rarity"], "#fff")
                }

    body = """
    <div class="card" style="max-width:1000px;margin:0 auto">
        <div class="title">Контракт</div>
        <div class="subtitle">Выбери минимум 3 предмета. Они сгорят, а ты получишь один новый.</div>

        {% if error %}<div class="notice">{{ error }}</div>{% endif %}
        {% if result %}
            <div class="notice">
                Контракт дал: <b style="color:{{ result.color }}">{{ result.name }}</b> —
                ${{ "%.2f"|format(result.price) }} ({{ result.rarity_label }})
            </div>
        {% endif %}

        <form method="post">
            <div class="inventory-grid">
                {% for item in inventory_items %}
                <label class="inventory-item" style="cursor:pointer">
                    <div class="inventory-image" style="background-image:url('{{ item.image }}')"></div>
                    <div class="inventory-content">
                        <div class="rarity" style="color:{{ item.color }}">{{ item.rarity_label }}</div>
                        <div class="drop-name">{{ item.name }}</div>
                        <div class="drop-price">$ {{ "%.2f"|format(item.price) }}</div>
                        <div class="mt16">
                            <input type="checkbox" name="item_ids" value="{{ item.id }}">
                        </div>
                    </div>
                </label>
                {% endfor %}
            </div>

            <div class="mt24">
                <button class="btn btn-blue" style="width:100%">Сделать контракт</button>
            </div>
        </form>
    </div>
    """
    return render_page("Контракт", body, inventory_items=inventory_items, result=result, error=error)


@app.route("/admin")
def admin():
    if not admin_required():
        return redirect(url_for("index"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, balance, is_admin, created_at FROM users ORDER BY id DESC")
    users = cur.fetchall()

    cur.execute("SELECT COUNT(*) AS c FROM inventory")
    total_inventory = cur.fetchone()["c"]

    cur.execute("SELECT COUNT(*) AS c FROM history")
    total_history = cur.fetchone()["c"]

    conn.close()

    body = """
    <div class="card">
        <div class="title">Админка</div>
        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-title">Пользователей</div>
                <div class="stat-value">{{ users|length }}</div>
            </div>
            <div class="stat-box">
                <div class="stat-title">Предметов в инвентарях</div>
                <div class="stat-value">{{ total_inventory }}</div>
            </div>
            <div class="stat-box">
                <div class="stat-title">Всего записей истории</div>
                <div class="stat-value">{{ total_history }}</div>
            </div>
        </div>

        <div class="mt24">
            <table class="table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Логин</th>
                        <th>Баланс</th>
                        <th>Роль</th>
                        <th>Создан</th>
                    </tr>
                </thead>
                <tbody>
                    {% for u in users %}
                    <tr>
                        <td>{{ u["id"] }}</td>
                        <td>{{ u["username"] }}</td>
                        <td>${{ "%.2f"|format(u["balance"]) }}</td>
                        <td>{% if u["is_admin"] == 1 %}<span class="badge">admin</span>{% else %}user{% endif %}</td>
                        <td>{{ u["created_at"] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    """
    return render_page("Админка", body, users=users, total_inventory=total_inventory, total_history=total_history)


@app.route("/open_case", methods=["POST"])
def open_case():
    user = current_user()
    if not user:
        return jsonify({"success": False, "error": "Сначала войди в аккаунт."})

    data = request.get_json(silent=True) or {}
    case_id = data.get("case_id")
    selected_case = get_case_by_id(case_id)

    if not selected_case:
        return jsonify({"success": False, "error": "Кейс не найден."})

    balance = float(user["balance"])
    if balance < selected_case["price"]:
        return jsonify({"success": False, "error": "Недостаточно баланса."})

    set_balance(user["id"], balance - selected_case["price"])

    winner = weighted_choice(selected_case["items"])
    roulette_items = [random.choice(selected_case["items"]) for _ in range(30)]
    winner_index = 24
    roulette_items[winner_index] = winner

    add_item_to_inventory(user["id"], winner)
    add_history(user["id"], winner, "case")

    winner_response = {
        "name": winner["name"],
        "rarity": winner["rarity"],
        "price": winner["price"],
        "image": winner["image"],
        "color": RARITY_COLORS.get(winner["rarity"], "#ffffff"),
        "rarity_label": RARITY_LABELS.get(winner["rarity"], winner["rarity"])
    }

    return jsonify({
        "success": True,
        "item": winner_response,
        "roulette_items": roulette_items,
        "winner_index": winner_index
    })


@app.route("/sell_item", methods=["POST"])
def sell_item():
    user = current_user()
    if not user:
        return jsonify({"success": False, "error": "Сначала войди."})

    data = request.get_json(silent=True) or {}
    item_id = data.get("item_id")
    if not item_id:
        return jsonify({"success": False, "error": "Не передан item_id."})

    new_balance = sell_inventory_item(user["id"], int(item_id))
    if new_balance is None:
        return jsonify({"success": False, "error": "Предмет не найден."})

    return jsonify({"success": True, "balance": round(new_balance, 2)})


@app.route("/sell_all", methods=["POST"])
def sell_all():
    user = current_user()
    if not user:
        return jsonify({"success": False, "error": "Сначала войди."})

    inventory_items = get_inventory_all(user["id"])
    if not inventory_items:
        return jsonify({"success": False, "error": "Инвентарь пуст."})

    total, new_balance = sell_all_inventory(user["id"])
    return jsonify({
        "success": True,
        "total": round(total, 2),
        "balance": round(new_balance, 2)
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
