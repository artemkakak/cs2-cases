from flask import Flask, render_template_string, request, jsonify, session
import random
import os

app = Flask(__name__)
app.secret_key = "cs2_cases_demo_secret_key_123"

ITEMS = [
    {"name": "Glock-18 | Vogue", "rarity": "common", "price": 4.50, "chance": 28},
    {"name": "USP-S | Cortex", "rarity": "common", "price": 7.90, "chance": 24},
    {"name": "AK-47 | Redline", "rarity": "rare", "price": 14.20, "chance": 18},
    {"name": "M4A1-S | Decimator", "rarity": "rare", "price": 18.80, "chance": 14},
    {"name": "AWP | Neo-Noir", "rarity": "epic", "price": 39.50, "chance": 8},
    {"name": "Desert Eagle | Printstream", "rarity": "epic", "price": 62.00, "chance": 5},
    {"name": "Karambit | Doppler", "rarity": "legendary", "price": 420.00, "chance": 2},
    {"name": "Butterfly Knife | Fade", "rarity": "legendary", "price": 680.00, "chance": 1},
]

RARITY_LABELS = {
    "common": "Обычный",
    "rare": "Редкий",
    "epic": "Эпический",
    "legendary": "Легендарный"
}

RARITY_COLORS = {
    "common": "#9aa0a6",
    "rare": "#4aa3ff",
    "epic": "#a970ff",
    "legendary": "#ffb84d"
}

CASES = [
    {
        "id": 1,
        "name": "Neon Case",
        "price": 10,
        "color": "#6d28d9",
        "items": ITEMS
    },
    {
        "id": 2,
        "name": "Inferno Case",
        "price": 25,
        "color": "#dc2626",
        "items": ITEMS
    },
    {
        "id": 3,
        "name": "Elite Case",
        "price": 50,
        "color": "#f59e0b",
        "items": ITEMS
    }
]


HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CS2 Cases</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, sans-serif; }
        body {
            background: linear-gradient(180deg, #0b1020, #111827);
            color: white;
            min-height: 100vh;
        }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px 24px;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.03);
            position: sticky;
            top: 0;
            z-index: 10;
            backdrop-filter: blur(10px);
        }

        .logo {
            font-size: 28px;
            font-weight: 800;
            letter-spacing: 1px;
        }

        .logo span {
            color: #60a5fa;
        }

        .balance-box {
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(255,255,255,0.05);
            padding: 10px 14px;
            border-radius: 14px;
        }

        .balance {
            font-size: 18px;
            font-weight: bold;
            color: #fbbf24;
        }

        .add-btn {
            background: #22c55e;
            border: none;
            color: white;
            padding: 10px 14px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
        }

        .container {
            max-width: 1320px;
            margin: 0 auto;
            padding: 24px;
        }

        .hero {
            margin-top: 10px;
            padding: 28px;
            border-radius: 24px;
            background: linear-gradient(135deg, rgba(96,165,250,0.15), rgba(168,85,247,0.12));
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 20px 50px rgba(0,0,0,0.25);
        }

        .hero h1 {
            font-size: 42px;
            margin-bottom: 10px;
        }

        .hero p {
            color: #cbd5e1;
            font-size: 16px;
        }

        .cases-title, .inventory-title {
            margin: 28px 0 14px;
            font-size: 24px;
            font-weight: 800;
        }

        .cases-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 18px;
        }

        .case-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 22px;
            padding: 18px;
            box-shadow: 0 12px 24px rgba(0,0,0,0.2);
            transition: 0.2s ease;
        }

        .case-card:hover {
            transform: translateY(-4px);
        }

        .case-preview {
            height: 140px;
            border-radius: 18px;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            font-weight: 900;
            box-shadow: inset 0 0 20px rgba(255,255,255,0.08);
        }

        .case-name {
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 8px;
        }

        .case-price {
            color: #fbbf24;
            font-size: 18px;
            margin-bottom: 14px;
        }

        .open-btn {
            width: 100%;
            border: none;
            background: linear-gradient(90deg, #2563eb, #7c3aed);
            color: white;
            padding: 14px;
            border-radius: 14px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }

        .open-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .roulette-wrap {
            margin-top: 28px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 24px;
            padding: 24px;
            overflow: hidden;
        }

        .roulette-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
            gap: 12px;
            flex-wrap: wrap;
        }

        .roulette-title {
            font-size: 24px;
            font-weight: 800;
        }

        .selected-case {
            color: #cbd5e1;
        }

        .roulette-area {
            position: relative;
            overflow: hidden;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.08);
            background: #0f172a;
            height: 170px;
        }

        .pointer {
            position: absolute;
            left: 50%;
            top: 0;
            transform: translateX(-50%);
            width: 6px;
            height: 100%;
            background: linear-gradient(180deg, #f59e0b, #ef4444);
            z-index: 3;
            box-shadow: 0 0 20px rgba(245,158,11,0.8);
        }

        .roulette-track {
            display: flex;
            align-items: center;
            height: 100%;
            gap: 14px;
            padding: 0 14px;
            transition: transform 5s cubic-bezier(0.08, 0.7, 0.15, 1);
            will-change: transform;
        }

        .skin-card {
            min-width: 190px;
            height: 120px;
            border-radius: 16px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 14px;
            border: 2px solid transparent;
            background: #111827;
            box-shadow: inset 0 0 20px rgba(255,255,255,0.03);
        }

        .skin-rarity {
            font-size: 12px;
            opacity: 0.9;
            margin-bottom: 8px;
            font-weight: bold;
        }

        .skin-name {
            font-size: 16px;
            font-weight: 800;
            line-height: 1.25;
            margin-bottom: 8px;
        }

        .skin-price {
            color: #fbbf24;
            font-size: 14px;
            font-weight: bold;
        }

        .result-box {
            margin-top: 18px;
            padding: 18px;
            border-radius: 18px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            min-height: 84px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: #cbd5e1;
            font-size: 18px;
            font-weight: bold;
        }

        .inventory-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
            margin-top: 10px;
        }

        .inventory-item {
            border-radius: 18px;
            padding: 16px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
        }

        .inventory-empty {
            color: #94a3b8;
            background: rgba(255,255,255,0.03);
            border: 1px dashed rgba(255,255,255,0.12);
            padding: 18px;
            border-radius: 18px;
        }

        .footer-note {
            margin-top: 24px;
            color: #94a3b8;
            font-size: 14px;
        }

        @media (max-width: 700px) {
            .hero h1 { font-size: 30px; }
            .roulette-area { height: 150px; }
            .skin-card { min-width: 170px; height: 108px; }
        }
    </style>
