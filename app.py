import os
import json
import io
import random
import pypdf
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Bot tokeni va Render webhook manzili
TOKEN = "8961394155:AAEyso--Kr7_OiSomtz7FXDBTwdafx1miQo"
WEBHOOK_URL = f"https://my-ai-bot-5x8z.onrender.com/{TOKEN}"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Webhook sozlash
try:
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    print("Webhook muvaffaqiyatli o'rnatildi!")
except Exception as e:
    print(f"Webhook o'rnatishda xato: {e}")

# Ma'lumotlar bazasini o'qish
def load_db():
    try:
        with open('database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

# Bazaga saqlash
def save_to_db(key, value):
    db = load_db()
    db[key.lower().strip()] = value.strip()
    with open('database.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

# Bazadan o'chirish
def delete_from_db(key):
    db = load_db()
    key_low = key.lower().strip()
    if key_low in db:
        del db[key_low]
        with open('database.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
        return True
    return False

# Matndan ommaviy ma'lumot olish
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

# Asosiy menyu tugmalari
def main_menu_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📅 Dars jadvali"),
        KeyboardButton("📚 Tibbiy fanlar"),
        KeyboardButton("🧠 Bilimni sinash (Test)"),
        KeyboardButton("⚙️ Admin / Baza sozlamalari"),
        KeyboardButton("📞 Aloqa / Yordam")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        f"Salom, {message.from_user.first_name}! 🩺 **Davolash ishi (DI-2026-25) yordamchisi** botiga xush kelibsiz!\n\n"
        f"Baza noldan tozalanib, yangi tartibga keltirildi. Istalgan mavzuni o'rgating yoki savol yuboring!",
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
                    f"📂 **Fayldan ma'lumotlar o'qildi!**\n\n✅ Jami **{count} ta** mavzu bazaga yodlatildi.",
                    parse_mode="Markdown"
                )
            else:
                key = file_name.rsplit('.', 1)[0]
                save_to_db(key, extracted_text.strip())
                bot.send_message(chat_id, f"📂 **Fayl saqlandi!**\n\n📌 *Mavzu:* {key}", parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "⚠️ Fayl bo'sh.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Xatolik: {str(e)}")

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
    
    # Admin menyusi
    elif text == "⚙️ Admin / Baza sozlamalari":
        db = load_db()
        admin_text = (
            f"⚙️ **Baza boshqaruvi**\n\n"
            f"📊 Mavzular soni: **{len(db)} ta**\n\n"
            f"• Qo'shish: `O'rgan: Mavzu - Ma'lumot`\n"
            f"• O'chirish: `O'chir: Mavzu`\n"
            f"• Ro'yxat: `Ro'yxat`"
        )
        bot.send_message(chat_id, admin_text, parse_mode="Markdown")
        return

    elif low_text == "ro'yxat" or low_text == "royxat":
        db = load_db()
        if not db:
            bot.send_message(chat_id, "📭 Bazada ma'lumot yo'q.")
            return
        keys_str = ", ".join([k.capitalize() for k in db.keys()])
        bot.send_message(chat_id, f"📚 **Mavzular:**\n\n{keys_str}", parse_mode="Markdown")
        return

    if low_text.startswith("o'chir:") or low_text.startswith("oʻchir:") or low_text.startswith("ochir:"):
        try:
            key_to_del = text.split(":", 1)[1].strip()
            if delete_from_db(key_to_del):
                bot.send_message(chat_id, f"🗑 **{key_to_del.capitalize()}** o'chirildi!", parse_mode="Markdown")
            else:
                bot.send_message(chat_id, f"⚠️ Topilmadi.", parse_mode="Markdown")
        except Exception:
            bot.send_message(chat_id, "⚠️ Xato format! Masalan: `O'chir: Yurak`", parse_mode="Markdown")
        return

    elif text == "🧠 Bilimni sinash (Test)":
        db = load_db()
        if not db:
            bot.send_message(chat_id, "⚠️ Bazada ma'lumot yo'q. Avval o'rgating!")
            return
        random_key, random_val = random.choice(list(db.items()))
        bot.send_message(chat_id, f"🧠 **Test:**\n\n❓ *Mavzu:* {random_key.capitalize()}\n\n💡 *Javob:* {random_val}", parse_mode="Markdown")
        return

    if "o'rgan:" in low_text or "oʻrgan:" in low_text or "organ:" in low_text:
        count = parse_and_save_bulk(text)
        if count > 0:
            bot.send_message(chat_id, f"🧠 Ajoyib! Jami **{count} ta** mavzu yodlatildi.", parse_mode="Markdown")
            return

    # Qidirish mantiqi
    db = load_db()
    found_items = []
    for keyword, answer in db.items():
        if keyword in low_text:
            found_items.append(f"📌 **{keyword.capitalize()}**:\n{answer}")

    if found_items:
        response = "\n\n---\n\n".join(found_items)
        bot.send_message(chat_id, response, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "🤖 Bu haqida ma'lumot yo'q.\n\nO'rgatish uchun:\n`O'rgan: mavzu - ma'lumot`", parse_mode="Markdown", reply_markup=main_menu_keyboard())

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    return "Clean Bot status: Active!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
