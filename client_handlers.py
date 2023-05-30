import asyncio
import copy
from random import randint

import requests
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, Text, StateFilter
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.state import default_state
from keyboards import yes_no_menu_inl, district_menu_inl, resume_alter_menu_inl, price_menu_inl
from telegram import Telegram
from decouple import config
from loader import db
from module import get_cards, get_offer, format_text, convert_params
from typing import List
from lexicon_ru import LEXICON_RU
from pprint import pprint

url = 'https://www.olx.uz/d/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/'
tg = Telegram(bot_token=config('BOT_TOKEN'), chat_id=config('CHAT_ID'))  # TODO: why 2 bots?
user_dict: dict[int, dict[str | int]] = {}

payload_boilerplate = {
    'currency': 'UZS',
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
router_price_from: Router = Router()
router_price_to: Router = Router()
router_district: Router = Router()

router_price_from.callback_query.filter(StateFilter(FSMSelectParams.price_from))
router_price_from.message.filter(StateFilter(FSMSelectParams.price_from))

router_price_to.callback_query.filter(StateFilter(FSMSelectParams.price_to))
router_price_to.message.filter(StateFilter(FSMSelectParams.price_to))

router_district.callback_query.filter(StateFilter(FSMSelectParams.district))

# @dp.message_handler(commands=['start'], state='*') # old type of decorator
@router.message(CommandStart())  # new type of decorator
async def command_start(message: types.Message, state: FSMContext):
    '''
    Launch the bot. By user_id check if the user is new or not. If new, propose to pick params starting price_to. Switch
    FMS to price_to.
    '''
    user_tg_id = message.from_user.id
    if db.user_is_in_db(user_tg_id):
        search_params = eval(*db.fetch('search_params', user_tg_id))
        ru_params = convert_params(search_params)
        await message.answer(f'Я тебя знаю, приятель! Твой последний запрос: \n\n{ru_params}\n\n Посмотреть параметры '
                             'запроса можно также в меню.',
                             reply_markup=resume_alter_menu_inl)
        await state.set_state(FSMSelectParams.resume_delivery)

    else:
        await message.answer(LEXICON_RU['ask_min_price'],
                             reply_markup=price_menu_inl)
        await state.set_state(FSMSelectParams.price_from)


@router.message(Command(commands=["cancel"]), ~StateFilter(default_state))
async def cancel_input(message: types.Message, state: FSMContext):
    await message.answer(LEXICON_RU['/cancel'])
    await state.clear()


@router_price_from.callback_query(F.data.isdigit())
async def process_menu_price_from(callback: types.CallbackQuery, state: FSMContext):
    min_price = int(callback.data)
    state_data = {'search[filter_float_price:from]': min_price}
    print(state_data)
    await state.update_data(state_data)
    await callback.message.answer(text=f'Вы выбрали {int(min_price/11420)} $\n' + LEXICON_RU['ask_max_price'],
                                  reply_markup=price_menu_inl)
    await state.set_state(FSMSelectParams.price_to)


@router_price_from.message(F.text.isdigit())
async def process_message_price_from(message: types.Message, state: FSMContext):
    min_price = int(message.text)
    state_data = {'search[filter_float_price:from]': min_price * 11420}
    print(state_data)
    await state.update_data(state_data)
    await message.answer(text=f'Вы выбрали {min_price} $\n' + LEXICON_RU['ask_max_price'],
                         reply_markup=price_menu_inl)
    await state.set_state(FSMSelectParams.price_to)
# TODO: add handlers for not_price_from, not_ditrict etc


@router_price_to.callback_query(F.data.isdigit())
async def process_menu_price_to(callback: types.CallbackQuery, state: FSMContext):
    max_price = int(callback.data)
    state_data = {'search[filter_float_price:to]': max_price}
    await state.update_data(state_data)
    await state.update_data(districts=[])
    await callback.message.answer(text=f'Вы выбрали {int(max_price/11420)} $\n' +LEXICON_RU['ask_district'],
                                  reply_markup=district_menu_inl)
    await state.set_state(FSMSelectParams.district)


@router_price_to.message(F.text.isdigit())
async def process_message_price_to(message: types.Message, state: FSMContext):
    max_price = int(message.text)
    state_data = {'search[filter_float_price:to]': max_price * 11420}
    await state.update_data(state_data)
    await state.update_data(districts=[])
    await message.answer(text=f'Вы выбрали {max_price} $\n' + LEXICON_RU['ask_district'],
                         reply_markup=district_menu_inl)
    await state.set_state(FSMSelectParams.district)


@router_district.callback_query(F.data != 'finish')
async def gather_district(callback: types.CallbackQuery, state: FSMContext): # TODO: remove clock icon
    data = await state.get_data()
    districts = data['districts']
    districts.append(callback.data)
    await state.update_data(districts=districts)


# TODO: if user presses 'выбрать' right away make a warning: 'Для начала выберите хотя бы один район'
# TODO: return common router


@router_district.callback_query(F.data == 'finish')
async def process_district(callback: types.CallbackQuery, state: FSMContext):
    user_dict[callback.from_user.id] = await state.get_data()
    print(user_dict)
    await callback.message.edit_text(text=LEXICON_RU['ask_to_start_parsing'],
                                     reply_markup=yes_no_menu_inl)
    await state.set_state(FSMSelectParams.start_parsing)


@router.callback_query(StateFilter(FSMSelectParams.start_parsing), Text(text='yes'))
async def parse_data(callback: types.CallbackQuery, state: FSMContext):
    print('Поехали парсить')
    user_id = callback.from_user.id
    print(callback.message.chat.id)
    user_query = user_dict[user_id]
    search_params = copy.deepcopy(user_query)
    search_districts = [LEXICON_RU[x] for x in user_query.pop('districts')]
    print(search_districts)
    payload = payload_boilerplate | user_query
    search_link = requests.get(url=url, params=payload).url  # TODO: use urllib to avoid making an extra request
    print(search_link)

    while await state.get_state() == 'FSMSelectParams:start_parsing':
        print('парсинг начался')
        cards: List[str] = get_cards(url=search_link)  # TODO: pass search_link from the above to avoid double job
        for card in cards:
            if not db.ad_is_in_db(card):
                offer = get_offer(card, search_districts)
                if offer:
                    offer['user_id'] = user_id
                    offer['search_link'] = search_link
                    offer['параметры_поиска'] = str(search_params)
                    text = format_text(offer)
                    db.send_to_db(offer)
                    await callback.message.answer(text=text)
                    # TODO: add sent or not field, add field with generated link
        await asyncio.sleep(randint(30, 40))

# @router.message()
async def resume_delivery(callback: types.CallbackQuery, state: FSMContext):
    print('Возобновляем рассылку.')
    await callback.message.answer(text=LEXICON_RU['/resume'])
    user_id = callback.message['chat']['id']
    search_link = db.fetch('search_link', user_id)[0]

    while await state.get_state() == 'FSMSelectParams:resume_delivery':
        cards: List[str] = get_cards(url=search_link)
        for card in cards:
            if not db.ad_is_in_db(card):
                search_params = eval(*db.fetch('search_params', user_id))
                search_districts = search_params['districts']
                offer = get_offer(card, search_districts)
                if offer:
                    offer['user_id'] = user_id
                    offer['search_link'] = search_link
                    offer['параметры_поиска'] = str(search_params)  # TODO: translate into Russian
                    text = format_text(offer)
                    db.send_to_db(offer)
                    tg.send_telegram(text)
                    # TODO: add sent or not field, add field with generated link

        await asyncio.sleep(randint(30, 40))


async def check_params(message: types.Message, state: FSMContext):
    await message.answer('Вот ваши параметры!')
    search_params = eval(*db.fetch('search_params', message['from']['id']))
    ru_params = convert_params(search_params)
    await message.answer(ru_params)

# TODO: add show_params
# TODO: add I don't get ya
# TODO: for biggie functions logic should be transfered to the module file



