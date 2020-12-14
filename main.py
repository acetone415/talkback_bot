"""Main Bot module."""

from telebot import TeleBot
import database
import config
import utils


bot = TeleBot(config.TOKEN)


@bot.message_handler(commands=["help"])
def print_help_info(message):
    """Print help information."""
    bot.send_message(message.chat.id, text=utils.HELP_INFO)


def is_home_button(message) -> bool:
    """Check if message.text == 'В начало'.
    :param message: Message object
    :return: bool"""
    if message.text == 'В начало':
        bot.send_message(message.chat.id, "Нажмите кнопку для продожения",
                         reply_markup=utils.generate_markup(['Начать работу'],
                                                            btn_home=False))
        bot.register_next_step_handler(message, level1_keyboard)
        return True
    return False


@bot.message_handler(content_types=['text'])
def level1_keyboard(message):
    """First keyboard level."""
    if message.text not in ['Выбрать автора', 'Выбрать песню']:
        bot.send_message(
            message.chat.id, text='Что вы хотите выбрать?',
            reply_markup=utils.generate_markup(['Выбрать автора',
                                                'Выбрать песню'],
                                               btn_home=False))
    elif message.text == 'Выбрать автора':
        bot.send_message(
            message.chat.id, text='С какой буквы начинается имя автора?',
            reply_markup=utils.generate_markup(config.AUTHOR_KEYBOARD))
        bot.register_next_step_handler(message, level2_keyboard,
                                       field='author', previous_buttons=config.AUTHOR_KEYBOARD)
    elif message.text == 'Выбрать песню':
        bot.send_message(
            message.chat.id, text='С какой буквы начинается название песни?',
            reply_markup=utils.generate_markup(config.SONG_KEYBOARD))
        bot.register_next_step_handler(message, level2_keyboard, field='song', previous_buttons=config.SONG_KEYBOARD)


def level2_keyboard(message, field, previous_buttons):
    """Second keyboard level, where you chose first letter of author or song.

    :param field: (str) Field in DB by which song is selected
    """
    # the dictionary is needed to substitute the field name into the
    # "text" parameter in bot.send_message
    field_to_text = {'song': 'песню', 'author': 'автора'}

    if is_home_button(message):
        pass

    elif message.text not in previous_buttons:
        # If sent message not in reply markup
        bot.send_message(message.chat.id,
                         "Некорректный ввод, попробуйте снова",
                         reply_markup=utils.generate_markup(previous_buttons))
        bot.register_next_step_handler(message, level2_keyboard, field, previous_buttons)

    else:
        db = database.Database(config.DATABASE_NAME)
        result = db.select_field_by_letter(letter=message.text.upper(),
                                           field=field)
        db.close()

        buttons = [f'{i[0]}' for i in result]
        markup = utils.generate_markup(buttons, row_width=2)

        bot.send_message(
            message.chat.id, text=f"Выберите {field_to_text[field]}",
            reply_markup=markup)
        bot.register_next_step_handler(message, level3_keyboard, field=field,
                                       previous_buttons=buttons)


def level3_keyboard(message, field, previous_buttons):
    """Last keyboard level, where you choose song to send in group channel."""

    if is_home_button(message):
        pass

    elif message.text not in previous_buttons:
        # If sent message not in reply markup
        bot.send_message(message.chat.id,
                         "Некорректный ввод, попробуйте снова",
                         reply_markup=utils.generate_markup(previous_buttons))
        bot.register_next_step_handler(message, level3_keyboard, field,
                                       previous_buttons)

    else:
        db = database.Database(config.DATABASE_NAME)
        result = db.select_pair(item=message.text, field=field)
        db.close()

        buttons = [f'{" - ".join(i)}' for i in result]
        markup = utils.generate_markup(buttons, row_width=1)

        bot.send_message(message.chat.id, text='Выбирайте', reply_markup=markup)
        bot.register_next_step_handler(message, send_to_channel,
                                       previous_buttons=buttons)


def send_to_channel(message, previous_buttons):
    """Send chosen song to group channel."""

    if is_home_button(message):
        pass

    elif message.text not in previous_buttons:
        # If sent message not in reply markup
        bot.send_message(message.chat.id,
                         "Некорректный ввод, попробуйте снова",
                         reply_markup=utils.generate_markup(previous_buttons))
        bot.register_next_step_handler(message, send_to_channel,
                                       previous_buttons)
    else:
        bot.send_message(chat_id=config.GROUP_CHANNEL_ID,
                         text=f"{message.text} is next",)
        bot.send_message(chat_id=message.chat.id,
                         text="Для продолжения нажмите на кнопку",
                         reply_markup=utils.generate_markup([]))


@bot.message_handler(content_types=['document'])
def download_file(message):
    """Download the tracklist from user."""
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(config.TRACKLIST_NAME, 'wb') as new_file:
        new_file.write(downloaded_file)

    db = database.Database(config.DATABASE_NAME)
    db.load_tracklist_from_file(config.TRACKLIST_NAME)
    config.AUTHOR_KEYBOARD, config.SONG_KEYBOARD = db.get_keyboards()
    db.close()


if __name__ == "__main__":
    bot.infinity_polling()
