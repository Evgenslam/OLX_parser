from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def create_inline_kb(row_width: int, **kwargs: str) -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text=text, callback_data=button)
                          for button, text in kwargs.items()]
    kb_builder.row(*buttons, width=row_width)
    return kb_builder.as_markup()

# TODO: move main menu func here

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


#https://www.olx.uz/d/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?currency=UZS&price_from=1000000&price_to
# =5000000
district_ids = [12, 19, 22, 23, 13, 25, 20, 26, 24]

districts_dict = dict(zip(districts_eng, districts))
districts_dict['finish'] = 'выбрать'
district_ids_dict = dict(zip(districts, district_ids))

price_dict = {str(x*11420): f'{x} $' for x in range(100, 1100, 100)}
yes_no_dict = {'yes': 'да', 'no': 'нет'}
resume_alter_dict = {'resume': 'Возобновить рассылку', 'alter': 'Изменить параметры'}


price_menu_inl = create_inline_kb(3, **price_dict)
district_menu_inl = create_inline_kb(2, **districts_dict)
yes_no_menu_inl = create_inline_kb(2, **yes_no_dict)
resume_alter_menu_inl = create_inline_kb(2, **resume_alter_dict)


# ?search[district_id]=18&: This parameter indicates the district ID to search for, and its value is 18.
# search[filter_float_price:from]=5000&: This parameter represents the minimum price range, and its value is 5000.
# search[filter_float_price:to]=60000&: This parameter represents the maximum price range, and its value is 60000.
# search[filter_float_number_of_rooms:from]=3&: This parameter represents the minimum number of rooms, and its value is 3.
# search[filter_float_number_of_rooms:to]=5&: This parameter represents the maximum number of rooms, and its value is 5.
# search[filter_float_floor:from]=1&: This parameter represents the minimum floor number, and its value is 1.
# search[filter_float_floor:to]=7&: This parameter represents the maximum floor number, and its value is 7.
# search[filter_float_total_floors:from]=1&: This parameter represents the minimum total number of floors, and its value is 1.
# search[filter_float_total_floors:to]=16&: This parameter represents the maximum total number of floors, and its value is 16.
# search[filter_enum_furnished][0]=yes&: This parameter indicates whether the property is furnished, and its value is yes.
# search[filter_enum_comission][0]=no&: This parameter indicates whether a commission is applicable, and its value is no.
# search[filter_float_total_area:from]=20&: This parameter represents the minimum total area, and its value is 20.
# search[filter_float_total_area:to]=150&: This parameter represents the maximum total area, and its value is 150.


theirlink = 'https://www.olx.uz/d/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?currency=UZS&search\%5Bfilter_float_price:from%5D=1000000&search%5Bfilter_float_price:to%5D=5000000'
mylink = 'https://www.olx.uz/d/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?currency=UZS&search%5Bfilter_float_price%3Afrom%5D=1000000&search%5Bfilter_float_price%3Ato%5D=5000000'

#print(theirlink == mylink)