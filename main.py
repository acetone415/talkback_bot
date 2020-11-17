from telebot import TeleBot, types
import config
from tracklist_handler import load_tracklist

song_list = load_tracklist(config.TRACKLIST_NAME)[2]
bot = TeleBot(config.TOKEN)


@bot.message_handler(commands=["start"])
def keyboard(message):
    markup = types.ReplyKeyboardMarkup(row_width=10)
    buttons = [types.KeyboardButton(f'{i}') for i in song_list]
    markup.add(*buttons)
    bot.send_message(message.chat.id, text='choose', reply_markup=markup)


if __name__ == "__main__":
    bot.infinity_polling()
