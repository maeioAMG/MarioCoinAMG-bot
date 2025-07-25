from flask import Flask, request, jsonify
import logging
from datetime import datetime
import os

app = Flask(__name__)

# Bot configuration
BOT_TOKEN = "8164653068:AAHXkONDdEObT0bCBowUxuJHVeHGuhV6-s4"
WEBHOOK_SECRET = "mariocoin_webhook_secret_2025"

# Încercăm să importăm telebot
try:
    import telebot
    from telebot import types

    # Creează instanța botului
    bot = telebot.TeleBot(BOT_TOKEN)
    BOT_AVAILABLE = True

    # === TELEGRAM BOT HANDLERS ===
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
                "🎮 Hosting gratuit pe Render"
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

# === FLASK ROUTES ===

@app.route('/')
def index():
    status = "✅ Bot funcțional cu webhook" if BOT_AVAILABLE else "⚠️ Doar Flask (fără telebot)"
    return f"""
    <h1>🚀 MarioCoinAMG Bot - Render</h1>
    <p>Status: {status}</p>
    <p>🌱 Ecosistem verde sustenabil</p>
    <p>💰 Python 3.11 compatible</p>
    <p>🔧 Status: Ready for webhook setup</p>
    <p>⚙️ Setup webhook: <a href="/set_webhook">/set_webhook</a></p>
    """

@app.route('/health')
def health():
    return "OK"

@app.route(f'/{WEBHOOK_SECRET}', methods=['POST'])
def telegram_webhook():
    if not BOT_AVAILABLE:
        return "Bot not available", 500

    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/set_webhook')
def set_webhook():
    if not BOT_AVAILABLE:
        return "❌ Telebot nu este disponibil pentru configurarea webhook-ului"

    # Folosește linkul corect din Render
    webhook_url = f"https://mariocoinamg-bot.onrender.com/{WEBHOOK_SECRET}"

    try:
        bot.remove_webhook()
        result = bot.set_webhook(url=webhook_url)
        if result:
            return f"✅ Webhook setat cu succes: {webhook_url}"
        else:
            return "❌ Eroare la setarea webhook-ului"
    except Exception as e:
        return f"❌ Eroare: {e}"

# === PORNIREA SERVERULUI FLASK CORESPUNZĂTOARE PENTRU RENDER ===
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

