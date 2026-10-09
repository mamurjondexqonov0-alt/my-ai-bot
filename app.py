import os
import json
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "7953931637:AAFI0y0dIrt-eXFv0lI-j4Hl_3s_3s"
WEBHOOK_URL = f"https://my-ai-bot-5x8z.onrender.com/{TOKEN}"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Server ishga tushishi bilan webhook'ni avtomatik ulaymiz
try:
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    print("Webhook muvaffaqiyatli o'rnatildi!")
except Exception as e:
    print(f"Webhook o'rnatishda xato: {e}")

def load_db():
    try:
        with open('database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_to_db(key, value):
    db = load_db()
    db[key.lower().strip()] = value.strip()
    with open('database.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

def main_menu_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🎬 Dublyaj loyihalari"),
        KeyboardButton("📝 Ssenariy / Matn tuzish"),
        KeyboardButton("📞 Aloqa / Buyurtma")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        f"Salom, {message.from_user.first_name}! 🎙 **Doktor Dubber** botiga xush kelibsiz!\n\n"
        f"Menga yangi tibbiy yoki boshqa ma'lumot o'rgatish uchun quyidagicha yozing:\n"
        f"👉 `O'rgan: mavzu - ma'lumot`",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_text_logic(message):
    text = message.text
    chat_id = message.chat.id
    low_text = text.lower()

    if text == "🎬 Dublyaj loyihalari":
        bot.send_message(chat_id, "📂 **Doktor Dubber Loyihalari:**\nBarcha anime va seriallar t.me/doktor_dubber kanalida yuklangan!", parse_mode="Markdown")
        return
    elif text == "📞 Aloqa / Buyurtma":
        bot.send_message(chat_id, "📝 Buyurtma va hamkorlik uchun: @doktor_dubber ga murojaat qiling.")
        return
    elif text == "📝 Ssenariy / Matn tuzish":
        bot.send_message(chat_id, "🎙 Ssenariy yoki matn mavzusini yozib yuboring. Birgalikda muhokama qilamiz!")
        return

    if low_text.startswith("o'rgan:") or low_text.startswith("oʻrgan:") or low_text.startswith("organ:"):
        try:
            content = text.split(":", 1)[1]
            if "-" in content:
                parts = content.split("-", 1)
                key = parts[0].strip()
                value = parts[1].strip()

                save_to_db(key, value)
                bot.send_message(
                    chat_id,
                    f"🧠 **Rahmat! Yangi bilim bazaga qo'shildi va yodlab qolindi:**\n\n📌 *Mavzu:* {key}\n📖 *Ma'lumot:* {value}",
                    parse_mode="Markdown"
                )
                return
        except Exception:
            bot.send_message(chat_id, "⚠️ Xatolik! O'rgatish formati noto'g'ri. Bunday yozing:\n`O'rgan: mavzu - ma'lumot`", parse_mode="Markdown")
            return

    db = load_db()
    found_answer = None

    for keyword, answer in db.items():
        if keyword in low_text:
            found_answer = answer
            break

    if found_answer:
        bot.send_message(chat_id, found_answer, parse_mode="Markdown")
    else:
        bot.send_message(
            chat_id,
            "🤖 Men bu haqida hali hech narsa bilmayman.\n\n"
            "Menga o'rgatish uchun quyidagicha yozing:\n"
            "`O'rgan: " + text + " - [bu yerga ma'lumotni yozing]`",
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
    return "Bot status: Active & Self-Learning Ready!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
