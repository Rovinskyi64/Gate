import os
import time
import requests

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "15"))

API_URL = "https://www.gate.com/apiw/v2/spot_loan/collateral/markets?limit=1000"
old_tokens = set()

def send_message(text):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("[WARN] TG credentials not set.")
        return
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "HTML"})
        if r.status_code != 200:
            print(f"Telegram send error: {r.status_code} {r.text}")
    except Exception as e:
        print("Telegram error:", e)

def fetch_tokens():
    try:
        r = requests.get(API_URL, timeout=10)
        if r.status_code != 200:
            print(f"Fetch error {r.status_code}: {r.text}")
            return []
        data = r.json()
        return data.get("data", {}).get("data", [])
    except Exception as e:
        print("Fetch error:", e)
        return []

def monitor_loop():
    global old_tokens
    print(f"Bot + monitor started (POOL, only new coins). Poll interval: {POLL_INTERVAL}s")
    send_message("🚀 Gate.io Lending Watcher запущено.")
    while True:
        tokens = fetch_tokens()
        if not tokens:
            time.sleep(POLL_INTERVAL)
            continue

        new_set = set([t["currency"] for t in tokens])
        new_coins = new_set - old_tokens

        if new_coins:
            msg = "<b>🆕 Нові токени у Lending пулі:</b>\n"
            for t in tokens:
                if t["currency"] in new_coins:
                    msg += f"{t['currency']}: {t['borrowable_amount_usdt']} USDT\n"
            send_message(msg)

        old_tokens = new_set
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    monitor_loop()
