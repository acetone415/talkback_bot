from telebot import TeleBot, types
import database
import config

bot = TeleBot(config.TOKEN)
AUTHOR_KEYBOARD, SONG_KEYBOARD = [], []
btn1, btn2, btn_home = 'Выбрать автора', 'Выбрать песню', 'В Начало'


def generate_markup(buttons):
    buttons = [types.KeyboardButton(f'{i}') for i in buttons]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                       one_time_keyboard=False)
    markup.add(*buttons)
    return markup


@bot.message_handler(commands=["start"])
def start_bot(message):
    db = database.Database(config.DATABASE_NAME)
    global AUTHOR_KEYBOARD, SONG_KEYBOARD
    AUTHOR_KEYBOARD, SONG_KEYBOARD = db.get_keyboards()
    db.close()

    bot.send_message(message.chat.id, text='Выберите',
                     reply_markup=generate_markup([btn1, btn2]))



@bot.message_handler(content_types=['text'])
def level1_keyboard(message):
    if message.text == btn1:
        text, keyboard, func = 'Выберите автора', AUTHOR_KEYBOARD, select_author
        bot.send_message(
            message.chat.id, text=text,
            reply_markup=generate_markup(keyboard))
        bot.register_next_step_handler(message, func)
    elif message.text == btn2:
        text, keyboard, func = 'Выберите песню', SONG_KEYBOARD, select_song
        bot.send_message(
            message.chat.id, text=text,
            reply_markup=generate_markup(keyboard))
        bot.register_next_step_handler(message, func)


def select_author(message):
    db = database.Database(config.DATABASE_NAME)
    result = db.select_field_by_letter(letter=message.text, field='author')
    buttons = [f'{i[0]}' for i in result]
    markup = generate_markup(buttons)
    bot.send_message(
        message.chat.id, text="Выберите песню",
        reply_markup=markup)
    db.close()


def select_song(message):
    db = database.Database(config.DATABASE_NAME)
    result = db.select_field_by_letter(letter=message.text, field='song')
    buttons = [f'{i[0]}' for i in result]
    markup = generate_markup(buttons)
    bot.send_message(
        message.chat.id, text="Выберите песню",
        reply_markup=markup)
    db.close()


if __name__ == "__main__":
    bot.infinity_polling()

