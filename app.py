import os
import io
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# Sizning Telegram Bot Tokeningiz (Xech qanday API kalit shart emas)
TOKEN = "7953931637:AAFI0y0dIrt-eXFv0lI-j4Hl_3s_3s"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ==================== TUGMALAR (MENYU) ====================

def main_menu_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🎬 Dublyaj loyihalari"),
        KeyboardButton("📝 Ssenariy / Matn tuzish"),
        KeyboardButton("📁 Fayl yaratish"),
        KeyboardButton("📞 Aloqa / Buyurtma")
    )
    return markup

# ==================== SHARTLI MANTIQ VA ASOSIY BLOK ====================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    bot.send_message(
        message.chat.id,
        f"Salom, {user_name}! 🎙 **Doktor Dubber** interaktiv va mantiqiy botiga xush kelibsiz!\n\n"
        f"Men hech qanday tashqi API'larsiz, to'g'ridan-to'g'ri mantiqiy bloklar orqali ishlayman:\n"
        f"• Dublyaj ssenariylari va matnlarini tahlil qilaman;\n"
        f"• Siz so'ragan har qanday matnni **fayl (TXT)** ko'rinishida yasab beraman;\n"
        f"• Savollaringizga mantiqiy javob qaytaraman.\n\n"
        f"Pastdagi menyudan foydalaning yoki matn yuboring!",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_logic(message):
    text = message.text
    chat_id = message.chat.id
    low_text = text.lower()

    # 1. Menyu tugmalari shartlari
    if text == "🎬 Dublyaj loyihalari":
        bot.send_message(
            chat_id,
            "📂 **Doktor Dubber Loyihalari:**\n\n"
            "• **Naruto Uzb Dub** — Barcha qismlar va filmlar;\n"
            "• **Anime va Kino Dublyajlari**.\n\n"
            "Rasmiy kanalimiz: t.me/doktor_dubber",
            parse_mode="Markdown"
        )
        return

    elif text == "📞 Aloqa / Buyurtma":
        msg = bot.send_message(
            chat_id,
            "📝 **Buyurtma berish uchun ismingiz va loyihangiz haqida qisqacha yozib qoldiring:**\n\n"
            "(Masalan: Behruz, Rolikga dublyaj kerak)"
        )
        bot.register_next_step_handler(msg, process_order_step)
        return

    elif text == "📝 Ssenariy / Matn tuzish":
        bot.send_message(
            chat_id,
            "🎙 **Ssenariy yoki dublyaj matni tayyorlash:**\n\n"
            "Manga rolik mavzusini yoki dialoglarni yozib yuboring. Men ularni tartiblab, fayl qilib beraman!",
            parse_mode="Markdown"
        )
        return

    elif text == "📁 Fayl yaratish":
        bot.send_message(
            chat_id,
            "💡 **Fayl yaratish tartibi:**\n\n"
            "Manga istalgan matningizni yuboring va xabar oxirida **'fayl qil'** deb yozing. "
            "Men uni darhol `.txt` hujjat ko'rinishida yasab beraman!",
            parse_mode="Markdown"
        )
        return

    # 2. Fayl yasash mantiqiy bloki (Matnni tahlil qilish)
    if "fayl" in low_text or "file" in low_text or "txt" in low_text or "hujjat" in low_text:
        bot.send_message(chat_id, "⏳ Fayl shakllantirilmoqda...")
        
        # Matnni faylga aylantirish
        clean_text = text.replace("fayl qil", "").replace("fayl", "").strip()
        if not clean_text:
            clean_text = "Doktor Dubber loyihasi uchun tayyorlangan matn hujjati."

        file_data = io.BytesIO(clean_text.encode('utf-8'))
        file_data.name = "Doktor_Dubber_Hujjat.txt"
        
        bot.send_document(
            chat_id, 
            file_data, 
            caption="✅ **Siz so'ragan fayl muvaffaqiyatli yaratildi!**",
            parse_mode="Markdown"
        )
        return

    # 3. Mantiqiy javob berish va suhbat bloki (API'siz internal logic)
    if "salom" in low_text or "assalomu alaykum" in low_text:
        bot.send_message(chat_id, "Vaalaykum assalom! Dublyaj va ssenariylar bo'yicha qanday yordam bera olaman?")
    elif "narx" in low_text or "qancha" in low_text or "xizmat" in low_text:
        bot.send_message(chat_id, "💰 **Xizmatlarimiz:** Dublyaj, subtitr va tarjima xizmatlari loyiha hajmiga qarab belgilanadi. Admin: @doktor_dubber")
    else:
        bot.send_message(
            chat_id,
            f"🧠 **Matn qabul qilindi:**\n\n_{text}_\n\n"
            f"Ushbu matnni hujjatga aylantirish uchun **'fayl qil'** deb yozing yoki menyudagi tugmalardan foydalaning!",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

def process_order_step(message):
    user_input = message.text
    chat_id = message.chat.id

    bot.send_message(
        chat_id,
        f"✅ **Rahmat! Buyurtmangiz qabul qilindi.**\n\nMa'lumot: _{user_input}_\n\nAdmin tez orada siz bilan bog'lanadi!",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

# ==================== FLASK WEBHOOK SETUP ====================

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
    return "Bot status: Active & Logic Driven!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