</head>
<body>
    <div class="topbar">
        <div class="logo">CS2 <span>CASES</span></div>
        <div class="balance-box">
            <div class="balance">Баланс: $<span id="balance">{{ balance }}</span></div>
            <button class="add-btn" onclick="addBalance()">+100$</button>
        </div>
    </div>

    <div class="container">
        <div class="hero">
            <h1>Открывай кейсы и выбивай дорогие скины</h1>
            <p>Демо-версия сайта. Пока без доната, только баланс, кейсы, анимация открытия и инвентарь.</p>
        </div>

        <div class="cases-title">Кейсы</div>
        <div class="cases-grid">
            {% for case in cases %}
            <div class="case-card">
                <div class="case-preview" style="background: linear-gradient(135deg, {{ case.color }}, #111827);">
                    {{ case.name }}
                </div>
                <div class="case-name">{{ case.name }}</div>
                <div class="case-price">$ {{ case.price }}</div>
                <button class="open-btn" onclick="openCase({{ case.id }}, '{{ case.name }}')">Открыть</button>
            </div>
            {% endfor %}
        </div>

        <div class="roulette-wrap">
            <div class="roulette-header">
                <div class="roulette-title">Анимация открытия</div>
                <div class="selected-case" id="selectedCaseText">Выбери кейс</div>
            </div>

            <div class="roulette-area">
                <div class="pointer"></div>
                <div class="roulette-track" id="rouletteTrack"></div>
            </div>

            <div class="result-box" id="resultBox">Здесь появится выпавший скин</div>
        </div>

        <div class="inventory-title">Инвентарь</div>
        <div id="inventoryArea">
            {% if inventory %}
                <div class="inventory-grid">
                    {% for item in inventory %}
                    <div class="inventory-item" style="border-left: 4px solid {{ item.color }}">
                        <div class="skin-rarity" style="color: {{ item.color }}">{{ item.rarity_label }}</div>
                        <div class="skin-name">{{ item.name }}</div>
                        <div class="skin-price">$ {{ item.price }}</div>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="inventory-empty">Инвентарь пуст. Открой первый кейс.</div>
            {% endif %}
        </div>

        <div class="footer-note">
            Демо для обучения. Позже можно добавить базу данных, аккаунты, продажу скинов, пополнение, топы и красивые картинки скинов.
        </div>
    </div>

    <script>
        let spinning = false;

        function rarityColor(rarity) {
            if (rarity === "common") return "#9aa0a6";
            if (rarity === "rare") return "#4aa3ff";
            if (rarity === "epic") return "#a970ff";
            return "#ffb84d";
        }

        function rarityLabel(rarity) {
            if (rarity === "common") return "Обычный";
            if (rarity === "rare") return "Редкий";
            if (rarity === "epic") return "Эпический";
            return "Легендарный";
        }

        function createSkinCard(item) {
            const color = rarityColor(item.rarity);
            const label = rarityLabel(item.rarity);
            return `
                <div class="skin-card" style="border-color:${color}">
                    <div class="skin-rarity" style="color:${color}">${label}</div>
                    <div class="skin-name">${item.name}</div>
                    <div class="skin-price">$ ${item.price}</div>
                </div>
            `;
        }

        function buildRoulette(items, winnerIndex) {
            const track = document.getElementById("rouletteTrack");
            track.style.transition = "none";
            track.style.transform = "translateX(0px)";
            track.innerHTML = "";

            const fullList = [];
            for (let i = 0; i < items.length; i++) {
                fullList.push(items[i]);
            }

            track.innerHTML = fullList.map(createSkinCard).join("");

            setTimeout(() => {
                const cardWidth = 204;
                const areaWidth = document.querySelector(".roulette-area").offsetWidth;
                const pointerOffset = areaWidth / 2 - cardWidth / 2;
                const moveX = (winnerIndex * cardWidth) - pointerOffset;

                track.style.transition = "transform 5s cubic-bezier(0.08, 0.7, 0.15, 1)";
                track.style.transform = `translateX(-${moveX}px)`;
            }, 50);
        }

        function renderInventory(items) {
            const area = document.getElementById("inventoryArea");

            if (!items.length) {
                area.innerHTML = '<div class="inventory-empty">Инвентарь пуст. Открой первый кейс.</div>';
                return;
            }

            area.innerHTML = `
                <div class="inventory-grid">
                    ${items.map(item => `
                        <div class="inventory-item" style="border-left:4px solid ${item.color}">
                            <div class="skin-rarity" style="color:${item.color}">${item.rarity_label}</div>
                            <div class="skin-name">${item.name}</div>
                            <div class="skin-price">$ ${item.price}</div>
                        </div>
                    `).join("")}
                </div>
            `;
        }

        async function addBalance() {
            const res = await fetch("/add_balance", {
                method: "POST"
            });
            const data = await res.json();
            document.getElementById("balance").textContent = data.balance.toFixed(2);
        }

        async function openCase(caseId, caseName) {
            if (spinning) return;

            const buttons = document.querySelectorAll(".open-btn");
            buttons.forEach(btn => btn.disabled = true);

            spinning = true;
            document.getElementById("selectedCaseText").textContent = "Открывается: " + caseName;
            document.getElementById("resultBox").textContent = "Кейс открывается...";

            const res = await fetch("/open_case", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({case_id: caseId})
            });

            const data = await res.json();

            if (!data.success) {
                document.getElementById("resultBox").textContent = data.error;
                buttons.forEach(btn => btn.disabled = false);
                spinning = false;
                return;
            }

            buildRoulette(data.roulette_items, data.winner_index);

            setTimeout(() => {
                document.getElementById("resultBox").innerHTML =
                    `Тебе выпало: <span style="color:${data.item.color}; margin-left:6px;">${data.item.name}</span> — $${data.item.price}`;
                document.getElementById("balance").textContent = data.balance.toFixed(2);
                renderInventory(data.inventory);
                buttons.forEach(btn => btn.disabled = false);
                spinning = false;
            }, 5200);
        }
    </script>
