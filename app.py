import os
import re
import random
import threading
import telebot
from flask import Flask

# 1. Telegram Bot Token
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8961394155:AAEFVyA_FVgbWyobOvuYhhEhHO6SoZLY0Cg")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 2. O'zimizning Mustaqil AI Dvigatelimiz
class CustomAI:
    def __init__(self):
        self.knowledge = {
            "salom": ["Salom! Sizga qanday yordam bera olaman?", "Assalomu alaykum! Savolingizni bering."],
            "ism": ["Men Termux'da yaratilgan va 24/7 serverda ishlaydigan mustaqil AI yordamchiman."],
            "yordam": ["Menga istalgan matnli savol yoki matematik amallarni bering!"],
            "qandaysan": ["Yaxshi, raxmat! 24/7 rejimda xizmatingizdamayman."]
        }

    def generate_response(self, text):
        clean_text = text.lower().strip()
        
        # Matematik misollarni hisoblash
        if re.match(r'^[0-9\+\-\*\/\(\)\s]+$', clean_text) and any(char.isdigit() for char in clean_text):
            try:
                result = eval(clean_text)
                return f"🧮 Hisoblash natijasi: {clean_text} = {result}"
            except Exception:
                pass

        # Kalit so'zlar bo'yicha tahlil
        for key in self.knowledge:
            if key in clean_text:
                return random.choice(self.knowledge[key])

        # Aks holda umumiy AI javob matni
        words_count = len(text.split())
        return f"🤖 AI Tahlili: Sizning xabaringiz ({words_count} ta so'z) tahlil qilindi. Men o'z bilimlar bazamni doimiy kengaytirib bormoqdaman!"

ai_brain = CustomAI()

# 3. Web Server (Render 24/7 uqlab qolmasligi uchun)
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ O'zimizning AI Serverimiz 24/7 rejimida ishlamoqda!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 4. Telegram Bot Buyruqlari
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(
        message.chat.id,
        "🤖 **Salom! Men Termux orqali yaratilgan va 24/7 ishlaydigan AI botman.**\n\nSavolingizni berishingiz mumkin!",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    response_text = ai_brain.generate_response(message.text)
    bot.reply_to(message, response_text)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("🤖 Mustaqil AI Bot Termux'da ishga tushdi...")
    bot.infinity_polling()
