import telebot
from groq import Groq
from flask import Flask, request
import base64
import os

BOT_TOKEN = "8853253021:AAFVteuxwkpTV0Phe6YThZW7hADg8x4d8yc"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
WEBHOOK_URL = "https://sadie-bot.onrender.com"

client = Groq(api_key=GROQ_API_KEY)
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

user_histories = {}

def get_history(user_id):
    if user_id not in user_histories:
        user_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return user_histories[user_id]

@bot.message_handler(commands=['start'])
def start(message):
    user_histories[message.from_user.id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    bot.reply_to(message, "Salom! Men Sadie 🌸 Nima haqida gaplashamiz? 💕")

@bot.message_handler(commands=['reset'])
def reset(message):
    user_histories[message.from_user.id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    bot.reply_to(message, "Suhbatni yangidan boshlaymiz 🌸")

@bot.message_handler(func=lambda m: True)
def handle(message):
    user_id = message.from_user.id
    history = get_history(user_id)
    history.append({"role": "user", "content": message.text})
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=history,
            max_tokens=1024
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        if len(history) > 22:
            user_histories[user_id] = [history[0]] + history[-20:]
        bot.reply_to(message, reply)
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
