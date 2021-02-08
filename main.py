"""Main Bot module."""

from os.path import exists

from peewee import OperationalError
from telebot import TeleBot, types

import config
import database as db

bot = TeleBot(config.TOKEN)


def generate_markup(buttons,
                    btn_back=False,
                    btn_home=True,
                    row_width=5) -> types.ReplyKeyboardMarkup:
    """Generate ReplyKeyboardMarkup.

    :param buttons: __iterable object, containing button labels
    :param btn_back: (bool) Adds button "Back" to keyboard if True
    :param btn_home: (bool) Adds button "Home" to keyboard if True
    :param row_width: (int) Row width in markup
    :return markup: Keyboard markup object
    """
    buttons = [types.KeyboardButton(f'{i}') for i in buttons]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                       one_time_keyboard=True,
                                       row_width=row_width)
    markup.add(*buttons)
    navigation = []
    if btn_back:
        navigation.append(types.KeyboardButton('Назад'))
    if btn_home:
        navigation.append(types.KeyboardButton('В начало'))
    markup.row(*navigation)
    return markup


def check_database(func):
    """Check tables existense in DB.

    If something happened with database for example a table was deleted
    the bot will try to load the tracklist into the database (if it exists)
    and will repeat the handler on which the error occurred
    If there is no file tracklist.txt, then the Bot will ask you to download it.
    """

    def inner(message, *args, **kwargs):
        try:
            func(message, *args, **kwargs)

        except (OperationalError, AttributeError):
            if exists(config.TRACKLIST_NAME):
                db.load_tracklist_from_file(config.TRACKLIST_NAME)
                db.AUTHOR_KEYBOARD, db.SONG_KEYBOARD =\
                    db.get_keyboards()
                bot.send_message(
                    message.chat.id,
                    "Произошла ошибка. Повторите попытку",
                    reply_markup=generate_markup(["Повторить ввод"])
                )
                bot.register_next_step_handler(message, func, *args, **kwargs)

            else:
                bot.send_message(
                        message.chat.id,
                        text="Произошла ошибка. Загрузите треклист.",
                        reply_markup=generate_markup([]))

    return inner


def check_message(func):
    """Check if the entered text matches the keyboard keys."""
    def inner(message, *args, **kwargs):
        if message.text == 'В начало':
            bot.send_message(message.chat.id, "Нажмите кнопку для продолжения",
                             reply_markup=generate_markup(['Начать работу'],
                                                          btn_home=False))
            bot.register_next_step_handler(message, level1_keyboard)

        elif message.text not in kwargs['previous_buttons']:
            # If sent message not in reply markup
            bot.send_message(message.chat.id,
                             "Некорректный ввод, попробуйте снова",
                             reply_markup=generate_markup(
                                 kwargs['previous_buttons']))
            bot.register_next_step_handler(message,
                                           check_message(func),
                                           *args, **kwargs)
        else:
            func(message, *args, **kwargs)

    return inner


@bot.message_handler(commands=["help"])
def print_help_info(message):
    """Print help information."""
    HELP_INFO = """Для того, чтобы перейти к выбору песни, введите любой символ
Для обновления треклиста просто загрузите его"""
    bot.send_message(message.chat.id, text=HELP_INFO)


@bot.message_handler(content_types=['text'])
@check_database
def level1_keyboard(message):
    """First keyboard level."""
    if message.text not in ['Выбрать автора', 'Выбрать песню']:
        bot.send_message(
            message.chat.id, text='Что вы хотите выбрать?',
            reply_markup=generate_markup(['Выбрать автора', 'Выбрать песню'],
                                         btn_home=False))
    elif message.text == 'Выбрать автора':
        bot.send_message(
            message.chat.id, text='С какой буквы начинается имя автора?',
            reply_markup=generate_markup(db.AUTHOR_KEYBOARD))
        bot.register_next_step_handler(message,
                                       level2_keyboard,
                                       field='author',
                                       previous_buttons=db.AUTHOR_KEYBOARD)
    elif message.text == 'Выбрать песню':
        bot.send_message(
            message.chat.id, text='С какой буквы начинается название песни?',
            reply_markup=generate_markup(db.SONG_KEYBOARD))
        bot.register_next_step_handler(message, level2_keyboard, field='song',
                                       previous_buttons=db.SONG_KEYBOARD)


@check_database
@check_message
def level2_keyboard(message, *args, **kwargs):
    """Second keyboard level, where you chose first letter of author or song."""
    # the dictionary is needed to substitute the field name into the
    # "text" parameter in bot.send_message
    field_to_text = {'song': 'песню', 'author': 'автора'}

    result = db.select_field_by_letter(letter=message.text.upper(),
                                       field=kwargs['field'])

    buttons = [f'{i}' for i in result]
    markup = generate_markup(buttons, row_width=2)

    bot.send_message(
        message.chat.id,
        text=f"Выберите {field_to_text[kwargs['field']]}",
        reply_markup=markup)
    bot.register_next_step_handler(message,
                                   level3_keyboard,
                                   field=kwargs['field'],
                                   previous_buttons=buttons)


@check_database
@check_message
def level3_keyboard(message, *args, **kwargs):
    """Last keyboard level, where you choose song to send in group channel."""
    result = db.select_pair(item=message.text, field=kwargs['field'])

    buttons = [f'{" - ".join(i)}' for i in result]
    markup = generate_markup(buttons, row_width=1)

    bot.send_message(message.chat.id, text='Выбирайте', reply_markup=markup)
    bot.register_next_step_handler(message, send_to_channel,
                                   previous_buttons=buttons)


@check_message
def send_to_channel(message, *args, **kwargs):
    """Send chosen song to group channel."""
    bot.send_message(chat_id=config.GROUP_CHANNEL_ID,
                     text=f"{message.text} is next",)
    bot.send_message(chat_id=message.chat.id,
                     text="Для продолжения нажмите на кнопку",
                     reply_markup=generate_markup([]))


@bot.message_handler(content_types=['document'])
def download_file(message):
    """Download the tracklist from user."""
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(config.TRACKLIST_NAME, 'wb') as new_file:
        new_file.write(downloaded_file)

    db.load_tracklist_from_file(config.TRACKLIST_NAME)
    db.AUTHOR_KEYBOARD, db.SONG_KEYBOARD = db.get_keyboards()


if __name__ == "__main__":
    bot.infinity_polling()
