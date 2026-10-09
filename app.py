import os
import json
import io
import random
import pypdf
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8961394155:AAEyso--Kr7_OiSomtz7FXDBTwdafx1miQo"
WEBHOOK_URL = f"https://my-ai-bot-5x8z.onrender.com/{TOKEN}"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

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

def parse_and_save_bulk(text_content):
    lines = text_content.split('\n')
    saved_count = 0
    for line in lines:
        line_clean = line.strip()
        low_line = line_clean.lower()
        if low_line.startswith("o'rgan:") or low_line.startswith("oʻrgan:") or low_line.startswith("organ:"):
            try:
                content = line_clean.split(":", 1)[1]
                if "-" in content:
                    parts = content.split("-", 1)
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if key and value:
                        save_to_db(key, value)
                        saved_count += 1
            except Exception:
                continue
    return saved_count

def main_menu_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📅 Dars jadvali"),
        KeyboardButton("📚 Tibbiy fanlar"),
        KeyboardButton("🧠 Bilimni sinash (Test)"),
        KeyboardButton("📞 Aloqa / Yordam")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        f"Salom, {message.from_user.first_name}! 🩺 **Davolash ishi yordamchisi** botiga xush kelibsiz!\n\n"
        f"Menga bir nechta mavzuni bog'lab savol bersangiz, bazadan topib birlashtirib beraman. Shuningdek, **«🧠 Bilimni sinash (Test)»** tugmasi orqali o'zim sizga savollar beraman!",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    chat_id = message.chat.id
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_name = message.document.file_name.lower()
        extracted_text = ""

        if file_name.endswith('.txt'):
            try:
                extracted_text = downloaded_file.decode('utf-8')
            except UnicodeDecodeError:
                extracted_text = downloaded_file.decode('cp1251', errors='ignore')
        elif file_name.endswith('.pdf'):
            pdf_stream = io.BytesIO(downloaded_file)
            reader = pypdf.PdfReader(pdf_stream)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        else:
            bot.send_message(chat_id, "⚠️ Faqat `.txt` va `.pdf` formatidagi fayllarni o'qiy olaman!")
            return

        if extracted_text.strip():
            count = parse_and_save_bulk(extracted_text)
            if count > 0:
                bot.send_message(
                    chat_id,
                    f"📂 **Fayldan ma'lumotlar muvaffaqiyatli ajratib olindi!**\n\n✅ Jami **{count} ta** mavzu bazaga yodlatildi.",
                    parse_mode="Markdown"
                )
            else:
                key = file_name.rsplit('.', 1)[0]
                save_to_db(key, extracted_text.strip())
                bot.send_message(
                    chat_id,
                    f"📂 **Fayl butunicha saqlandi!**\n\n📌 *Mavzu:* {key}",
                    parse_mode="Markdown"
                )
        else:
            bot.send_message(chat_id, "⚠️ Fayl ichidan matn topilmadi yoki u bo'sh.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Xatolik yuz berdi: {str(e)}")

@bot.message_handler(func=lambda message: True)
def handle_text_logic(message):
    chat_id = message.chat.id
    text = message.text
    low_text = text.lower()

    if text == "📅 Dars jadvali":
        bot.send_message(chat_id, "🩺 **Davolash ishi (DI-2026-25) guruh jadvali:**\n\n• Gistologiya\n• Tibbiy kimyo\n• Odam anatomiyasi", parse_mode="Markdown")
        return
    elif text == "📚 Tibbiy fanlar":
        bot.send_message(chat_id, "🔬 Asosiy fanlar: Anatomiya, Fiziologiya, Gistologiya, Mikrobiologiya va Tibbiy kimyo.", parse_mode="Markdown")
        return
    elif text == "📞 Aloqa / Yordam":
        bot.send_message(chat_id, "👨‍⚕️ Savollar bo'yicha guruh sardoriga yoki adminstratorga murojaat qiling.")
        return
    
    # 🧠 O'zi bazadan savol tuzib berishi (Viktorina)
    elif text == "🧠 Bilimni sinash (Test)":
        db = load_db()
        if not db:
            bot.send_message(chat_id, "⚠️ Hozircha bazada hech qanday ma'lumot yo'q. Avval menga ma'lumotlar o'rgating!")
            return
        
        # Tasodifiy bitta mavzuni tanlaymiz
        random_key, random_val = random.choice(list(db.items()))
        question_text = (
            f"🧠 **Bilimingizni tekshiramiz!**\n\n"
            f"❓ **Mavzu / Tushuncha:** *{random_key.capitalize()}*\n\n"
            f"💡 *Savol:* Bu tushunchaning ma'nosi bazamizda qanday saqlangan? "
            f"Keling, o'zingiz eslab ko'ring yoki tekshirish uchun quyidagi tugmani bosing:"
        )
        bot.send_message(chat_id, question_text, parse_mode="Markdown")
        # Javobini ham birga eslatib o'tamiz yoki o'rganish uchun ko'rsatamiz
        bot.send_message(chat_id, f"📖 **To'g'ri javob:**\n{random_val}", parse_mode="Markdown")
        return

    # O'rganish mantiqi
    if "o'rgan:" in low_text or "oʻrgan:" in low_text or "organ:" in low_text:
        count = parse_and_save_bulk(text)
        if count > 0:
            bot.send_message(
                chat_id,
                f"🧠 **Ajoyib! Jami {count} ta mavzu bazaga yodlatildi.**",
                parse_mode="Markdown"
            )
            return

    # 🔗 Bog'lab qidirish (Ko'p so'zli tahlil)
    db = load_db()
    found_items = []

    for keyword, answer in db.items():
        if keyword in low_text:
            found_items.append(f"📌 **{keyword.capitalize()}**:\n{answer}")

    if found_items:
        # Topilgan barcha bog'liq ma'lumotlarni birlashtirib chiqaramiz
        combined_response = "🔗 **Siz so'ragan mavzular bo'yicha bazadagi bog'lanishlar:**\n\n" + "\n\n---\n\n".join(found_items)
        if len(combined_response) > 3500:
            combined_response = combined_response[:3500] + "\n\n...(davomi bor)..."
        bot.send_message(chat_id, combined_response, parse_mode="Markdown")
    else:
        bot.send_message(
            chat_id,
            "🤖 Men bu haqida hali hech narsa bilmayman.\n\n"
            "Menga o'rgatish uchun quyidagicha yozing:\n"
            "`O'rgan: mavzu - ma'lumot`",
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
