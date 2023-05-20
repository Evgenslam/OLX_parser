import asyncio
import time
import copy
import requests
from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from keyboards import yes_no_menu_inl, district_menu_inl, districts_dict, resume_alter_menu_inl
from telegram import Telegram
from decouple import config
from loader import db, dp
from module import get_cards, get_offer, format_text, convert_params
from typing import List

url = 'https://www.olx.uz/d/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/'
tg = Telegram(bot_token=config('bot_token'), chat_id=config('chat_id'))

payload_boilerplate = {
    'currency': 'UZS',
    'districts': [],
}


class FSMSelectParams(StatesGroup):
    price_from = State()
    price_to = State()
    district = State()
    start_parsing = State()
    rooms_from = State()
    rooms_to = State()
    area_from = State()
    area_to = State()
    start_delivery = State()
    resume_delivery = State()
    check_params = State()
    change_params = State()
    stop_delivery = State()


# @dp.message_handler(commands=['start'], state='*')
@dp.message(Command(commands=["start"]))
async def command_start(message: types.Message, state: FSMContext): #not sure if state: FSMContext is used in the
    # newer version of aiogram
    '''
    Launch the bot. By user_id check if the user is new or not. If new, propose to pick params starting price_to. Switch
    FMS to price_to.
    '''
    await state.finish()
    user_tg_id = message['from']['id']
    async with state.proxy() as data:
        data['user_id'] = message['from']['id']

    # TODO: use REDIS instead of state.proxy()
    if db.verification(user_tg_id):
        search_params = eval(*db.fetch('search_params', user_tg_id))
        ru_params = convert_params(search_params)
        await message.answer(f'Я тебя знаю, приятель! Твой последний запрос: \n\n{ru_params}\n\n Посмотреть параметры '
                             'запроса можно также в меню.',
                             reply_markup=resume_alter_menu_inl)
        await FSMSelectParams.resume_delivery.set()

    else:
        async with state.proxy() as data:
            data['user_id'] = message['from']['id']
        await message.answer('Для начала расскажите, какая квартира вас интересует. Какую минимальную цену вы готовы '
                             'платить в месяц? Для справки: 1 000 000 сум - это чуть меньше 100 долларов.')
        # TODO: make kb for better UX
        await FSMSelectParams.price_from.set()


# @dp.message_handler(commands=['cancel'], state=*)
@dp.message(Command(commands=["cancel"]))
async def cancel_input(message: types.Message, state: FSMContext):
    global the_payload
    current_state = await state.get_state()
    if current_state:
        the_payload = {'currency': 'UZS', 'districts': []}
        await message.answer('Чтобы заново ввести параметры, нажмите /start')
        await state.finish()
    else:
        await message.answer('Вы пока ещё ничего не вводили. Прямо сейчас можете ввести минимальную цену')
        await FSMSelectParams.price_from.set()


# @dp.message_handler()
async def process_price_from(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['search[filter_float_price:from]'] = message.text
    # the_payload['search[filter_float_price:from]'] = message.text
    await message.answer('Какую максимальную цену в сумах вы готовы платить в месяц? '
                         'Для справки: 1 000 000 сум - это чуть меньше 100 долларов.')  # TODO: make kb for better UX
    await FSMSelectParams.price_to.set()


# @dp.message_handler()
async def process_price_to(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['search[filter_float_price:to]'] = message.text
    # the_payload['search[filter_float_price:to]'] = message.text
    await message.answer('Выберите, пожалуйста, район.',  # TODO: how to pick several districts at once?
                         reply_markup=district_menu_inl)
    await FSMSelectParams.district.set()


# @dp.message_handler()
async def process_district(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['districts'] = []
        data['districts'].append(districts_dict[callback.data])

    await callback.message.answer('Спасибо ваши данные зарегстрированы. '
                                  'Начать поиск и рассылку по вашему запросу?',
                                  reply_markup=yes_no_menu_inl)
    await FSMSelectParams.start_parsing.set()


async def parse_data(callback: types.CallbackQuery, state: FSMContext):
    print('Ща будем парсить')
    await callback.message.answer('Как только появится подходящее объявление, мы сразу кинем ссылку на него сюда.')

    user_query = await state.get_data()
    user_id = user_query.pop('user_id')
    search_params = copy.deepcopy(user_query)
    search_districts = user_query.pop('districts')
    payload = payload_boilerplate | user_query
    search_link = requests.get(url=url, params=payload).url  # TODO: use urllib to avoid making an extra request
    print(search_link)

    while await state.get_state() == 'FSMSelectParams:start_parsing':  # TODO: add a state to be able to finish
        cards: List[str] = get_cards(url=search_link)  # TODO: pass search_link from the above to avoid double job
        for card in cards:
            if not db.is_in_db(card):
                offer = get_offer(card, search_districts)
                if offer:
                    offer['user_id'] = user_id
                    offer['search_link'] = search_link
                    offer['параметры_поиска'] = str(search_params)
                    text = format_text(offer)
                    db.send_to_db(offer)  # TODO: поменять chat id на динамический, вытаскивать из message
                    tg.send_telegram(text)  # TODO: Filter by number. Change tg to send_message
                    # TODO: add sent or not field, add field with generated link
        await asyncio.sleep(randint(30, 40))


async def resume_delivery(callback: types.CallbackQuery, state: FSMContext):
    print('Возобновляем рассылку.')
    await callback.message.answer('Как только появится подходящее объявление, мы сразу кинем ссылку на него сюда.')
    user_id = callback.message['chat']['id']
    search_link = db.fetch('search_link', user_id)[0]

    while await state.get_state() == 'FSMSelectParams:resume_delivery':  # TODO: add a state to be able to finish
        cards: List[str] = get_cards(url=search_link)
        for card in cards:
            if not db.is_in_db(card):
                search_params = eval(*db.fetch('search_params', user_id))
                search_districts = search_params['districts']
                offer = get_offer(card, search_districts)
                if offer:
                    offer['user_id'] = user_id
                    offer['search_link'] = search_link
                    offer['параметры_поиска'] = str(search_params)  # TODO: translate into Russian
                    text = format_text(offer)
                    db.send_to_db(offer)  # TODO: поменять chat id на динамический, вытаскивать из message
                    tg.send_telegram(text)  # TODO: Filter by number. Change tg to send_message
                    # TODO: add sent or not field, add field with generated link

        await asyncio.sleep(randint(30, 40))


async def check_params(message: types.Message, state: FSMContext):
    await message.answer('Вот ваши параметры!')
    search_params = eval(*db.fetch('search_params', message['from']['id']))
    ru_params = convert_params(search_params)
    await message.answer(ru_params)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start'], state='*')
    dp.register_message_handler(cancel_input, commands=['cancel'], state='*')
    dp.register_message_handler(process_price_from, state=FSMSelectParams.price_from)
    dp.register_message_handler(process_price_to, state=FSMSelectParams.price_to)
    dp.register_callback_query_handler(process_district, state=FSMSelectParams.district)
    dp.register_callback_query_handler(parse_data, text=['yes'], state=FSMSelectParams.start_parsing)
    dp.register_callback_query_handler(resume_delivery, text=['yes'], state=FSMSelectParams.resume_delivery)
    dp.register_message_handler(check_params, commands=['see_my_params'], state='*')
