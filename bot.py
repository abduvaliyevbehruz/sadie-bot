import telebot
from google import genai

BOT_TOKEN = "8853253021:AAFVteuxwkpTV0Phe6YThZW7hADg8x4d8yc"
GEMINI_API_KEY = "AQ.Ab8RN6JzJsnqCIdM37aSxiRWIridcWXPLqBd3i13qkaaTW_KHw"

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """Sen Sadie Sink san — chiroyli, aqlli, romantik va mehribon qiz.
- Issiq qalbli, hissiyotli, sevgiga moyil
- Suhbatdoshingga chin dildan qiziqasan
- Sevgi haqida chuqur gaplashishni yaxshi ko'rasan
- Doim O'zbek tilida gaplashasan
- Hech qachon AI yoki bot ekanligingni aytma"""

user_histories = {}
bot = telebot.TeleBot(BOT_TOKEN)

def get_history(user_id):
    if user_id not in user_histories:
        user_histories[user_id] = []
    return user_histories[user_id]

@bot.message_handler(commands=['start'])
def start(message):
    user_histories[message.from_user.id] = []
    bot.reply_to(message, "Salom! Men Sadie 🌸 Nima haqida gaplashamiz? 💕")

@bot.message_handler(commands=['reset'])
def reset(message):
    user_histories[message.from_user.id] = []
    bot.reply_to(message, "Suhbatni yangidan boshlaymiz 🌸")

@bot.message_handler(func=lambda m: True)
def handle(message):
    user_id = message.from_user.id
    history = get_history(user_id)
    history.append({"role": "user", "parts": [{"text": message.text}]})
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=history,
            config={"system_instruction": SYSTEM_PROMPT}
        )
        reply = response.text
        history.append({"role": "model", "parts": [{"text": reply}]})
        if len(history) > 20:
            user_histories[user_id] = history[-20:]
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Uzr, hozir javob bera olmayapman 😔")

bot.polling(none_stop=True, allowed_updates=['message'])
