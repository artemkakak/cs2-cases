 from flask import Flask, render_template_string, request, jsonify
import random

app = Flask(__name__)

ITEMS = [
    {"name": "AK-47 | Redline", "rarity": "rare", "price": 12.40, "chance": 24},
    {"name": "M4A1-S | Decimator", "rarity": "rare", "price": 15.80, "chance": 20},
    {"name": "AWP | Neo-Noir", "rarity": "epic", "price": 38.50, "chance": 14},
    {"name": "USP-S | Cortex", "rarity": "rare", "price": 9.90, "chance": 18},
    {"name": "Desert Eagle | Printstream", "rarity": "legendary", "price": 65.00, "chance": 8},
    {"name": "Karambit | Doppler", "rarity": "knife", "price": 420.00, "chance": 2},
    {"name": "Butterfly Knife | Fade", "rarity": "knife", "price": 680.00, "chance": 1},
    {"name": "Glock-18 | Vogue", "rarity": "common", "price": 4.50, "chance": 13},
]

RARITY_LABELS = {
    "common": "Обычный",
    "rare": "Редкий",
    "epic": "Эпический",
    "legendary": "Легендарный",
    "knife": "Нож",
}

RARITY_COLORS = {
    "common": "#9aa0a6",
    "rare": "#4aa3ff",
    "epic": "#a970ff",
    "legendary": "#ff5c7a",
    "knife": "#ffc94d",
}

CASES = [
    {
        "id": 1,
        "name": "Neon Case",
        "price": 99,
        "desc": "Яркий кейс с хорошим шансом на дорогие скины.",
        "image": "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=1200&auto=format&fit=crop",
    },
    {
        "id": 2,
        "name": "Shadow Case",
        "price": 149,
        "desc": "Темный стиль и шанс выбить нож.",
        "image": "https://images.unsplash.com/photo-1511512578047-dfb367046420?q=80&w=1200&auto=format&fit=crop",
    },
    {
        "id": 3,
        "name": "Gold Case",
        "price": 199,
        "desc": "Дорогой кейс для жирных дропов.",
        "image": "https://images.unsplash.com/photo-1511882150382-421056c89033?q=80&w=1200&auto=format&fit=crop",
    },
]


def choose_item():
    weighted = []
    for item in ITEMS:
        weighted.extend([item] * item["chance"])
    return random.choice(weighted)


