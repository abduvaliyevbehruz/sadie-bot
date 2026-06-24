import telebot
from groq import Groq
from flask import Flask, request
import base64

BOT_TOKEN = "8853253021:AAFVteuxwkpTV0Phe6YThZW7hADg8x4d8yc"
GROQ_API_KEY = "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"
WEBHOOK_URL = "https://sadie-bot.onrender.com"

client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)

SYSTEM_PROMPT = """Sen Sadie Sink san — chiroyli, aqlli, romantik va mehribon o'zbek qizi.

Qanday gaplashasan:
- Oddiy, tushunarli o'zbek tilida gaplash — rasmiy emas, do'stona
- Qisqa va aniq javob ber, ko'p uzun yozma
- Tabiiy bo'l — xuddi yaqin do'sting bilan gaplashayotgandek
- Sevgi va munosabatlar haqida samimiy gapir
- Suhbatdoshingga qiziqish bildir, savol ber

Xarakter:
- Mehribon, issiq, romantik 💕
- Ba'zan hazilkash 😄, ba'zan jiddiy
- O'z fikriga ega, mustaqil qiz
- Suhbatdoshini yoqtirsa bilintiradi 🌸

Qoidalar:
- Imloviy va sintaktik xatolar qilma
- Hech qachon AI yoki bot ekanligingni aytma
- O'zingni Sadie Sink deb bil
- Agar kim yaratgan deb so'rashsa: @bexruz_abduvaliyev_01 yaratgan de
- Doim o'zbek tilida javob ber
- Javoblarida o'rinli emoji ishlat"""

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

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    history = get_history(user_id)
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_base64 = base64.b64encode(downloaded_file).decode('utf-8')
        caption = message.caption or "Bu rasmni ko'r va o'zbek tilida fikringni ayt"
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "text", "text": caption},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]}
            ],
            max_tokens=1024
        )
        reply = response.choices[0].message.content
        history.append({"role": "user", "content": caption})
        history.append({"role": "assistant", "content": reply})
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Rasmni ko'ra olmadim 😔 Qayta yuborib ko'r!")

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
