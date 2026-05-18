import telebot
from curl_cffi import requests
import re
import json
from datetime import datetime
from flask import Flask
from threading import Thread
import urllib3

urllib3.disable_warnings()

# --- CONFIG ---
TOKEN = "8510274862:AAGkSIrvwONolWc_6gynRbQw1AUb_iMhUus"
bot = telebot.TeleBot(TOKEN)

# Keywords dyal l-zbel (Aflam o Mosalsalat) bach n-ms7ouhoum
VOD_KEYWORDS = ["MOVIE", "FILM", "SERIE", "VOD", "NETFLIX", "CINEMA", "4K RELAX", "V.O.D", "SEASON", "2024", "2025"]

# --- KEEP ALIVE WEB SERVER ---
app = Flask('')
@app.route('/')
def home(): return "IPTV Bot is Alive!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- CHECKER LOGIC ---

def get_live_folders(api_url):
    """Jbed gha l-folders dyal l-boldan o s-sport"""
    try:
        r = requests.get(f"{api_url}&action=get_live_categories", impersonate="chrome110", timeout=10, verify=False).json()
        if isinstance(r, list):
            live_only = []
            for c in r:
                name = c.get('category_name', '')
                # Filter: Khlli gha l-folders li ma-fihomch kelmet Movie/Serie
                if not any(k in name.upper() for k in VOD_KEYWORDS):
                    live_only.append(name)
            return " ➔ ".join(live_only[:25]), len(live_only) # Khod max 25 bach message may-kounch t-wiil
    except: pass
    return "None", 0

def check_link(url):
    try:
        match = re.search(r'(https?://[^/:]+[:\d]*).*username=([^& \n]+)&password=([^& \n]+)', url)
        if not match: return None

        base, user, pw = match.groups()
        api_url = f"{base}/player_api.php?username={user}&password={pw}"

        # TLS Bypass Shield 885
        r = requests.get(api_url, impersonate="chrome110", timeout=15, verify=False).json()
        u = r.get('user_info', {})

        if u.get('auth') == 1:
            # Account WORKING!
            exp = u.get('exp_date')
            expiry = datetime.fromtimestamp(int(exp)).strftime('%d/%m/%Y') if exp and exp != "null" else "Unlimited"

            # Capture Live Categories Only
            folders_str, folders_count = get_live_folders(api_url)

            msg = (
                f"💎 **IPTV MASTER HIT** 💎\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **User:** `{user}`\n"
                f"🔑 **Pass:** `{pw}`\n"
                f"⏳ **Expiry:** `{expiry}`\n"
                f"🚀 **Conn:** `{u.get('active_cons', '0')}/{u.get('max_connections', '0')}`\n"
                f"📊 **Status:** `{u.get('status', 'Active').upper()}`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📺 **LIVE TV FOLDERS [{folders_count}]**\n"
                f"📁 {folders_str} ...\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🌐 **Server:** {base}\n"
                f"🔗 **M3U Link:**\n`{url}|User-Agent=VLC/3.0.18`"
            )
            return msg
        return None
    except: return None

# --- BOT HANDLERS ---

@bot.message_handler(commands=['start'])
def welcome(m):
    bot.reply_to(m, "🦁 **IPTV LIVE SCAPER BOT V25**\n\nSift link Xtream oula 3ram dyal l-hadra fiha links, ghan-frez lik gha l-ishtiira-kat dyal l-3rab o s-sport!")

@bot.message_handler(content_types=['text'])
def handle_text(m):
    text = m.text
    # Jbed ga3 l-links mn l-messaage
    urls = re.findall(r'(https?://[^\s]+)', text)
    if not urls: return

    bot.send_chat_action(m.chat.id, 'typing')
    found = False

    for u in list(set(urls)):
        if "username=" in u.lower():
            res = check_link(u)
            if res:
                # Handle long messages
                if len(res) > 4000: bot.send_message(m.chat.id, res[:4000], parse_mode="Markdown")
                else: bot.send_message(m.chat.id, res, parse_mode="Markdown")
                found = True

    if not found and "http" in text.lower():
        bot.reply_to(m, "❌ Ga3 l-links li sift-ti Dead oula IP Locked.")

# --- START ---
if __name__ == "__main__":
    keep_alive() # Ch3el l-web server dyal Flask
    print("[*] Bot V25 is Running... Ready for UptimeRobot.")
    bot.polling(none_stop=True)
