import os
from io import BytesIO
from queue import Queue
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Dispatcher
from movies_scraper import search_movies, get_movie


TOKEN = os.getenv("TOKEN")
URL = "https://moviebot-psi.vercel.app"
bot = Bot(TOKEN)


def welcome(update, context) -> None:
    update.message.reply_text(f"𝗛𝗘𝗟𝗟𝗢 {update.message.from_user.first_name}, 𝚆𝙴𝙻𝙲𝙾𝙼𝙴 𝚃𝙾 𝙳𝙰𝚇𝚇 𝙼𝚄𝚂𝙸𝙲 𝙱𝙾𝚃.\n"
                              f"🔥🔥 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝗬𝗼𝘂𝗿 𝗙𝗮𝘃𝗼𝘂𝗿𝗶𝘁𝗲 𝗠𝗼𝘃𝗶𝗲𝘀 𝗙𝗼𝗿 💯 𝗙𝗿𝗲𝗲 𝗔𝗻𝗱 🍿 𝗘𝗻𝗷𝗼𝘆 𝗶𝘁. 𓆠")
    update.message.reply_text("𝐄𝐍𝐓𝐄𝐑 𝐘𝐎𝐔𝐑 𝐌𝐎𝐕𝐈𝐄 𝐍𝐀𝐌𝐄 𝐁𝐀𝐁𝐘 ")


def find_movie(update, context):
    search_results = update.message.reply_text("🔍\n𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴...........")
    query = update.message.text
    movies_list = search_movies(query)
    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = InlineKeyboardButton(movie["title"], callback_data=movie["id"])
            keyboards.append([keyboard])
        reply_markup = InlineKeyboardMarkup(keyboards)
        search_results.edit_text('𝐒𝐞𝐚𝐫𝐜𝐡 𝐑𝐞𝐬𝐮𝐥𝐭𝐬........', reply_markup=reply_markup)
    else:
        search_results.edit_text('ˢᴼᴿᴿʸ ʸᴼᵁᴿ ˢᴱᴬᴿᶜᴴᴵᴺᴳ ᴿᴱˢᵁᴸᵀˢ ᴮᴼᵀ ᶠᴼᵁᴺᴰ ⌕!\nᴘʟᴇᴀꜱᴇ 🙏 ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ & ꜱᴇᴀʀᴄʜ ɴᴏᴡ
        .')


def movie_result(update, context) -> None:
    query = update.callback_query
    s = get_movie(query.data)
    response = requests.get(s["img"])
    img = BytesIO(response.content)
    query.message.reply_photo(photo=img, caption=f"🎥 {s['title']}")
    link = ""
    links = s["links"]
    for i in links:
        link += "Open Link :-" + i + "\n" + links[i] + "\n\n"
    caption = f"⚡ Fast Download Links :-\n\n{link}"
    if len(caption) > 4095:
        for x in range(0, len(caption), 4095):
            query.message.reply_text(text=caption[x:x+4095])
    else:
        query.message.reply_text(text=caption)
        


def setup():
    update_queue = Queue()
    dispatcher = Dispatcher(bot, update_queue, use_context=True)
    dispatcher.add_handler(CommandHandler('start', welcome))
    dispatcher.add_handler(MessageHandler(Filters.text, find_movie))
    dispatcher.add_handler(CallbackQueryHandler(movie_result))
    return dispatcher


app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/{}'.format(TOKEN), methods=['GET', 'POST'])
def respond():
    update = Update.de_json(request.get_json(force=True), bot)
    setup().process_update(update)
    return 'ok'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}/{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"