HTML = """
<!doctype html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CS2 Cases</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(180deg, #0d1117, #111827 55%, #0b1020);
            color: #fff;
        }
        .container {
            width: min(1200px, calc(100% - 32px));
            margin: 0 auto;
        }
        header {
            position: sticky;
            top: 0;
            z-index: 50;
            backdrop-filter: blur(10px);
            background: rgba(10, 14, 24, 0.75);
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }
        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 0;
        }
        .logo {
            font-size: 26px;
            font-weight: 800;
            letter-spacing: 1px;
        }
        .logo span { color: #59f; }
        .balance {
            background: linear-gradient(135deg, #1f2937, #111827);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 12px 16px;
            min-width: 160px;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }
        .hero {
            padding: 40px 0 22px;
        }
        .hero-card {
            background: radial-gradient(circle at top right, rgba(73,141,255,0.22), transparent 35%), linear-gradient(135deg, #131a2a, #0f172a);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 28px;
            padding: 36px;
            box-shadow: 0 16px 40px rgba(0,0,0,0.28);
        }
        .hero h1 {
            margin: 0 0 12px;
            font-size: clamp(28px, 4vw, 52px);
        }
        .hero p {
            margin: 0;
            font-size: 18px;
            color: #cbd5e1;
            max-width: 750px;
        }
        .notice {
            margin-top: 16px;
            display: inline-block;
            padding: 10px 14px;
            border-radius: 999px;
            background: rgba(255,255,255,0.06);
            color: #cbd5e1;
            font-size: 14px;
        }
        .cases-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 22px;
            padding: 18px 0 10px;
        }
        .case-card {
            background: #111827;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 16px 35px rgba(0,0,0,0.22);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }
        .case-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 22px 45px rgba(0,0,0,0.28);
        }
        .case-image {
            width: 100%;
            height: 210px;
            object-fit: cover;
            display: block;
        }
        .case-body {
            padding: 18px;
        }
        .case-title {
            font-size: 24px;
            margin: 0 0 8px;
            font-weight: 800;
        }
        .case-desc {
            color: #94a3b8;
            margin: 0 0 18px;
            min-height: 44px;
        }
        .case-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
        }
        .price {
            font-size: 22px;
            font-weight: 800;
            color: #7dd3fc;
        }
        button {
            border: 0;
            cursor: pointer;
            border-radius: 14px;
            padding: 12px 18px;
            font-weight: 800;
            font-size: 15px;
            transition: transform 0.15s ease, opacity 0.15s ease;
        }
        button:hover { transform: scale(1.03); }
        .open-btn {
            background: linear-gradient(135deg, #2563eb, #38bdf8);
            color: white;
        }
        .danger {
            background: linear-gradient(135deg, #ef4444, #f97316);
            color: white;
        }
        .inventory {
            margin: 36px 0 60px;
            background: rgba(15,23,42,0.9);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 28px;
            padding: 28px;
        }
        .section-title {
            margin: 0 0 18px;
            font-size: 30px;
        }
        .result-box {
            margin: 18px 0 22px;
            min-height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            border: 1px dashed rgba(255,255,255,0.12);
            border-radius: 22px;
            background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
            padding: 20px;
        }
        .result-item h3 {
            margin: 0 0 10px;
            font-size: 28px;
        }
        .result-item p {
            margin: 6px 0;
            color: #cbd5e1;
            font-size: 17px;
        }
        .inventory-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 14px;
        }
        .inv-card {
            background: linear-gradient(135deg, #141c2e, #0f172a);
            border: 1px solid rgba(255,255,255,0.08);
            border-left: 5px solid #64748b;
            border-radius: 20px;
            padding: 16px;
        }
        .inv-card h4 {
            margin: 0 0 8px;
            font-size: 18px;
        }
        .inv-card p {
            margin: 4px 0;
            color: #cbd5e1;
        }
        .muted {
            color: #94a3b8;
        }
        .controls {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 18px;
        }
        footer {
            color: #94a3b8;
            text-align: center;
            padding: 22px 0 34px;
        }
        @media (max-width: 700px) {
            .hero-card { padding: 24px; }
            .case-footer { flex-direction: column; align-items: stretch; }
            button { width: 100%; }
        }
    </style>
</head>
<body>
    <header>
        <div class="container topbar">
            <div class="logo">CS2<span>Cases</span></div>
            <div class="balance">
                <div class="muted">Баланс</div>
                <div id="balanceValue">500₴</div>
            </div>
        </div>
    </header>

    <main class="container">
        <section class="hero">
            <div class="hero-card">
                <h1>Сайт открытия кейсов CS2</h1>
                <p>Красивый демо-сайт на Python + Flask. Можно открывать кейсы, получать дропы и собирать инвентарь.</p>
                <div class="notice">Это демо-симулятор без реальных денег, без пополнения и без вывода.</div>
            </div>
        </section>

        <section class="cases-grid">
            {% for case in cases %}
            <article class="case-card">
                <img src="{{ case.image }}" alt="{{ case.name }}" class="case-image">
                <div class="case-body">
                    <h2 class="case-title">{{ case.name }}</h2>
                    <p class="case-desc">{{ case.desc }}</p>
                    <div class="case-footer">
                        <div class="price">{{ case.price }}₴</div>
                        <button class="open-btn" onclick="openCase({{ case.id }}, {{ case.price }})">Открыть кейс</button>
                    </div>
                </div>
            </article>
            {% endfor %}
        </section>

        <section class="inventory">
            <h2 class="section-title">Результат открытия</h2>
            <div class="result-box" id="resultBox">
                <div class="muted">Тут будет твой дроп после открытия кейса</div>
            </div>

            <div class="controls">
                <button class="danger" onclick="clearInventory()">Очистить инвентарь</button>
            </div>

            <h2 class="section-title" style="margin-top: 28px;">Инвентарь</h2>
            <div class="inventory-grid" id="inventoryGrid">
                <div class="muted">Пока пусто. Открой первый кейс.</div>
            </div>
        </section>
    </main>

    <footer>
        Сделано на Python Flask • один файл • легко менять дизайн, кейсы и дроп
    </footer>

    <script>
        let balance = 500;
        let inventory = [];

        function updateBalance() {
            document.getElementById('balanceValue').textContent = balance + '₴';
        }

        function renderInventory() {
            const grid = document.getElementById('inventoryGrid');
            if (inventory.length === 0) {
                grid.innerHTML = '<div class="muted">Пока пусто. Открой первый кейс.</div>';
                return;
            }

            grid.innerHTML = inventory.map(item => `
                <div class="inv-card" style="border-left-color:${item.color}">
                    <h4>${item.name}</h4>
                    <p>Редкость: ${item.rarity}</p>
                    <p>Цена: ${item.price}$</p>
                </div>
            `).join('');
        }

        function setResult(item) {
            document.getElementById('resultBox').innerHTML = `
                <div class="result-item">
                    <h3 style="color:${item.color}">${item.name}</h3>
                    <p>Редкость: ${item.rarity}</p>
                    <p>Примерная цена: ${item.price}$</p>
                </div>
            `;
        }

        async function openCase(caseId, casePrice) {
            if (balance < casePrice) {
                alert('Недостаточно баланса');
                return;
            }

            try {
                const response = await fetch('/open_case', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ case_id: caseId })
                });

                const data = await response.json();
                balance -= casePrice;
                updateBalance();
                inventory.unshift(data.item);
                setResult(data.item);
                renderInventory();
            } catch (error) {
                alert('Ошибка открытия кейса');
            }
        }

        function clearInventory() {
            inventory = [];
            renderInventory();
            document.getElementById('resultBox').innerHTML = '<div class="muted">Тут будет твой дроп после открытия кейса</div>';
        }

        updateBalance();
        renderInventory();
    </script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML, cases=CASES)


@app.route("/open_case", methods=["POST"])
def open_case():
    item = choose_item()
    return jsonify({
        "item": {
            "name": item["name"],
            "rarity": RARITY_LABELS[item["rarity"]],
            "price": item["price"],
            "color": RARITY_COLORS[item["rarity"]],
        }
    })


if __name__ == "__main__":
    app.run(debug=True)
