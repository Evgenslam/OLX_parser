import asyncio
import copy
from random import randint

import requests
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, Text, StateFilter
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.state import default_state
from keyboards import yes_no_menu_inl, district_menu_inl, districts_dict, resume_alter_menu_inl
from telegram import Telegram
from decouple import config
from loader import db, dp
from module import get_cards, get_offer, format_text, convert_params
from typing import List
from pprint import pprint

url = 'https://www.olx.uz/d/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/'
tg = Telegram(bot_token=config('bot_token'), chat_id=config('chat_id'))
user_dict: dict[int, dict[str | int]] = {}
#districts: list[str] = []

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

router: Router = Router()
router_district: Router = Router()

router_district.callback_query.filter(StateFilter(FSMSelectParams.district))

# @dp.message_handler(commands=['start'], state='*') # old type of decorator
@router.message(CommandStart())  # new type of decorator , #StateFilter(default_state
async def command_start(message: types.Message, state: FSMContext):
    '''
    Launch the bot. By user_id check if the user is new or not. If new, propose to pick params starting price_to. Switch
    FMS to price_to.
    '''
    user_tg_id = message.from_user.id
    if db.verification(user_tg_id):
        search_params = eval(*db.fetch('search_params', user_tg_id))
        ru_params = convert_params(search_params)
        await message.answer(f'Я тебя знаю, приятель! Твой последний запрос: \n\n{ru_params}\n\n Посмотреть параметры '
                             'запроса можно также в меню.',
                             reply_markup=resume_alter_menu_inl)
        await state.set_state(FSMSelectParams.resume_delivery)

    else:
        await message.answer('Для начала расскажите, какая квартира вас интересует. Какую минимальную цену вы готовы '
                             'платить в месяц? Для справки: 1 000 000 сум - это чуть меньше 100 долларов.')
        # TODO: make kb for better UX
        await state.set_state(FSMSelectParams.price_from)


@router.message(Command(commands=["cancel"]), ~StateFilter(default_state))
async def cancel_input(message: types.Message, state: FSMContext):
    await message.answer('Вы прервали заполнение параметров.\n Чтобы снова перейти к заполнению параметров, введите /start')
    await state.clear()


@router.message(StateFilter(FSMSelectParams.price_from), F.text.isdigit())
async def process_price_from(message: types.Message, state: FSMContext):
    await state.update_data(price_from=message.text)
    await message.answer('Какую максимальную цену в сумах вы готовы платить в месяц? '
                         'Для справки: 1 000 000 сум - это чуть меньше 100 долларов.')  # TODO: make kb for better UX
    await state.set_state(FSMSelectParams.price_to)

# TODO: add handlers for not_price_from, not_ditrict etc


@router.message(StateFilter(FSMSelectParams.price_to), F.text.isdigit())
async def process_price_to(message: types.Message, state: FSMContext):
    await state.update_data(price_to=message.text)
    await state.update_data(districts=[])
    await message.answer('Выберите, пожалуйста, район. После выбора всех интерсующих вас районов, нажмите "выбрать".',
                         reply_markup=district_menu_inl)
    # TODO: how to pick several districts at once?
    await state.set_state(FSMSelectParams.district)


@router.callback_query(StateFilter(FSMSelectParams.district), F.data != 'finish') #, ~F.text == 'выбрать'
async def gather_district(callback: types.CallbackQuery, state: FSMContext):
    pprint(callback)
    data = await state.get_data()
    districts = data['districts']
    districts.append(callback.data)
    await state.update_data(districts=districts)
    print(await state.get_data())

# TODO: if user presses 'выбрать' right away make a warning: 'Для начала выберите хотя бы один район'


@router.callback_query(StateFilter(FSMSelectParams.district), F.data == 'finish')
async def process_district(callback: types.CallbackQuery, state: FSMContext):
    user_dict[callback.from_user.id] = await state.get_data()
    print(user_dict)
    await callback.message.edit_text('Спасибо ваши данные зарегстрированы.')
    await callback.message.answer('Начать рассылку', reply_markup=yes_no_menu_inl)
    await state.set_state(FSMSelectParams.start_parsing)

# TODO: check parsing func
@router.callback_query(StateFilter(FSMSelectParams.start_parsing), Text(text='yes'))
async def parse_data(callback: types.CallbackQuery, state: FSMContext):
    print('Поехали парсить')
    user_id = callback.from_user.id
    user_query = user_dict[user_id]
    search_districts = user_query.pop('districts')
    search_params = copy.deepcopy(user_query)
    payload = payload_boilerplate | user_query
    search_link = requests.get(url=url, params=payload).url  # TODO: use urllib to avoid making an extra request
    print(search_link)

    while await state.get_state() == 'FSMSelectParams:start_parsing':  # TODO: check if it has to be :start_parsing or .start_parsing
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

# @router.message()
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

# TODO: add show_params
# TODO: add I don't get ya

# def register_handlers(dp: Dispatcher):
#     dp.message.register(command_start, CommandStart(), StateFilter(default_state))
#     dp.message.register(cancel_input, Command(commands=['cancel']))
#     dp.message.register(process_price_from, StateFilter(FSMSelectParams.price_from), F.text.isdigit())
#     dp.message.register(process_price_to, StateFilter(FSMSelectParams.price_to), F.text.isdigit())
#     dp.callback_query.register(process_district, StateFilter(FSMSelectParams.district)) # TODO: add func with callback
#     dp.callback_query.register(parse_data, Text(text=['yes']), StateFilter(FSMSelectParams.start_parsing))
#     dp.callback_query.register(resume_delivery, Text(text=['yes']), StateFilter(FSMSelectParams.resume_delivery))
#     dp.message.register(check_params, Command(commands=['see_my_params']), StateFilter(FSMSelectParams.check_params))
