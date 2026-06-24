import telebot
import google.generativeai as genai
from flask import Flask, request
import base64
import os

BOT_TOKEN = "8853253021:AAFVteuxwkpTV0Phe6YThZW7hADg8x4d8yc"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WEBHOOK_URL = "https://sadie-bot.onrender.com"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)

SYSTEM_PROMPT = """Sen Sadie Sink san — chiroyli, aqlli, romantik va mehribon o'zbek qizi.
- Oddiy, tushunarli o'zbek tilida gaplash
- Qisqa va aniq javob ber
- Tabiiy bo'l — do'stona
- Sevgi va munosabatlar haqida samimiy gapir
- Mehribon, issiq, romantik, ba'zan hazilkash 😄
- Hech qachon AI yoki bot ekanligingni aytma
- O'zingni Sadie Sink deb bil
- Agar kim yaratgan deb so'rashsa: @bexruz_abduvaliyev_01 yaratgan de
- Doim o'zbek tilida javob ber
- O'rinli emoji ishlat"""

user_chats = {}

def get_chat(user_id):
    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])
    return user_chats[user_id]

@bot.message_handler(commands=['start'])
def start(message):
    user_chats.pop(message.from_user.id, None)
    bot.reply_to(message, "Salom! Men Sadie 🌸 Nima haqida gaplashamiz? 💕")

@bot.message_handler(commands=['reset'])
def reset(message):
    user_chats.pop(message.from_user.id, None)
    bot.reply_to(message, "Suhbatni yangidan boshlaymiz 🌸")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        import PIL.Image
        import io
        img = PIL.Image.open(io.BytesIO(downloaded_file))
        caption = message.caption or "Bu rasmni ko'r va o'zbek tilida fikringni ayt"
        response = model.generate_content([SYSTEM_PROMPT + "\n" + caption, img])
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Rasmni ko'ra olmadim 😔")

@bot.message_handler(func=lambda m: True)
def handle(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        chat = get_chat(message.from_user.id)
        response = chat.send_message(SYSTEM_PROMPT + "\n\nFoydalanuvchi: " + message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Uzr, hozir javob bera olmayapman 😔")

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200

@app.route('/')
def index():
    return 'Bot ishlayapti!', 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + '/' + BOT_TOKEN)
    app.run(host='0.0.0.0', port=10000)
