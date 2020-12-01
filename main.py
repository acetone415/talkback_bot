"""Main Bot module."""

from telebot import TeleBot
import database
import config
import utils


bot = TeleBot(config.TOKEN)
AUTHOR_KEYBOARD, SONG_KEYBOARD = [], []


@bot.message_handler(commands=["start"])
def start_bot(message):
    """Initialise bot setup after launching the bot."""
    db = database.Database(config.DATABASE_NAME)
    global AUTHOR_KEYBOARD, SONG_KEYBOARD
    AUTHOR_KEYBOARD, SONG_KEYBOARD = db.get_keyboards()
    db.close()


def get_started(message):
    """Generate a start button."""
    bot.send_message(message.chat.id, text="Нажмите кнопку для начала работы",
                     reply_markup=utils.generate_markup(["Начать работу"]))


@bot.message_handler(commands=["help"])
def print_help_info(message):
    """Print help information."""
    bot.send_message(message.chat.id, text=utils.HELP_INFO)


@bot.message_handler(content_types=['text'])
def level1_keyboard(message):
    """First keyboard level."""
    if message.text not in ['Выбрать автора', 'Выбрать песню']:
        bot.send_message(
            message.chat.id, text='Что вы хотите выбрать?',
            reply_markup=utils.generate_markup(['Выбрать автора',
                                                'Выбрать песню']))
    elif message.text == 'Выбрать автора':
        bot.send_message(
            message.chat.id, text='С какой буквы начинается имя автора?',
            reply_markup=utils.generate_markup(AUTHOR_KEYBOARD))
        bot.register_next_step_handler(message, level2_keyboard,
                                       field='author')
    elif message.text == 'Выбрать песню':
        bot.send_message(
            message.chat.id, text='С какой буквы начинается название песни?',
            reply_markup=utils.generate_markup(SONG_KEYBOARD))
        bot.register_next_step_handler(message, level2_keyboard, field='song')


def level2_keyboard(message, field):
    """Second keyboard level, where you chose first letter of author or song.

    :param field: (str) Field in DB by which song is selected
    """
    # the dictionary is needed to substitute the field name into the
    # "text" parameter in bot.send_message
    field_to_text = {'song': 'песню', 'author': 'автора'}

    db = database.Database(config.DATABASE_NAME)
    result = db.select_field_by_letter(letter=message.text, field=field)
    db.close()

    buttons = [f'{i[0]}' for i in result]
    markup = utils.generate_markup(buttons, row_width=2)

    bot.send_message(
        message.chat.id, text=f"Выберите {field_to_text[field]}",
        reply_markup=markup)
    bot.register_next_step_handler(message, level3_keyboard, field=field)


def level3_keyboard(message, field):
    """Last keyboard level, where you choose song to send in group channel."""
    db = database.Database(config.DATABASE_NAME)
    result = db.select_pair(item=message.text, field=field)
    db.close()

    buttons = [f'{" - ".join(i)}' for i in result]
    markup = utils.generate_markup(buttons, row_width=1)

    bot.send_message(message.chat.id, text='Выбирайте', reply_markup=markup)
    bot.register_next_step_handler(message, send_to_channel)


def send_to_channel(message):
    """Send chosen song to group channel."""
    bot.send_message(chat_id=config.GROUP_CHANNEL_ID,
                     text=f"{message.text} is next",)
    bot.send_message(chat_id=message.chat.id,
                     text="Для продолжения нажмите на кнопку",
                     reply_markup=utils.generate_markup(['Начать работу']))


@bot.message_handler(content_types=['document'])
def download_file(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(config.TRACKLIST_NAME, 'wb') as new_file:
        new_file.write(downloaded_file)

    db = database.Database(config.DATABASE_NAME)
    db.load_tracklist_from_file(config.TRACKLIST_NAME)
    db.close()

    bot.register_next_step_handler(message, start_bot)



if __name__ == "__main__":
    bot.infinity_polling()
