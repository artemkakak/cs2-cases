from flask import Flask, render_template_string, request, jsonify, session
import random
import os
import sqlite3
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "cs2_cases_super_demo_secret_key_v3"


DB_PATH = "site.db"


ITEMS = [
    {
        "name": "Glock-18 | Vogue",
        "rarity": "common",
        "price": 4.50,
        "chance": 24,
        "image": "https://via.placeholder.com/280x120/1f2937/ffffff?text=Glock-18+%7C+Vogue"
    },
    {
        "name": "USP-S | Cortex",
        "rarity": "common",
        "price": 7.90,
        "chance": 20,
        "image": "https://via.placeholder.com/280x120/111827/ffffff?text=USP-S+%7C+Cortex"
    },
    {
        "name": "AK-47 | Redline",
        "rarity": "rare",
        "price": 14.20,
        "chance": 18,
        "image": "https://via.placeholder.com/280x120/1e293b/ffffff?text=AK-47+%7C+Redline"
    },
    {
        "name": "M4A1-S | Decimator",
        "rarity": "rare",
        "price": 18.80,
        "chance": 14,
        "image": "https://via.placeholder.com/280x120/0f172a/ffffff?text=M4A1-S+%7C+Decimator"
    },
    {
        "name": "AWP | Neo-Noir",
        "rarity": "epic",
        "price": 39.50,
        "chance": 10,
        "image": "https://via.placeholder.com/280x120/111827/ffffff?text=AWP+%7C+Neo-Noir"
    },
    {
        "name": "Desert Eagle | Printstream",
        "rarity": "epic",
        "price": 62.00,
        "chance": 8,
        "image": "https://via.placeholder.com/280x120/1f2937/ffffff?text=Deagle+%7C+Printstream"
    },
    {
        "name": "Karambit | Doppler",
        "rarity": "legendary",
        "price": 420.00,
        "chance": 4,
        "image": "https://via.placeholder.com/280x120/111827/ffffff?text=Karambit+%7C+Doppler"
    },
    {
        "name": "Butterfly Knife | Fade",
        "rarity": "legendary",
        "price": 680.00,
        "chance": 2,
        "image": "https://via.placeholder.com/280x120/0f172a/ffffff?text=Butterfly+%7C+Fade"
    },
]

CASES = [
    {
        "id": 1,
        "name": "Neon Case",
        "price": 10,
        "color1": "#2563eb",
        "color2": "#7c3aed",
        "description": "Бюджетный кейс с шансом на жирный нож",
        "items": ITEMS
    },
    {
        "id": 2,
        "name": "Inferno Case",
        "price": 25,
        "color1": "#dc2626",
        "color2": "#f97316",
        "description": "Средний кейс с хорошим шансом на эпик",
        "items": ITEMS
    },
    {
        "id": 3,
        "name": "Elite Case",
        "price": 50,
        "color1": "#f59e0b",
        "color2": "#eab308",
        "description": "Дорогой кейс для сильных дропов",
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
            id TEXT PRIMARY KEY,
            balance REAL NOT NULL DEFAULT 100.0,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
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
            user_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            rarity TEXT NOT NULL,
            price REAL NOT NULL,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_or_create_user():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())

    user_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()

    if not user:
        cur.execute(
            "INSERT INTO users (id, balance, created_at) VALUES (?, ?, ?)",
            (user_id, 100.0, datetime.utcnow().isoformat())
        )
        conn.commit()

    conn.close()
    return user_id


def get_balance(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return float(row["balance"]) if row else 0.0


def set_balance(user_id, balance):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = ? WHERE id = ?", (balance, user_id))
    conn.commit()
    conn.close()


def add_balance_db(user_id, amount):
    balance = get_balance(user_id) + amount
    set_balance(user_id, balance)
    return balance


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


def add_history(user_id, item):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO history (user_id, item_name, rarity, price, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        item["name"],
        item["rarity"],
        item["price"],
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()


def get_inventory(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, item_name, rarity, price, image, created_at
        FROM inventory
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "name": row["item_name"],
            "rarity": row["rarity"],
            "price": row["price"],
            "image": row["image"],
            "color": RARITY_COLORS.get(row["rarity"], "#ffffff"),
            "rarity_label": RARITY_LABELS.get(row["rarity"], row["rarity"])
        })
    return result


def get_history(user_id, limit=8):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT item_name, rarity, price, created_at
        FROM history
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
            "price": row["price"],
            "color": RARITY_COLORS.get(row["rarity"], "#ffffff"),
            "rarity_label": RARITY_LABELS.get(row["rarity"], row["rarity"]),
        })
    return result


