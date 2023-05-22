from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def create_inline_kb(row_width: int, **kwargs: str) -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text=text, callback_data=button)
                          for button, text in kwargs.items()]
    kb_builder.row(*buttons, width=row_width)
    return kb_builder.as_markup()


districts =['Мирзо-Улугбекский', 'Сергелийский', 'Яшнабадский', 'Чиланзарский', 'Мирабадский', 'Юнусабадский',
              'Алмазарский', 'Яккасарайский', 'Шайхантахурский']
districts_eng = ['Mirzo-Ulugbekskii', 'Sergeliiskii', 'Yashnabadskii', 'Chilanzarskii', 'Mirabadskii',
                  'Yunusabadskii','Almazarski', 'Yakkasaraiski', 'Shaikhantakhurskii']

#Бектемирский - 18, Учтепинский - 21
#new format of link
#ps://www.olx.uz/d/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/
# ?search%5Bdistrict_id%5D=18&
# search%5Bfilter_float_price:from%5D=5000&
# search%5Bfilter_float_price:to%5D=60000&
# search%5Bfilter_float_number_of_rooms:from%5D=3&
# search%5Bfilter_float_number_of_rooms:to%5D=5&
# search%5Bfilter_float_floor:from%5D=1&
# search%5Bfilter_float_floor:to%5D=7&
# search%5Bfilter_float_total_floors:from%5D=1&
# search%5Bfilter_float_total_floors:to%5D=16&
# search%5Bfilter_enum_furnished%5D%5B0%5D=yes&
# search%5Bfilter_enum_comission%5D%5B0%5D=no&
# search%5Bfilter_float_total_area:from%5D=20&
# search%5Bfilter_float_total_area:to%5D=150&
# currency=UZS

district_ids = [12, 19, 22, 23, 13, 25, 20, 26, 24]

districts_dict = dict(zip(districts_eng, districts))
districts_dict['finish'] = 'выбрать'
district_ids_dict = dict(zip(districts, district_ids))

yes_no_dict = {'yes': 'да', 'no': 'нет'}
resume_alter_dict = {'resume': 'Возобновить рассылку по этим параметрам', 'alter': 'Изменить параметры'}

district_menu_inl = create_inline_kb(2, **districts_dict)
yes_no_menu_inl = create_inline_kb(2, **yes_no_dict)
resume_alter_menu_inl = create_inline_kb(2, **resume_alter_dict)


