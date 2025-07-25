import os
from flask import Flask, request, jsonify
import logging
from datetime import datetime

# Configurare logging pentru a vedea erori în log-urile Render
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# --- Configurare Bot ---
# Codul citește token-urile din "mediul" platformei de hosting (Render).
# Acestea NU sunt vizibile în codul de pe GitHub.
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

# Verificăm dacă token-ul și secretul sunt setate
if not BOT_TOKEN:
    logging.error("Variabila de mediu BOT_TOKEN nu este setată! Bot-ul este inactiv.")
if not WEBHOOK_SECRET:
    logging.error("Variabila de mediu WEBHOOK_SECRET nu este setată! Webhook-ul nu va funcționa securizat.")

# Încercăm să importăm telebot și să inițializăm bot-ul
try:
    import telebot
    from telebot import types
    
    if BOT_TOKEN:
        bot = telebot.TeleBot(BOT_TOKEN)
        BOT_AVAILABLE = True
        logging.info("Telebot inițializat cu succes.")
    else:
        bot = None
        BOT_AVAILABLE = False
        logging.warning("Telebot nu a putut fi inițializat din cauza lipsei BOT_TOKEN.")
    
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
            elif call.data == "lang_en": # Adăugat și text în engleză pentru consistență
                response = (
                    "🚀 *MarioCoinAMG - Green Ecosystem*\n\n"
                    "🌱 Bot works 24/7!\n"
                    "💰 Froggies → MARIO tokens\n"
                    "☁️ Hosting on Render"
                )
                bot.edit_message_text(
                    response,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown'
                )

except ImportError:
    BOT_AVAILABLE = False
    bot = None
    logging.error("Eroare: Biblioteca 'pyTelegramBotAPI' nu a putut fi importată. Asigură-te că este în requirements.txt.")

# === Rute Flask ===

# Aceasta este ruta secretă pe care Telegram o va apela
# Este esențial ca WEBHOOK_SECRET să fie setat în variabilele de mediu
@app.route(f'/{WEBHOOK_SECRET}', methods=['POST'])
def telegram_webhook():
    if not BOT_AVAILABLE:
        logging.warning("Webhook primit, dar bot-ul nu este disponibil.")
        return "Bot-ul nu este configurat.", 500
    
    # Verificare secret token pentru securitate
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != WEBHOOK_SECRET:
        logging.warning("X-Telegram-Bot-Api-Secret-Token invalid primit.")
        return "Neautorizat", 403

    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        logging.error(f"Eroare la procesarea actualizării webhook-ului: {e}")
        return f"Eroare: {e}", 500

# Aceasta este ruta pe care o vizitezi tu pentru a activa bot-ul
@app.route('/set_webhook')
def set_webhook_route():
    if not BOT_AVAILABLE:
        return "❌ Bot-ul nu poate fi setat deoarece BOT_TOKEN lipsește."

    # Render oferă automat URL-ul public în variabila de mediu 'RENDER_EXTERNAL_URL'
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    
    if not render_url:
        logging.error("Nu s-a putut detecta URL-ul public al aplicației (rulezi local?).")
        return "❌ Eroare: Nu s-a putut detecta URL-ul public al aplicației (rulezi local?)."
    
    webhook_url = f"{render_url}/{WEBHOOK_SECRET}"
    
    try:
        logging.info(f"Încerc să elimin webhook-ul existent...")
        bot.remove_webhook() # Întotdeauna bine să elimini vechiul webhook
        logging.info(f"Setez noul webhook la: {webhook_url}")
        # Setăm webhook-ul, incluzând secret_token pentru securitate
        result = bot.set_webhook(url=webhook_url, secret_token=WEBHOOK_SECRET)
        
        if result:
            logging.info("Webhook setat cu succes.")
            return f"✅ Webhook setat cu succes la: {webhook_url}"
        else:
            logging.error("Eroare la setarea webhook-ului.")
            return "❌ Eroare la setarea webhook-ului"
    except Exception as e:
        logging.error(f"Eroare la setarea webhook-ului: {e}")
        return f"❌ Eroare: {e}"

# Pagina principală a aplicației web
@app.route('/')
def index():
    status_text = "✅ Bot-ul este gata de activare." if BOT_AVAILABLE else "⚠️ BOT_TOKEN nu este setat în Environment."
    return f"""
    <h1>🚀 MarioCoinAMG Bot rulează pe Render</h1>
    <p>Status: {status_text}</p>
    <p>După deploy, vizitează <a href="/set_webhook">/set_webhook</a> pentru a activa bot-ul.</p>
    """

# === PORNIREA SERVERULUI FLASK CORESPUNZĂTOARE PENTRU RENDER ===
if __name__ == '__main__':
    logging.info("Rulez aplicația Flask local.")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
