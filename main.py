from telebot import TeleBot, types
import database
import config

bot = TeleBot(config.TOKEN)
AUTHOR_KEYBOARD, SONG_KEYBOARD = [], []


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

    bot.send_message(
        message.chat.id, text='Что вы хотите выбрать?',
        reply_markup=generate_markup(['Выбрать автора',
                                      'Выбрать песню']))


@bot.message_handler(content_types=['text'])
def level1_keyboard(message):
    if message.text == 'Выбрать автора':
        bot.send_message(
            message.chat.id, text='С какой буквы начинается имя автора?',
            reply_markup=generate_markup(AUTHOR_KEYBOARD))
        bot.register_next_step_handler(message, select_author)
    elif message.text == 'Выбрать песню':
        bot.send_message(
            message.chat.id, text='С какой буквы начинается название песни?',
            reply_markup=generate_markup(SONG_KEYBOARD))
        bot.register_next_step_handler(message, select_song)


def select_author(message):
    db = database.Database(config.DATABASE_NAME)
    result = db.select_field_by_letter(letter=message.text, field='author')
    buttons = [f'{i[0]}' for i in result]
    markup = generate_markup(buttons)
    bot.send_message(
        message.chat.id, text="Выберите автора",
        reply_markup=markup)
    db.close()
    bot.register_next_step_handler(message, choose_song_and_author)


def select_song(message):
    db = database.Database(config.DATABASE_NAME)
    result = db.select_field_by_letter(letter=message.text, field='song')
    buttons = [f'{i[0]}' for i in result]
    markup = generate_markup(buttons)
    bot.send_message(
        message.chat.id, text="Выберите песню",
        reply_markup=markup)
    db.close()


def choose_song_and_author(message):
    db = database.Database(config.DATABASE_NAME)
    result = db.select_pair(item=message.text, field='author')
    buttons = [f'{" - ".join(i)}' for i in result]
    markup = generate_markup(buttons)
    bot.send_message(message.chat.id, text='choose', reply_markup=markup)


if __name__ == "__main__":
    bot.infinity_polling()

