import os
import json
from urllib.parse import urlunparse
import requests

TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
DATA_FILE = "data/predictions.json"

def send_msg(text):
    if not TOKEN or not CHAT_ID:
        print("Mungojnë çelësat e Telegram!")
        return
    url = urlunparse(("https", "api.telegram.org", "/bot" + TOKEN + "/sendMessage", "", "", ""))
    requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10)

def main():
    if not os.path.exists(DATA_FILE):
        print("Nuk u gjet data/predictions.json")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Përshtatet me strukturën e JSON-it të faqes (listë ose dictionary me 'matches'/'predictions')
    matches = data if isinstance(data, list) else data.get("matches", data.get("predictions", []))
    if not matches:
        print("Nuk ka ndeshje sot.")
        return

    lines = ["⚽ <b>PARASHIKIMET & VALUE BETS E DITËS</b>\n"]
    count = 0

    for m in matches:
        home = m.get("home_team") or m.get("home", "")
        away = m.get("away_team") or m.get("away", "")
        league = m.get("league", "")
        tip = m.get("tip") or m.get("prediction") or m.get("advice", "")
        odds = m.get("odds") or m.get("best_odds") or m.get("odd", "")
        is_value = m.get("is_value") or m.get("value_bet") or m.get("vip", False)

        if not home or not away:
            continue

        badge = "💎 <b>VALUE BET</b> | " if is_value else "📌 "
        line = badge + "<b>" + str(home) + " vs " + str(away) + "</b>"
        if league:
            line += " (" + str(league) + ")"
        if tip:
            line += "\n   👉 Zgjedhja: <b>" + str(tip) + "</b>"
        if odds:
            line += " | Kuota: <b>" + str(odds) + "</b>"

        lines.append(line + "\n")
        count += 1

        # Dërgo mesazhin çdo 12 ndeshje që të mos kalojë limitin e karaktereve të Telegramit
        if count % 12 == 0:
            send_msg("\n".join(lines))
            lines = []

    if lines:
        send_msg("\n".join(lines))

    print("U dërguan në Telegram", count, "ndeshje.")

if __name__ == "__main__":
    main()
