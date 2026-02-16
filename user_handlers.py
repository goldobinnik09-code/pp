# Assuming this is the new content that replaces CallsignState.waiting

from aiogram import types

async def waiting_for_callsign_handler(message: types.Message):
    # Create inline buttons for callsign selection
    markup = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text='Callsign 1', callback_data='callsign_1'),
        types.InlineKeyboardButton(text='Callsign 2', callback_data='callsign_2'),
        types.InlineKeyboardButton(text='Callsign 3', callback_data='callsign_3'),
    ]
    markup.add(*buttons)

    await message.answer('Please select your callsign:', reply_markup=markup)