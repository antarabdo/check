import telebot
from curl_cffi import requests
import re
from datetime import datetime
import urllib3

# Bach n-7iyed s-da3 dyal SSL
urllib3.disable_warnings()

# --- CONFIG ---
TOKEN = "8510274862:AAGkSIrvwONolWc_6gynRbQw1AUb_iMhUus"
bot = telebot.TeleBot(TOKEN)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"

# --- FUNCTIONS ---

def get_all_live_categories(api_url):
    try:
        r = requests.get(f"{api_url}&action=get_live_categories", impersonate="chrome110", timeout=10, verify=False).json()
        if isinstance(r, list) and len(r) > 0:
            formatted_cats = ""
            for i, c in enumerate(r, 1):
                formatted_cats += f"  {i:02d} ➔ 📁 {c['category_name']}\n"
            return formatted_cats, len(r)
    except: pass
    return "None", 0

def check_xtream_master(url):
    try:
        match = re.search(r'(http[s]?://[^/:]+[:\d]*).*username=([^& \n]+)&password=([^& \n]+)', url)
        if not match: return None
        base, user, pw = match.groups()
        api_url = f"{base}/player_api.php?username={user}&password={pw}"
        
        # 1. Login Check
        r = requests.get(api_url, impersonate="chrome110", timeout=12, verify=False).json()
        u = r.get('user_info', {})
        if u.get('auth') == 0: return None

        # 2. Real Stream Check (IP Lock Test)
        test_stream = f"{base}/live/{user}/{pw}/1.ts"
        try:
            # Check gha l-headers bach n-choufu wach l-ishtiirak kiy-at7i s-sora
            r_stream = requests.head(test_stream, impersonate="chrome110", timeout=8, verify=False)
            stream_status = "✅ **STREAM WORKING**" if r_stream.status_code == 200 else "❌ **STREAM FAILED (IP Locked)**"
        except:
            stream_status = "❌ **STREAM ERROR (Blocked)**"

        # 3. Categories & Expiry
        exp = u.get('exp_date')
        expiry = datetime.fromtimestamp(int(exp)).strftime('%d/%m/%Y') if exp and exp != "null" else "∞ Unlimited"
        cat_list, total_cats = get_all_live_categories(api_url)

        msg = (
            f"💎 **IPTV REAL SCAN** 💎\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **User:** `{user}`\n"
            f"🔑 **Pass:** `{pw}`\n"
            f"⏳ **Exp:** `{expiry}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎬 **Result:** {stream_status}\n"
            f"🚀 **Conn:** `{u.get('active_cons', '0')}/{u.get('max_connections', '0')}`\n"
            f"📊 **Status:** `{u.get('status', 'Active').upper()}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📺 **LIVE TV FOLDERS [{total_cats}]**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{cat_list}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 **M3U Link:**\n`{url}|User-Agent=VLC/3.0.18`"
        )
        return msg
    except: return None

# --- BOT HANDLERS ---

@bot.message_handler(commands=['start'])
def welcome(m):
    bot.reply_to(m, "🦁 **IPTV REAL MASTER V20**\n\nSift link Xtream bach n-checki lik l-Login o s-Sora (Stream) f deqqa wa7da!")

@bot.message_handler(content_types=['text'])
def handle_msg(m):
    text = m.text
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    if not urls: return
    
    bot.send_chat_action(m.chat.id, 'typing')
    found = False
    for u in list(set(urls)):
        if "username=" in u:
            res = check_xtream_master(u)
            if res:
                # Handle Telegram message length limit
                if len(res) > 4000:
                    bot.send_message(m.chat.id, res[:4000], parse_mode="Markdown")
                else:
                    bot.send_message(m.chat.id, res, parse_mode="Markdown")
                found = True
    
    if not found and "http" in text:
        bot.reply_to(m, "❌ Dead oula IP Locked.")

# --- START BOT ---
print("[*] Bot V20 is Running... Sift /start f Telegram.")
bot.polling(none_stop=True)