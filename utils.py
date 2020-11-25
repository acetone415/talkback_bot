from telebot import types


def generate_markup(buttons):
    buttons = [types.KeyboardButton(f'{i}') for i in buttons]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                       one_time_keyboard=False)
    markup.add(*buttons)
    return markup
