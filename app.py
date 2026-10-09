import os
import io
import json
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "7953931637:AAFI0y0dIrt-eXFv0lI-j4Hl_3s_3s"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Lokal database.json faylini o'qish funksiyasi
def load_db():
    try:
        with open('database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def main_menu_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🎬 Dublyaj loyihalari"),
        KeyboardButton("📝 Ssenariy / Matn tuzish"),
        KeyboardButton("📁 Fayl yaratish"),
        KeyboardButton("📞 Aloqa / Buyurtma")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        f"Salom, {message.from_user.first_name}! 🎙 **Doktor Dubber** botiga xush kelibsiz!\n\n"
        f"Serverga yuklangan bilimlar bazasi orqali sizga anatomiya, dublyaj, tarjima va boshqa mavzularda javob bera olaman. "
        f"Shuningdek, istalgan matningizni **fayl (TXT)** ko'rinishida yasab beraman!\n\n"
        f"Manga savol yozing yoki matn yuboring:",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_local_knowledge(message):
    text = message.text
    chat_id = message.chat.id
    low_text = text.lower()

    # 1. Menyu tugmalari
    if text == "🎬 Dublyaj loyihalari":
        bot.send_message(chat_id, "📂 **Doktor Dubber Loyihalari:**\nBarcha anime va seriallar t.me/doktor_dubber kanalida yuklangan!", parse_mode="Markdown")
        return
    elif text == "📞 Aloqa / Buyurtma":
        bot.send_message(chat_id, "📝 Buyurtma va hamkorlik uchun: @doktor_dubber ga murojaat qiling.")
        return
    elif text == "📝 Ssenariy / Matn tuzish":
        bot.send_message(chat_id, "🎙 Ssenariy yoki matn mavzusini yozib yuboring. Uni tartiblab, xohlasangiz fayl qilib beraman!")
        return
    elif text == "📁 Fayl yaratish":
        bot.send_message(chat_id, "💡 Matningizni yuboring va xabar oxiriga **'fayl qil'** deb yozing. Men uni darhol `.txt` hujjat qilib beraman!")
        return

    # 2. Fayl yaratish mantiqi
    if "fayl" in low_text or "txt" in low_text or "hujjat" in low_text:
        bot.send_message(chat_id, "⏳ Fayl shakllantirilmoqda...")
        clean_text = text.replace("fayl qil", "").replace("faylga aylantir", "").replace("fayl", "").strip()
        if not clean_text:
            clean_text = "Doktor Dubber loyihasi uchun tayyorlangan matn."

        file_data = io.BytesIO(clean_text.encode('utf-8'))
        file_data.name = "Doktor_Dubber_Hujjat.txt"
        
        bot.send_document(
            chat_id, 
            file_data, 
            caption="✅ **Siz so'ragan hujjat tayyorlandi!**",
            parse_mode="Markdown"
        )
        return

    # 3. Serverdagi database.json orqali aqlli qidirish va javob berish
    db = load_db()
    found_answer = None

    # Foydalanuvchi yozgan gap ichida database'dagi kalit so'zlar bor-yo'qligini tekshiramiz
    for keyword, answer in db.items():
        if keyword in low_text:
            found_answer = answer
            break

    if found_answer:
        bot.send_message(chat_id, found_answer, parse_mode="Markdown")
    else:
        # Agar baza topolmasa, umumiy tahlil va fayl qilish taklifi
        bot.send_message(
            chat_id,
            f"📥 **Xabaringiz qabul qilindi:**\n\n_{text}_\n\n"
            f"💡 *Bu matndan hujjat yaratish uchun xabaringiz oxiriga 'fayl qil' deb yozing!*",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://my-ai-bot-5x8z.onrender.com/' + TOKEN)
    return "Bot status: Active & Local Database Loaded!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