def sell_inventory_item(user_id, item_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, price FROM inventory
        WHERE user_id = ? AND id = ?
    """, (user_id, item_id))
    row = cur.fetchone()

    if not row:
        conn.close()
        return None

    price = float(row["price"])
    cur.execute("DELETE FROM inventory WHERE id = ? AND user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()

    new_balance = add_balance_db(user_id, price)
    return new_balance


def sell_all_inventory(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(price), 0) as total FROM inventory WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    total = float(row["total"]) if row else 0.0

    cur.execute("DELETE FROM inventory WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    new_balance = add_balance_db(user_id, total)
    return total, new_balance


def weighted_choice(items):
    expanded = []
    for item in items:
        expanded.extend([item] * item["chance"])
    return random.choice(expanded)


def get_case_by_id(case_id):
    for case in CASES:
        if case["id"] == case_id:
            return case
    return None


HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CS2 Cases</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: Inter, Arial, sans-serif; }
        body {
            background:
                radial-gradient(circle at top, rgba(124,58,237,0.18), transparent 30%),
                radial-gradient(circle at right, rgba(37,99,235,0.14), transparent 25%),
                linear-gradient(180deg, #070b14, #0d1322);
            color: #fff;
            min-height: 100vh;
        }

        .topbar {
            position: sticky;
            top: 0;
            z-index: 50;
            backdrop-filter: blur(12px);
            background: rgba(7, 11, 20, 0.75);
            border-bottom: 1px solid rgba(255,255,255,0.08);
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px 24px;
        }

        .logo {
            font-size: 30px;
            font-weight: 900;
            letter-spacing: 1px;
        }

        .logo span {
            background: linear-gradient(90deg, #60a5fa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .top-actions {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }

        .pill {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 10px 14px;
            font-weight: 700;
        }

        .balance {
            color: #fbbf24;
        }

        .btn {
            border: none;
            border-radius: 14px;
            padding: 12px 16px;
            font-weight: 800;
            cursor: pointer;
            color: #fff;
            transition: 0.2s ease;
        }

        .btn:hover {
            transform: translateY(-2px);
        }

        .btn-green { background: linear-gradient(90deg, #16a34a, #22c55e); }
        .btn-red { background: linear-gradient(90deg, #dc2626, #ef4444); }
        .btn-blue { background: linear-gradient(90deg, #2563eb, #7c3aed); }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px;
        }

        .hero {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 20px;
            margin-top: 10px;
            margin-bottom: 24px;
        }

        .hero-left, .hero-right {
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.04);
            border-radius: 28px;
            padding: 28px;
            box-shadow: 0 30px 80px rgba(0,0,0,0.25);
        }

        .hero-left h1 {
            font-size: 48px;
            line-height: 1.05;
            margin-bottom: 14px;
        }

        .hero-left p {
            color: #cbd5e1;
            font-size: 16px;
            max-width: 700px;
        }

        .hero-stats {
            margin-top: 20px;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .stat-box {
            min-width: 160px;
            border-radius: 18px;
            padding: 16px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
        }

        .stat-title {
            color: #94a3b8;
            font-size: 13px;
            margin-bottom: 8px;
        }

        .stat-value {
            font-size: 24px;
            font-weight: 900;
        }

        .section-title {
            font-size: 28px;
            font-weight: 900;
            margin: 10px 0 16px;
        }

        .cases-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 18px;
        }

        .case-card {
            border-radius: 24px;
            padding: 18px;
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.08);
            overflow: hidden;
            position: relative;
            transition: 0.22s ease;
        }

        .case-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.28);
        }

        .case-glow {
            height: 170px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: 900;
            margin-bottom: 14px;
            box-shadow: inset 0 0 40px rgba(255,255,255,0.1), 0 0 40px rgba(0,0,0,0.2);
        }

        .case-name {
            font-size: 22px;
            font-weight: 900;
            margin-bottom: 8px;
        }

        .case-desc {
            color: #cbd5e1;
            font-size: 14px;
            min-height: 40px;
            margin-bottom: 10px;
        }

        .case-price {
            color: #fbbf24;
            font-weight: 900;
            font-size: 18px;
            margin-bottom: 14px;
        }

        .open-btn {
            width: 100%;
        }

        .roulette-wrap, .inventory-wrap, .history-wrap {
            margin-top: 26px;
            border-radius: 28px;
            padding: 24px;
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.08);
        }

        .roulette-head, .inventory-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 18px;
        }

        .roulette-sub {
            color: #94a3b8;
        }

        .roulette-area {
            position: relative;
            height: 190px;
            background: #0b1220;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            overflow: hidden;
        }

        .pointer {
            position: absolute;
            left: 50%;
            top: 0;
            transform: translateX(-50%);
            width: 8px;
            height: 100%;
            background: linear-gradient(180deg, #f59e0b, #ef4444);
            z-index: 5;
            box-shadow: 0 0 24px rgba(245,158,11,0.8);
        }

        .roulette-track {
            display: flex;
            align-items: center;
            gap: 14px;
            height: 100%;
            padding: 0 14px;
            transition: transform 6s cubic-bezier(0.08, 0.7, 0.15, 1);
            will-change: transform;
        }

        .drop-card {
            min-width: 220px;
            height: 140px;
            border-radius: 18px;
            overflow: hidden;
            background: #111827;
            border: 2px solid transparent;
            box-shadow: inset 0 0 20px rgba(255,255,255,0.04);
        }

        .drop-image {
            height: 90px;
            background-size: cover;
            background-position: center;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }

        .drop-info {
            padding: 10px 12px;
        }

        .rarity {
            font-size: 12px;
            font-weight: 800;
            margin-bottom: 5px;
        }

        .drop-name {
            font-size: 15px;
            font-weight: 900;
            margin-bottom: 4px;
            line-height: 1.2;
        }

        .drop-price {
            color: #fbbf24;
            font-weight: 800;
            font-size: 14px;
        }

        .result-box {
            margin-top: 16px;
            min-height: 72px;
            border-radius: 18px;
            padding: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            color: #cbd5e1;
            font-size: 18px;
            font-weight: 800;
        }

        .main-grid {
            display: grid;
            grid-template-columns: 1fr 340px;
            gap: 20px;
        }

        .inventory-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 14px;
        }

        .inventory-item {
            border-radius: 20px;
            overflow: hidden;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
        }

        .inventory-image {
            height: 120px;
            background-size: cover;
            background-position: center;
        }

        .inventory-content {
            padding: 14px;
        }

        .inventory-actions {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            margin-top: 10px;
        }

        .small-btn {
            flex: 1;
            border: none;
            padding: 10px 12px;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 800;
            color: white;
        }

        .empty-box {
            color: #94a3b8;
            border: 1px dashed rgba(255,255,255,0.1);
            border-radius: 18px;
            padding: 18px;
            background: rgba(255,255,255,0.03);
        }

        .history-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .history-item {
            padding: 14px;
            border-radius: 16px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
        }

        .toast {
            position: fixed;
            right: 20px;
            bottom: 20px;
            min-width: 240px;
            max-width: 360px;
            background: rgba(15,23,42,0.96);
            color: white;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 14px 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.35);
            opacity: 0;
            transform: translateY(20px);
            pointer-events: none;
            transition: 0.25s ease;
            z-index: 999;
        }

        .toast.show {
            opacity: 1;
            transform: translateY(0);
        }

        .note {
            color: #94a3b8;
            font-size: 13px;
            margin-top: 14px;
        }

        @media (max-width: 1100px) {
            .hero, .main-grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 700px) {
            .hero-left h1 {
                font-size: 34px;
            }

            .topbar {
                padding: 16px;
            }

            .container {
                padding: 16px;
            }

            .drop-card {
                min-width: 190px;
            }
        }
    </style>
</head>
<body>
    <div class="topbar">
        <div class="logo">CS2 <span>CASES</span></div>

        <div class="top-actions">
            <div class="pill">Баланс: <span class="balance">$<span id="balance">{{ balance }}</span></span></div>
            <button class="btn btn-green" onclick="addBalance()">+100$</button>
            <button class="btn btn-red" onclick="sellAllItems()">Продать всё</button>
        </div>
    </div>

    <div class="container">
        <div class="hero">
            <div class="hero-left">
                <h1>Открывай кейсы.<br>Выбивай топовые скины.</h1>
                <p>
                    Жирная демо-версия case сайта на Flask. Есть анимация открытия, баланс, продажа дропа,
                    история, инвентарь и сохранение через SQLite.
                </p>

                <div class="hero-stats">
                    <div class="stat-box">
                        <div class="stat-title">Кейсов</div>
                        <div class="stat-value">{{ cases|length }}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-title">Предметов в инвентаре</div>
                        <div class="stat-value" id="inventoryCount">{{ inventory|length }}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-title">Последние дропы</div>
                        <div class="stat-value">{{ history|length }}</div>
                    </div>
                </div>
            </div>

            <div class="hero-right">
                <div class="section-title" style="margin-top:0;">Шансы по редкости</div>
                <div class="history-list">
                    <div class="history-item"><span style="color:#9ca3af;font-weight:900;">Обычный</span> — чаще всего</div>
                    <div class="history-item"><span style="color:#60a5fa;font-weight:900;">Редкий</span> — реже</div>
                    <div class="history-item"><span style="color:#c084fc;font-weight:900;">Эпический</span> — хороший дроп</div>
                    <div class="history-item"><span style="color:#fbbf24;font-weight:900;">Легендарный</span> — самый жир</div>
                </div>
                <div class="note">Это демо. Баланс тут виртуальный.</div>
            </div>
        </div>

        <div class="section-title">Кейсы</div>
        <div class="cases-grid">
            {% for case in cases %}
            <div class="case-card">
                <div class="case-glow" style="background: linear-gradient(135deg, {{ case.color1 }}, {{ case.color2 }});">
                    {{ case.name }}
                </div>
                <div class="case-name">{{ case.name }}</div>
                <div class="case-desc">{{ case.description }}</div>
                <div class="case-price">$ {{ case.price }}</div>
                <button class="btn btn-blue open-btn" onclick="openCase({{ case.id }}, '{{ case.name }}')">
                    Открыть кейс
                </button>
            </div>
            {% endfor %}
        </div>

        <div class="roulette-wrap">
            <div class="roulette-head">
                <div>
                    <div class="section-title" style="margin:0;">Открытие кейса</div>
                    <div class="roulette-sub" id="selectedCaseText">Выбери кейс для открытия</div>
                </div>
            </div>

            <div class="roulette-area">
                <div class="pointer"></div>
                <div class="roulette-track" id="rouletteTrack"></div>
            </div>

            <div class="result-box" id="resultBox">Тут появится твой дроп</div>
        </div>

        <div class="main-grid">
            <div class="inventory-wrap">
                <div class="inventory-head">
                    <div class="section-title" style="margin:0;">Инвентарь</div>
                </div>

                <div id="inventoryArea">
                    {% if inventory %}
                    <div class="inventory-grid">
                        {% for item in inventory %}
                        <div class="inventory-item">
                            <div class="inventory-image" style="background-image:url('{{ item.image }}')"></div>
                            <div class="inventory-content">
                                <div class="rarity" style="color:{{ item.color }}">{{ item.rarity_label }}</div>
                                <div class="drop-name">{{ item.name }}</div>
                                <div class="drop-price">$ {{ item.price }}</div>
                                <div class="inventory-actions">
                                    <button class="small-btn" style="background:#dc2626;" onclick="sellItem({{ item.id }})">Продать</button>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <div class="empty-box">Инвентарь пуст. Открой первый кейс.</div>
                    {% endif %}
                </div>
            </div>

            <div class="history-wrap">
                <div class="section-title" style="margin-top:0;">История</div>
                <div id="historyArea">
                    {% if history %}
                    <div class="history-list">
                        {% for item in history %}
                        <div class="history-item">
                            <div class="rarity" style="color:{{ item.color }}">{{ item.rarity_label }}</div>
                            <div class="drop-name">{{ item.name }}</div>
                            <div class="drop-price">$ {{ item.price }}</div>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <div class="empty-box">Пока истории нет.</div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        let spinning = false;

        function showToast(text) {
            const toast = document.getElementById("toast");
            toast.textContent = text;
            toast.classList.add("show");
            setTimeout(() => toast.classList.remove("show"), 2500);
        }

        function playTick() {
            try {
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();

                osc.type = "triangle";
                osc.frequency.value = 650;
                gain.gain.value = 0.02;

                osc.connect(gain);
                gain.connect(ctx.destination);

                osc.start();
                osc.stop(ctx.currentTime + 0.05);
            } catch (e) {}
        }

        function rarityLabel(rarity) {
            if (rarity === "common") return "Обычный";
            if (rarity === "rare") return "Редкий";
            if (rarity === "epic") return "Эпический";
            return "Легендарный";
        }

        function rarityColor(rarity) {
            if (rarity === "common") return "#9ca3af";
            if (rarity === "rare") return "#60a5fa";
            if (rarity === "epic") return "#c084fc";
            return "#fbbf24";
        }

        function createDropCard(item) {
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

        function renderInventory(items) {
            const area = document.getElementById("inventoryArea");
            document.getElementById("inventoryCount").textContent = items.length;

            if (!items.length) {
                area.innerHTML = `<div class="empty-box">Инвентарь пуст. Открой первый кейс.</div>`;
                return;
            }

            area.innerHTML = `
                <div class="inventory-grid">
                    ${items.map(item => `
                        <div class="inventory-item">
                            <div class="inventory-image" style="background-image:url('${item.image}')"></div>
                            <div class="inventory-content">
                                <div class="rarity" style="color:${item.color}">${item.rarity_label}</div>
                                <div class="drop-name">${item.name}</div>
                                <div class="drop-price">$ ${Number(item.price).toFixed(2)}</div>
                                <div class="inventory-actions">
                                    <button class="small-btn" style="background:#dc2626;" onclick="sellItem(${item.id})">Продать</button>
                                </div>
                            </div>
                        </div>
                    `).join("")}
                </div>
            `;
        }

        function renderHistory(items) {
            const area = document.getElementById("historyArea");

            if (!items.length) {
                area.innerHTML = `<div class="empty-box">Пока истории нет.</div>`;
                return;
            }

            area.innerHTML = `
                <div class="history-list">
                    ${items.map(item => `
                        <div class="history-item">
                            <div class="rarity" style="color:${item.color}">${item.rarity_label}</div>
                            <div class="drop-name">${item.name}</div>
                            <div class="drop-price">$ ${Number(item.price).toFixed(2)}</div>
                        </div>
                    `).join("")}
                </div>
            `;
        }

        function buildRoulette(items, winnerIndex) {
            const track = document.getElementById("rouletteTrack");
            track.style.transition = "none";
            track.style.transform = "translateX(0px)";
            track.innerHTML = items.map(createDropCard).join("");

            setTimeout(() => {
                const cardWidth = 234;
                const areaWidth = document.querySelector(".roulette-area").offsetWidth;
                const pointerOffset = areaWidth / 2 - cardWidth / 2;
                const moveX = (winnerIndex * cardWidth) - pointerOffset;

                track.style.transition = "transform 6s cubic-bezier(0.08, 0.7, 0.15, 1)";
                track.style.transform = `translateX(-${moveX}px)`;
                playTick();
            }, 50);
        }

        async function addBalance() {
            const res = await fetch("/add_balance", { method: "POST" });
            const data = await res.json();
            document.getElementById("balance").textContent = Number(data.balance).toFixed(2);
            showToast("Баланс пополнен на $100");
        }

        async function openCase(caseId, caseName) {
            if (spinning) return;

            spinning = true;
            document.querySelectorAll(".open-btn").forEach(btn => btn.disabled = true);
            document.getElementById("selectedCaseText").textContent = "Открывается: " + caseName;
            document.getElementById("resultBox").textContent = "Кейс открывается...";

            const res = await fetch("/open_case", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ case_id: caseId })
            });

            const data = await res.json();

            if (!data.success) {
                document.getElementById("resultBox").textContent = data.error;
                document.querySelectorAll(".open-btn").forEach(btn => btn.disabled = false);
                spinning = false;
                showToast(data.error);
                return;
            }

            buildRoulette(data.roulette_items, data.winner_index);

            setTimeout(() => {
                document.getElementById("resultBox").innerHTML =
                    `Тебе выпало: <span style="color:${data.item.color}; margin-left:6px;">${data.item.name}</span> — $${Number(data.item.price).toFixed(2)}`;

                document.getElementById("balance").textContent = Number(data.balance).toFixed(2);
                renderInventory(data.inventory);
                renderHistory(data.history);

                document.querySelectorAll(".open-btn").forEach(btn => btn.disabled = false);
                spinning = false;
                showToast("Новый дроп: " + data.item.name);
            }, 6200);
        }

        async function sellItem(itemId) {
            const res = await fetch("/sell_item", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ item_id: itemId })
            });

            const data = await res.json();

            if (!data.success) {
                showToast(data.error);
                return;
            }

            document.getElementById("balance").textContent = Number(data.balance).toFixed(2);
            renderInventory(data.inventory);
            showToast("Предмет продан");
        }

        async function sellAllItems() {
            const res = await fetch("/sell_all", {
                method: "POST"
            });

            const data = await res.json();

            if (!data.success) {
                showToast(data.error);
                return;
            }

            document.getElementById("balance").textContent = Number(data.balance).toFixed(2);
            renderInventory(data.inventory);
            showToast("Продано всё на $" + Number(data.total).toFixed(2));
        }
    </script>
</body>
</html>
"""


@app.before_request
def before_request():
    init_db()
    get_or_create_user()


@app.route("/")
def index():
    user_id = get_or_create_user()
    return render_template_string(
        HTML,
        cases=CASES,
        balance=round(get_balance(user_id), 2),
        inventory=get_inventory(user_id),
        history=get_history(user_id)
    )


@app.route("/add_balance", methods=["POST"])
def add_balance_route():
    user_id = get_or_create_user()
    new_balance = add_balance_db(user_id, 100.0)
    return jsonify({"success": True, "balance": round(new_balance, 2)})


@app.route("/open_case", methods=["POST"])
def open_case():
    user_id = get_or_create_user()
    data = request.get_json(silent=True) or {}
    case_id = data.get("case_id")

    selected_case = get_case_by_id(case_id)
    if not selected_case:
        return jsonify({"success": False, "error": "Кейс не найден."})

    balance = get_balance(user_id)
    if balance < selected_case["price"]:
        return jsonify({"success": False, "error": "Недостаточно баланса."})

    new_balance = balance - selected_case["price"]
    set_balance(user_id, new_balance)

    winner = weighted_choice(selected_case["items"])

    roulette_items = [random.choice(selected_case["items"]) for _ in range(30)]
    winner_index = 24
    roulette_items[winner_index] = winner

    add_item_to_inventory(user_id, winner)
    add_history(user_id, winner)

    winner_response = {
        "name": winner["name"],
        "rarity": winner["rarity"],
        "price": winner["price"],
        "image": winner["image"],
        "color": RARITY_COLORS.get(winner["rarity"], "#ffffff"),
        "rarity_label": RARITY_LABELS.get(winner["rarity"], winner["rarity"]),
    }

    return jsonify({
        "success": True,
        "balance": round(new_balance, 2),
        "item": winner_response,
        "roulette_items": roulette_items,
        "winner_index": winner_index,
        "inventory": get_inventory(user_id),
        "history": get_history(user_id)
    })


@app.route("/sell_item", methods=["POST"])
def sell_item_route():
    user_id = get_or_create_user()
    data = request.get_json(silent=True) or {}
    item_id = data.get("item_id")

    if not item_id:
        return jsonify({"success": False, "error": "Не передан item_id."})

    new_balance = sell_inventory_item(user_id, item_id)
    if new_balance is None:
        return jsonify({"success": False, "error": "Предмет не найден."})

    return jsonify({
        "success": True,
        "balance": round(new_balance, 2),
        "inventory": get_inventory(user_id)
    })


@app.route("/sell_all", methods=["POST"])
def sell_all_route():
    user_id = get_or_create_user()
    inventory = get_inventory(user_id)

    if not inventory:
        return jsonify({"success": False, "error": "Инвентарь пуст."})

    total, new_balance = sell_all_inventory(user_id)

    return jsonify({
        "success": True,
        "total": round(total, 2),
        "balance": round(new_balance, 2),
        "inventory": get_inventory(user_id)
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
