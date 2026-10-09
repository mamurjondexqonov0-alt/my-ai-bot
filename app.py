import os
import json
import io
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
    """Matn ichidan bir nechta 'O'rgan: mavzu - ma'lumot' qismlarini topib, alohida-alohida saqlaydi"""
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
        KeyboardButton("📞 Aloqa / Yordam")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        f"Salom, {message.from_user.first_name}! 🩺 **Davolash ishi yordamchisi** botiga xush kelibsiz!\n\n"
        f"Men bir nechta ma'lumotni ketma-ket (har birini yangi qatordan `O'rgan: mavzu - ma'lumot` qilib) yuborsangiz, ularning **har birini alohida-alohida** ajratib bazaga yodlab olaman.\n\n"
        f"Shuningdek, `.txt` fayl yuborishingiz ham mumkin.",
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
            # Fayl ichidagi barcha O'rgan qismlarini alohida-alohida ajratib saqlaymiz
            count = parse_and_save_bulk(extracted_text)
            if count > 0:
                bot.send_message(
                    chat_id,
                    f"📂 **Fayldan ma'lumotlar muvaffaqiyatli ajratib olindi!**\n\n✅ Jami **{count} ta** mavzu alohida-alohida bazaga yodlatildi.",
                    parse_mode="Markdown"
                )
            else:
                # Agar faylda O'rgan formati bo'lmasa, fayl nomini kalit qilib butun matnni saqlaymiz
                key = file_name.rsplit('.', 1)[0]
                save_to_db(key, extracted_text.strip())
                bot.send_message(
                    chat_id,
                    f"📂 **Fayl butunicha saqlandi!**\n\n📌 *Mavzu:* {key}\n📖 *Hajmi:* {len(extracted_text)} ta belgi",
                    parse_mode="Markdown"
                )
        else:
            bot.send_message(chat_id, "⚠️ Fayl ichidan matn topilmadi yoki u bo'sh.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Faylni o'qishda xatolik yuz berdi: {str(e)}")

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

    # Agar xabarda bir nechta "O'rgan:" bo'lsa, hammasini bittalab ajratib olamiz
    if "o'rgan:" in low_text or "oʻrgan:" in low_text or "organ:" in low_text:
        count = parse_and_save_bulk(text)
        if count > 0:
            bot.send_message(
                chat_id,
                f"🧠 **Ajoyib! Jami {count} ta yangi mavzu alohida-alohida ajratilib, bazaga yodlatildi.**",
                parse_mode="Markdown"
            )
            return

    # Bazadan qidirish
    db = load_db()
    found_answer = None

    for keyword, answer in db.items():
        if keyword in low_text:
            found_answer = answer
            break

    if found_answer:
        if len(found_answer) > 3500:
            bot.send_message(chat_id, found_answer[:3500] + "\n\n...(davomi bor)...", parse_mode="Markdown")
        else:
            bot.send_message(chat_id, found_answer, parse_mode="Markdown")
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
