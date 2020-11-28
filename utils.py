"""This module contains secondary functions."""

from telebot import types

HELP_INFO = """Для начала работы бота после его запуска введите /start
Для того, чтобы перейти к выбору песни введите любой символ"""


def generate_markup(buttons):
    """Generate ReplyKeyboardMarkup.

    :param buttons: (list) List, containing button labels
    :return markup: Keyboard markup object
    """
    buttons = [types.KeyboardButton(f'{i}') for i in buttons]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                       one_time_keyboard=True)
    markup.add(*buttons)
    return markup
