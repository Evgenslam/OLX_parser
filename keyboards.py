from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pprint import pprint

def create_inline_kb(row_width: int, **kwargs) -> InlineKeyboardMarkup:
    inline_kb: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=row_width)
    [inline_kb.insert(InlineKeyboardButton(
                      text=text,
                      callback_data=button))
                      for button, text in kwargs.items()]
    return inline_kb

districts =['Мирзо-Улугбекский', 'Сергелийский', 'Яшнабадский', 'Чиланзарский', 'Мирабадский', 'Юнусабадский',
              'Алмазарский', 'Яккасарайский', 'Шайхантахурский']
districts_eng = ['Mirzo-Ulugbekskii', 'Sergeliiskii', 'Yashnabadskii', 'Chilanzarskii', 'Mirabadskii',
                  'Yunusabadskii','Almazarski', 'Yakkasaraiski', 'Shaikhantakhurskii']

districts_dict = dict(zip(districts_eng, districts))
yes_no_dict = {'yes': 'да', 'no': 'нет'}

district_menu_inl = create_inline_kb(2, **districts_dict)
yes_no_menu_inl = create_inline_kb(1, **yes_no_dict)


# yes_no_menu_inl: InlineKeyboardMarkup = InlineKeyboardMarkup()
# yes_button: InlineKeyboardButton = InlineKeyboardButton(
#                                     text='да',
#                                     callback_data='yes'
# )
#
# no_button: InlineKeyboardButton  = InlineKeyboardButton(
#                                     text='нет',
#                                     callback_data='no'
# )
#
# yes_no_menu_inl.row(yes_button, no_button)
