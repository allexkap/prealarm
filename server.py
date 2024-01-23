import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Tuple, Union

from aiogram import Bot, Dispatcher, F, exceptions, types
from aiogram.filters.command import Command

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(filename)s:%(lineno)d %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=(
        logging.FileHandler(Path(__file__).with_suffix('.log'), 'a'),
        logging.StreamHandler(),
    ),
)


WEEK = (
    'Воскресенье',
    'Понедельник',
    'Вторник',
    'Среда',
    'Четверг',
    'Пятница',
    'Суббота',
)


def get_timetable_message():
    data = ('8.00', '6.00', '6.00', '6.00', '6.00', '6.00', '8.00')
    text = 'Текущее расписание\n' + '\n'.join(
        f'{data[i]} - {WEEK[i]}' for i in (1, 2, 3, 4, 5, 6, 0)
    )
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text='Обновить', callback_data='view')],
            [types.InlineKeyboardButton(text='Редактировать', callback_data='edit')],
        ]
    )
    return text, markup


def parse_time(text: str) -> Union[Tuple[int, int], None]:
    return (0, 0)


bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
dp = Dispatcher()
with open('profiles.json') as file:
    profiles = set(json.load(file))
    dp.message.filter(F.from_user.id.in_(profiles))


async def send_timetable(message: types.Message):
    text, markup = get_timetable_message()
    await message.answer(text=text, reply_markup=markup)


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(
        text='Привет',
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await send_timetable(message)


@dp.message(F.text)
async def text_handler(message: types.Message, data={}):
    assert message.from_user

    if message.text == 'Отмена':
        await message.answer(
            text='Лады',
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await send_timetable(message)

    elif message.text in WEEK:
        data[message.from_user.id] = WEEK.index(message.text)
        await message.answer(
            text='Напиши время',
            reply_markup=types.ReplyKeyboardRemove(),
        )

    elif (
        message.from_user.id in data
        and message.text
        and (time := parse_time(message.text))
    ):
        logging.info(
            f'Change alarm time for user={message.from_user.id} '
            f'day={data[message.from_user.id]} time={time}'
        )
        del data[message.from_user.id]
        await message.answer(
            text='Сохранил',
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await send_timetable(message)

    else:
        await message.answer(
            text='Я чет не пон :(', reply_markup=types.ReplyKeyboardRemove()
        )
        await send_timetable(message)


@dp.callback_query(F.data == 'view')
async def callback_view(callback: types.CallbackQuery):
    if not isinstance(callback.message, types.Message):
        logging.warning('callback.message is not instance of types.Message')
        return
    text, markup = get_timetable_message()
    try:
        await callback.message.edit_text(text=text, reply_markup=markup)
    except exceptions.TelegramBadRequest:
        pass  # ignore message is not modified
    await callback.answer()


@dp.callback_query(F.data == 'edit')
async def callback_edit(callback: types.CallbackQuery):
    if not isinstance(callback.message, types.Message):
        logging.warning('callback.message is not instance of types.Message')
        return
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=WEEK[1]), types.KeyboardButton(text=WEEK[4])],
            [types.KeyboardButton(text=WEEK[2]), types.KeyboardButton(text=WEEK[5])],
            [types.KeyboardButton(text=WEEK[3]), types.KeyboardButton(text=WEEK[6])],
            [types.KeyboardButton(text='Отмена'), types.KeyboardButton(text=WEEK[0])],
        ]
    )
    await callback.message.answer(text='Выбери день', reply_markup=markup)
    await callback.message.edit_reply_markup()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
