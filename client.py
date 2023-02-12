import time
from random import randint
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from keyboards import yes_no_menu_inl
from database import Database
from telegram import Telegram
from decouple import config
from module import get_cards, get_offer, format_text
from typing import List
from pprint import pprint

#user_phone = input('Пожалуйста, введите свой номер телефона: ')
url = 'https://www.olx.uz/d/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/'
tg = Telegram(bot_token=config('bot_token'), chat_id=config('chat_id'))

the_payload = {'currency': 'UZS'}
           # 'search[filter_float_price:from]': None,
           # 'search[filter_float_price:to]': None
           # }
user_tg_ids = []

class FSMSelectParams(StatesGroup):
    price_from = State()
    price_to = State()
    start_parsing = State()
    # rooms_from = State()
    # rooms_to = State()
    # area_from = State()
    # area_to = State()
    # start_delivery = State()
    # check_params = State()
    # change_params = State()
    # stop_delivery = State()


# @dp.message_handler(commands=['start'], state='*')
async def command_start(message: types.Message, state: FSMContext):
    '''
    Запуск бота. Предлагаем выбрать параметры. Сначала минимальная цена. Переводим в состояние price_to.
    When bot is running
    '''
    try:
        user_tg_id = message['from']['id']
        if user_tg_id not in user_tg_ids:
            user_tg_ids.append(user_tg_id)
        async with state.proxy() as data:
            data['user_tg_id'] = message['from']['id']
        await message.answer('Для начала расскажите, какая квартира вас интересует. Какую минимальную цену вы готовы '
                             'платить в месяц? Для справки: 1 000 000 сум - это чуть меньше 100 долларов.')
        await FSMSelectParams.price_from.set()
    except:
        await message.reply('Общение с ботом через ЛС. Напишите ему: ')


# @dp.message_handler(commands=['cancel'], state=*)
async def cancel_input(message: types.Message, state: FSMContext):
    global the_payload
    current_state = await state.get_state()
    if current_state:
        the_payload = {'currency': 'UZS'}
        await message.answer('Чтобы заново ввести параметры, нажмите /start')
        await state.finish()
    else:
        await message.answer('Вы пока ещё ничего не вводили. Прямо сейчас можете ввести минимальную цену')
        await FSMSelectParams.price_from.set()


# @dp.message_handler()
async def process_price_from(message: types.Message, state: FSMContext):
    # async with state.proxy() as data:
    #     data['price_from'] = message.text
    # the_payload['search[filter_float_price:from]'] = state.get_data()
    the_payload['search[filter_float_price:from]'] = message.text
    await message.answer('Какую максимальную цену в сумах вы готовы платить в месяц? '
                        'Для справки: 1 000 000 сум - это чуть меньше 100 долларов.')
    await FSMSelectParams.price_to.set()


# @dp.message_handler()
async def process_price_to(message: types.Message, state: FSMContext):
    #nullify the state.proxy()
    #go back to start
    the_payload['search[filter_float_price:to]'] = message.text
    await message.answer('Спасибо ваши данные зарегстрированы.')
    await state.finish()
    await message.answer('Начать поиск и рассылку по вашему запросу?',
                        reply_markup=yes_no_menu_inl)
    await FSMSelectParams.start_parsing.set()


def parse_data(callback: types.CallbackQuery, state: FSMContext):
    print('Ща будем парсить')
    while True:
        db = Database(db_path='DB/realty5.db')  # TODO: add number field
        cards: List[str] = get_cards(url=url, payload=the_payload)
        for card in cards:
            if not db.is_in_db(card):
                offer = get_offer(card)
                offer['user_id'] = user_tg_ids[-1]
                print(offer)
                text = format_text(offer)
                db.send_to_db(offer)   # TODO: adjust to pass more data
                tg.send_telegram(text) # TODO: Filter by number. Change tg to send_message
                                       # TODO: add sent or not field, add field with generated  link

        time.sleep(randint(30, 40))


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start'], state='*')
    dp.register_message_handler(cancel_input, commands=['cancel'], state='*')
    dp.register_message_handler(process_price_from, state=FSMSelectParams.price_from)
    dp.register_message_handler(process_price_to, state=FSMSelectParams.price_to)
    dp.register_callback_query_handler(parse_data, text=['yes'], state=FSMSelectParams.start_parsing)
