# flask_app.py

from flask import Flask, request
import os  # Importăm 'os' pentru a putea citi variabilele de mediu
import logging
import telebot
from telebot import types

# --- CONFIGURARE SECURIZATĂ ---
# Codul citește token-urile din "mediul" platformei de hosting (Render).
# Acestea NU sunt vizibile în codul de pe GitHub.
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

# Inițiem aplicația Flask
app = Flask(__name__)

# Verificăm dacă token-ul a fost încărcat și inițiem bot-ul
if BOT_TOKEN:
    bot = telebot.TeleBot(BOT_TOKEN)
else:
    # Dacă token-ul lipsește, bot-ul nu va funcționa
    bot = None
    print("AVERTISMENT: Variabila de mediu BOT_TOKEN nu este setată. Bot-ul este inactiv.")

# === TELEGRAM BOT HANDLERS ===
# Acest cod va rula doar dacă bot-ul a fost inițiat cu succes
if bot:
    @bot.message_handler(commands=['start'])
    def start_command(message):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("🇷🇴 Română", callback_data="lang_ro"),
            types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        )
        welcome_text = (
            "🚀 Bun venit la MarioCoinAMG!\n"
            "🌱 Construiește-ți viitorul verde!\n\n"
            "Alege limba preferată:"
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard)

    @bot.message_handler(commands=['broscute'])
    def broscute_command(message):
        response = (
            "🐸 *Broșcuțe MarioCoinAMG*\n\n"
            "💰 Balanța ta: **350 broșcuțe**\n"
            "🪙 Rate conversie: **10000 broșcuțe = 100 MARIO**\n\n"
            "🎯 Bot funcționează 24/7 pe Render!"
        )
        bot.send_message(message.chat.id, response, parse_mode='Markdown')

    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        if call.data == "lang_ro":
            response = (
                "🚀 *MarioCoinAMG - Ecosistem Verde*\n\n"
                "🌱 Bot funcționează 24/7!\n"
                "💰 Broșcuțe → MARIO tokens\n"
                "☁️ Hosting pe Render"
            )
            bot.edit_message_text(
                response,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )

# === FLASK ROUTES ===

# Aceasta este ruta secretă pe care Telegram o va apela
# Este esențial ca WEBHOOK_SECRET să fie setat în variabilele de mediu
@app.route(f'/{WEBHOOK_SECRET}', methods=['POST'])
def telegram_webhook():
    if bot:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    else:
        return "Bot-ul nu este configurat.", 500

# Aceasta este ruta pe care o vizitezi tu pentru a activa bot-ul
@app.route('/set_webhook')
def set_webhook_route():
    if not bot:
        return "❌ Bot-ul nu poate fi setat deoarece BOT_TOKEN lipsește."

    # Render oferă automat URL-ul public în variabila de mediu 'RENDER_EXTERNAL_URL'
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    
    if not render_url:
        return "❌ Eroare: Nu s-a putut detecta URL-ul public al aplicației (rulezi local?)."
    
    webhook_url = f"{render_url}/{WEBHOOK_SECRET}"
    
    try:
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        return f"✅ Webhook setat cu succes la: {webhook_url}"
    except Exception as e:
        return f"❌ Eroare la setarea webhook-ului: {e}"

# Pagina principală a aplicației web
@app.route('/')
def index():
    status_text = "✅ Bot-ul este gata de activare." if bot else "⚠️ BOT_TOKEN nu este setat în Environment."
    return f"<h1>🚀 MarioCoinAMG Bot rulează pe Render</h1><p>{status_text}</p><p>După deploy, vizitează /set_webhook pentru a activa bot-ul.</p>"
# === PORNIREA SERVERULUI FLASK CORESPUNZĂTOARE PENTRU RENDER ===
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

