    
import telebot
import requests
import sqlite3
from telebot import types
import os

# ✅ Bot token
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# ✅ Database setup
conn = sqlite3.connect('data.db', check_same_thread=False)
with conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        credit INTEGER DEFAULT 0,
        unlimited INTEGER DEFAULT 0
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS redeem_codes (
        code TEXT PRIMARY KEY,
        value INTEGER,
        unlimited INTEGER DEFAULT 0,
        used_by TEXT DEFAULT ''
    )''')

# ✅ Redeem codes: 1 Unlimited, 9 with 20 credit
codes = [
    ("RAJPUTUNLIMITED", 0, 1),
    ("RAJPUT20A", 20, 0),
    ("RAJPUT20B", 20, 0),
    ("RAJPUT20C", 20, 0),
    ("RAJPUT20D", 20, 0),
    ("RAJPUT20E", 20, 0),
    ("RAJPUT20F", 20, 0),
    ("RAJPUT20G", 20, 0),
    ("RAJPUT20H", 20, 0),
    ("RAJPUT20I", 20, 0),
]
with conn:
    for code, value, unlimited in codes:
        conn.execute("INSERT OR IGNORE INTO redeem_codes (code, value, unlimited) VALUES (?, ?, ?)", (code, value, unlimited))

# ✅ Channel/group join check
REQUIRED_IDS = [-1002704011071, -1002803224315, -1002760898725]
API_URL = 'https://glonova.in/Iwowoo3o.php/?num='

# ✅ User Functions
def init_user(uid):
    with conn:
        conn.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (uid,))

def get_credits(uid):
    row = conn.execute("SELECT credit FROM users WHERE id=?", (uid,)).fetchone()
    return row[0] if row else 0

def is_unlimited(uid):
    row = conn.execute("SELECT unlimited FROM users WHERE id=?", (uid,)).fetchone()
    return row[0] == 1 if row else False

def deduct(uid):
    if is_unlimited(uid): return True
    if get_credits(uid) > 0:
        with conn:
            conn.execute("UPDATE users SET credit=credit-1 WHERE id=?", (uid,))
        return True
    return False

def add_credit(uid, amount):
    with conn:
        conn.execute("UPDATE users SET credit=credit+? WHERE id=?", (amount, uid))

def set_unlimited(uid):
    with conn:
        conn.execute("UPDATE users SET unlimited=1 WHERE id=?", (uid,))

def check_joined(uid):
    for cid in REQUIRED_IDS:
        try:
            member = bot.get_chat_member(cid, uid)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True

# ✅ Start command
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.is_bot:
        return
    uid = message.from_user.id
    init_user(uid)

    if not check_joined(uid):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel 1", url="https://t.me/HACKrhaibahihqckr"))
        markup.add(types.InlineKeyboardButton("🔗 Join Group 2", url="https://t.me/+YP3uSVPdcJ0xYjM9"))
        markup.add(types.InlineKeyboardButton("🎬 Join Channel 3", url="https://t.me/+9Im8_gCDFq9jMDhl"))
        markup.add(types.InlineKeyboardButton("✅ Joined All - Verify", callback_data="verify"))
        try:
            bot.send_message(uid, "🔒 Bot use karne ke liye sabhi channel/group join karo.", reply_markup=markup)
        except telebot.apihelper.ApiTelegramException as e:
            if "bots can't send messages to bots" in str(e):
                pass
            else:
                raise
        return

    main_menu(message)

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify_join(call):
    if check_joined(call.from_user.id):
        main_menu(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ Abhi bhi sab join nahi kiya!")

# ✅ Main Menu
def main_menu(msg):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📱 Number Info", "🚗 Vehicle Info")
    kb.row("🎫 Redeem", "💳 Balance")
    kb.row("🔗 Referral", "👤 Contact Admin")
    bot.send_message(msg.chat.id, "✅ Access granted. Select an option:", reply_markup=kb)

# ✅ /redeem command
@bot.message_handler(commands=['redeem'])
def ask_code(message):
    bot.send_message(message.chat.id, "🔢 Apna Redeem Code bheje:")
    bot.register_next_step_handler(message, handle_redeem)

def handle_redeem(message):
    code = message.text.strip()
    uid = message.from_user.id
    row = conn.execute("SELECT * FROM redeem_codes WHERE code=?", (code,)).fetchone()
    if not row:
        bot.send_message(uid, "❌ Invalid Code")
        return

    used_by = row[3]
    if str(uid) in used_by:
        bot.send_message(uid, "⚠️ Ye code aap pehle hi use kar chuke ho.")
        return

    if row[2] == 1:
        set_unlimited(uid)
        msg = "✅ Code Applied: UNLIMITED - Lifetime VIP"
    else:
        add_credit(uid, row[1])
        msg = f"✅ {row[1]} credit add kiye gaye. /balance use kare."

    new_used = used_by + f" {uid}"
    with conn:
        conn.execute("UPDATE redeem_codes SET used_by=? WHERE code=?", (new_used, code))

    bot.send_message(uid, msg)

# ✅ /balance command
@bot.message_handler(commands=['balance'])
def balance(message):
    uid = message.from_user.id
    if is_unlimited(uid):
        bot.send_message(uid, "💠 Aapke paas UNLIMITED VIP access hai!")
    else:
        bot.send_message(uid, f"💰 Credit bache hain: {get_credits(uid)}")

# ✅ /referral command
@bot.message_handler(commands=['referral'])
def referral(message):
    uid = message.from_user.id
    link = f"https://t.me/{bot.get_me().username}?start={uid}"
    bot.send_message(uid, f"🔗 Doston ko bot bhejo aur free credit pao!\n💸 Invite Link: {link}\n🎁 Har referral pe reward!")

# ✅ Manual buttons
@bot.message_handler(func=lambda m: m.text == "📱 Number Info")
def ask_number(message):
    uid = message.from_user.id
    if not is_unlimited(uid) and get_credits(uid) <= 0:
        bot.send_message(uid, "❌ यह सेवा केवल VIP यूज़र्स के लिए है।\n🎁 /redeem या 🔗 Referral से क्रेडिट पाएं।")
        return
    bot.send_message(uid, "📞 Number bhejo:")
    bot.register_next_step_handler(message, handle_number)

def handle_number(message):
    uid = message.from_user.id
    if not deduct(uid):
        bot.send_message(uid, "❌ क्रेडिट खत्म हो चुके हैं।")
        return
    num = message.text.strip()
    try:
        res = requests.get(API_URL + num)
        if res.status_code == 200:
            data = res.json()
            if data.get("success"):
                out = data.get("data", {}).get("Requested Number Results", [])
                msg = f"🎯 OSINT Report for `{num}`"
                for i, person in enumerate(out[:3], 1):
                    msg += f"\n\n👤 Person {i}"
                    for k, v in person.items():
                        msg += f"\n〄 {k}: `{v}`"
                msg += "\n\n🛡️ Powered by @HACKER722727"
                bot.send_message(uid, msg, parse_mode='Markdown')
            else:
                bot.send_message(uid, "❌ Data not found.")
        else:
            bot.send_message(uid, "❌ API Error.")
    except:
        bot.send_message(uid, "❌ Internal Error")

# ✅ Other buttons
@bot.message_handler(func=lambda m: m.text in ["🎫 Redeem", "💳 Balance", "👤 Contact Admin", "🚗 Vehicle Info", "🔗 Referral"])
def others(m):
    if m.text == "🎫 Redeem":
        ask_code(m)
    elif m.text == "💳 Balance":
        balance(m)
    elif m.text == "👤 Contact Admin":
        bot.send_message(m.chat.id, "👑 Admin: @HACKER722727\n💰 VIP Plans: ₹5000 Lifetime / ₹1200 Month")
    elif m.text == "🚗 Vehicle Info":
        bot.send_message(m.chat.id, "🚗 Feature coming soon!")
    elif m.text == "🔗 Referral":
        referral(m)

from flask import Flask, request
import logging

# ... (keep all existing code from line 2 to 251)

# ✅ Webhook setup
WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

app = Flask(__name__)

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))