</body>
</html>
"""


def init_user():
    if "balance" not in session:
        session["balance"] = 100.0
    if "inventory" not in session:
        session["inventory"] = []


def weighted_choice(items):
    expanded = []
    for item in items:
        expanded.extend([item] * item["chance"])
    return random.choice(expanded)


def build_inventory_with_colors():
    inventory = session.get("inventory", [])
    result = []
    for item in inventory:
        copy_item = dict(item)
        copy_item["color"] = RARITY_COLORS.get(copy_item["rarity"], "#ffffff")
        copy_item["rarity_label"] = RARITY_LABELS.get(copy_item["rarity"], copy_item["rarity"])
        result.append(copy_item)
    return result


@app.route("/")
def index():
    init_user()
    return render_template_string(
        HTML,
        cases=CASES,
        balance=round(session["balance"], 2),
        inventory=build_inventory_with_colors()
    )


@app.route("/add_balance", methods=["POST"])
def add_balance():
    init_user()
    session["balance"] += 100.0
    session.modified = True
    return jsonify({"balance": round(session["balance"], 2)})


@app.route("/open_case", methods=["POST"])
def open_case():
    init_user()
    data = request.get_json()
    case_id = data.get("case_id")

    selected_case = next((c for c in CASES if c["id"] == case_id), None)
    if not selected_case:
        return jsonify({"success": False, "error": "Кейс не найден."})

    if session["balance"] < selected_case["price"]:
        return jsonify({"success": False, "error": "Недостаточно баланса."})

    session["balance"] -= selected_case["price"]

    winner = weighted_choice(selected_case["items"])

    roulette_items = []
    for _ in range(28):
        roulette_items.append(random.choice(selected_case["items"]))

    winner_index = 22
    roulette_items[winner_index] = winner

    session["inventory"].insert(0, winner)
    session.modified = True

    winner_response = dict(winner)
    winner_response["color"] = RARITY_COLORS.get(winner["rarity"], "#ffffff")
    winner_response["rarity_label"] = RARITY_LABELS.get(winner["rarity"], winner["rarity"])

    return jsonify({
        "success": True,
        "balance": round(session["balance"], 2),
        "item": winner_response,
        "roulette_items": roulette_items,
        "winner_index": winner_index,
        "inventory": build_inventory_with_colors()
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
