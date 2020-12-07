"""This module contains secondary functions."""

from telebot import types

HELP_INFO = """Для начала работы бота после его запуска введите /start
Для того, чтобы перейти к выбору песни, введите любой символ
Для обновления треклиста просто загрузите его"""


def generate_markup(buttons, btn_back=False, btn_home=False, row_width=5):
    """Generate ReplyKeyboardMarkup.

    :param buttons: (list) List, containing button labels
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
