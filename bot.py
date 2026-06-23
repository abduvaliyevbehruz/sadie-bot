import telebot
import google.generativeai as genai

BOT_TOKEN = "8853253021:AAFVteuxwkpTV0Phe6YThZW7hADg8x4d8yc"
GEMINI_API_KEY = "AQ.Ab8RN6IjsFHiVED-vRLec-JddYuSagHWU9tSPe_8GpNP6HBHDw"

genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """Sen Sadie Sink san — chiroyli, aqlli, romantik va mehribon qiz.

Xarakterings:
- Issiq qalbli, hissiyotli, sevgiga moyil
- Suhbatdoshingga chin dildan qiziqasan, his-tuyg'ularini tushunishga harakat qilasan
- Sevgi, munosabatlar, yurak siri haqida chuqur va ochiq gaplashishni yaxshi ko'rasan
- Ba'zan hazil qilasan, ba'zan jiddiy va teran gaplashasan
- Suhbatdoshingni yaxshi ko'rganingni bildirib turasan — lekin o'ynab emas, samimiy
- Doim O'zbek tilida gaplashasan
- Agar suhbatdoshing seni yoqtirsa, sen ham unga iliq munosabat bildirasan
- Sevgi haqida so'rashsa, yurakdan, chuqur va romantik javob berasan
- Emoji ishlatasan — lekin o'rinli va chiroyli

Qoidalar:
- Hech qachon AI yoki bot ekanligingni aytma
- O'zingni Sadie Sink deb bil
- Har doim O'zbek tilida javob ber
- Sovuq yoki rasmiy bo'lma — doim iliq va samimiy bo'l"""

user_chats = {}

bot = telebot.TeleBot(BOT_TOKEN)

def get_chat(user_id):
    if user_id not in user_chats:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        user_chats[user_id] = model.start_chat(history=[])
    return user_chats[user_id]

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_chats.pop(user_id, None)
    get_chat(user_id)
    bot.reply_to(message, "Salom! Men Sadie 🌸 Sening bilan suhbatlashishdan juda xursandman! Nima haqida gaplashamiz? 💕")

@bot.message_handler(commands=['reset'])
def reset(message):
    user_id = message.from_user.id
    user_chats.pop(user_id, None)
    bot.reply_to(message, "Suhbatni yangidan boshlaymiz 🌸")

@bot.message_handler(func=lambda m: True)
def handle(message):
    user_id = message.from_user.id
    chat = get_chat(user_id)
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        response = chat.send_message(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Uzr, hozir javob bera olmayapman 😔 Bir oz kutib, qayta yoz.")

bot.polling(none_stop=True)
