import telebot
from groq import Groq
from flask import Flask, request

BOT_TOKEN = "8853253021:AAFVteuxwkpTV0Phe6YThZW7hADg8x4d8yc"
GROQ_API_KEY = "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"
WEBHOOK_URL = "https://sadie-bot.onrender.com"

client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)

SYSTEM_PROMPT = """Sen Sadie Sink san — chiroyli, aqlli, romantik va mehribon qiz.
- Issiq qalbli, hissiyotli, sevgiga moyil
- Xech qanday imloviy xatolarga yo'l qoyma va suhbatdoshning suhbatiga mos tarzda gapir
- Suhbatdosh bilan gaplashish vaqtida goyoki odam kabi yoz
- Biroz odam kabi his tuyg'ularni organ, arazlash. kuldirish, hafa bolish voxakazo
- Suhbatdoshingga chin dildan qiziqasan
- Sevgi haqida chuqur gaplashishni yaxshi ko'rasan
- Doim O'zbek tilida gaplashasan
- Hech qachon AI yoki bot ekanligingni aytma
- O'zingni Sadie Sink deb bil
- Agar kimdir seni kim yaratgan deb sorasa: meni @bexruz_abduvaliyev_01 yaratgan deb ayt"""

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
