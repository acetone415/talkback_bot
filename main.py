from telebot import TeleBot
import database
import config
import utils

bot = TeleBot(config.TOKEN)
AUTHOR_KEYBOARD, SONG_KEYBOARD = [], []


@bot.message_handler(commands=["start"])
def start_bot(message):
    db = database.Database(config.DATABASE_NAME)
    global AUTHOR_KEYBOARD, SONG_KEYBOARD
    AUTHOR_KEYBOARD, SONG_KEYBOARD = db.get_keyboards()
    db.close()


@bot.message_handler(commands=["help"])
def print_help_info(message):
    bot.send_message(message.chat.id, text=utils.HELP_INFO)


@bot.message_handler(content_types=['text'])
def level1_keyboard(message):
    if message.text not in ['Выбрать автора', 'Выбрать песню']:
        bot.send_message(
            message.chat.id, text='Что вы хотите выбрать?',
            reply_markup=utils.generate_markup(['Выбрать автора',
                                                'Выбрать песню']))
    elif message.text == 'Выбрать автора':
        bot.send_message(
            message.chat.id, text='С какой буквы начинается имя автора?',
            reply_markup=utils.generate_markup(AUTHOR_KEYBOARD))
        bot.register_next_step_handler(message, level2_keyboard, field='author')
    elif message.text == 'Выбрать песню':
        bot.send_message(
            message.chat.id, text='С какой буквы начинается название песни?',
            reply_markup=utils.generate_markup(SONG_KEYBOARD))
        bot.register_next_step_handler(message, level2_keyboard, field='song')


def level2_keyboard(message, field):
    db = database.Database(config.DATABASE_NAME)
    # the dictionary is needed to substitute the field name into the "text"
    # parameter in bot.send_message
    field_to_text = {'song': 'песню', 'author': 'автора'}
    result = db.select_field_by_letter(letter=message.text, field=field)
    buttons = [f'{i[0]}' for i in result]
    markup = utils.generate_markup(buttons)
    bot.send_message(
        message.chat.id, text=f"Выберите {field_to_text[field]}",
        reply_markup=markup)
    db.close()
    bot.register_next_step_handler(message, level3_keyboard, field=field)


def level3_keyboard(message, field):
    db = database.Database(config.DATABASE_NAME)
    result = db.select_pair(item=message.text, field=field)
    buttons = [f'{" - ".join(i)}' for i in result]
    markup = utils.generate_markup(buttons)
    bot.send_message(message.chat.id, text='Выбирайте', reply_markup=markup)
    db.close()


if __name__ == "__main__":
    bot.infinity_polling()
