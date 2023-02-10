from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

yes_no_menu_inl: InlineKeyboardMarkup = InlineKeyboardMarkup()
yes_button: InlineKeyboardButton  = InlineKeyboardButton(
                                    text='да',
                                    callback_data='yes'
)

no_button: InlineKeyboardButton  = InlineKeyboardButton(
                                    text='нет',
                                    callback_data='no'
)

yes_no_menu_inl.add(yes_button).add(no_button)