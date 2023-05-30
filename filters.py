from aiogram.filters import BaseFilter
from aiogram import types

class SmallerThan(BaseFilter):
    def __init__(self, min_price: int) -> None:
        self.min_price = min_price

    async def __call__(self, callback: types.CallbackQuery) -> bool:
        return int(callback.data) < self.min_price
