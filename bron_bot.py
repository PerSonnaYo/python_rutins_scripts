from email.mime import base
import time
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery, Message,\
    InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputFile
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram import Bot

import os
import vk
from sqlalchemy import create_engine
import pandas as pd
from vk_api import exceptions as exp
import asyncio
import datetime
from datetime import date
import traceback
from meshok_interface import MeshokAPI
from static_config import logs_folder_name
from static_config import temp_folder_name, files_folder_name
from vk_photo_interface import Vk_Photo_API
from utils_for_bots import Bot1_API
from config import TELEGRAM_BOT_TOKEN_BRON, TELEGRAM_ADMIN_CHAT_ID, VK_ACCESS_TOKEN_EGOR, VK_VERSION, VK_LIMIT_TRY, VK_ALBUM_ID_FROM,VK_ALBUM_ID_BRON, VK_OWNER_ID, loger_auot, DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_TABLE, meshok_token
# TOKEN = "5519156028:AAGLUl2TzOjrJU94MOzCuFnB0mKzLgZWZ2M"
file_log = f'{logs_folder_name}/telega_vk.log'
logger = loger_auot('telega_vk.log', __name__)

# TOKEN = "5519156028:AAGLUl2TzOjrJU94MOzCuFnB0mKzLgZWZ2M"

vk_api = Vk_Photo_API('БРОНь Бот')  # подключаем вк

meshok = MeshokAPI(meshok_token)#подключаем мешок

conn_pg = create_engine(f'postgresql+psycopg2://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TABLE}')

# создаём форму и указываем поля
bot = Bot(token=TELEGRAM_BOT_TOKEN_BRON)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
class Form(StatesGroup):
    # date = State()
    job = State()
    price = State()
    selfprice = State()
    owner = State()

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await message.reply('ОК')

# @dp.message_handler()
async def send_files(wait_for):
    while True:
        try:
            await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(f"{temp_folder_name}/backup_coins_base.xlsx", 'rb'))
            await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(f"{files_folder_name}/my_coins_project.dump", 'rb'))
            # await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(f"{files_folder_name}/comments_req.txt", 'rb'))
        except:
            print('Error file')
        await asyncio.sleep(wait_for)


@dp.message_handler(content_types=['text'])
async def date_start(message: Message):
    query = """select * 
            from 
                (select id, name, price, photo_id1, photo_id2, photo_url1, photo_url2, selfprice 
                from main_base_coins where status in (5,6,7,8) order by date_sale desc, id desc limit 30
                )ll
            where name ilike %(slo)s
    """
    try:
        base_df = pd.read_sql("""select id, name, price, photo_id1, photo_id2, photo_url1, photo_url2, selfprice from main_base_coins where status in (3, 4) and name ilike %(slo)s order by dates""", con=conn_pg, params={'slo': f'%{message.text}%'})
        base_df1 = pd.read_sql(query, con=conn_pg, params={'slo': f'%{message.text}%'})
    except:
        tb = traceback.format_exc()
        logger.error(f'БРОН бот: поиск монет не сработал(read_sql)\n{tb}')
        await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
        return
    base_df = pd.concat([base_df, base_df1])
    base_df.reset_index(inplace=True)  # make sure indexes pair with number of rows
    if len(base_df) == 0:
        await bot.send_message(message.chat.id, "Ничего не найдено")
    else:
        await bot.send_message(message.chat.id, f"Найдено {len(base_df)} штук")
    for index, row in base_df.iterrows():
        if index == 25:
            break
        b2 = InlineKeyboardButton("Изменить цену",
                                            callback_data="price {} {} {}".format(row['id'], row['photo_id1'], row['photo_id2']))
        b3 = InlineKeyboardButton("Изменить себестоимость",
                                            callback_data="value {} {} {}".format(row['id'], row['photo_id1'], row['photo_id2']))
        b4 = InlineKeyboardButton("Изменить владельца",
                                            callback_data="owner {} {} {}".format(row['id'], row['photo_id1'], row['photo_id2']))
        b5 = InlineKeyboardButton("Удалить",
                                            callback_data="del {} {} {}".format(row['id'], row['photo_id1'], row['photo_id2']))
        b6 = InlineKeyboardButton("Вернуть",
                                            callback_data="ret {} {} {}".format(row['id'], row['photo_id1'], row['photo_id2']))
        kb = InlineKeyboardMarkup(row_width=2).add(b6, b4, b3, b5, b2)  # Создаем клавиатуру
        try:
            await bot.send_media_group(message.chat.id, [InputMediaPhoto(row['photo_url1']),
                                                    InputMediaPhoto(row['photo_url2'])])  # Отсылаем сразу 2 фото
        except:
            await bot.send_message(message.chat.id, "Фоток нет")
        await bot.send_message(message.chat.id, f"{row['id']} ^ {row['name']}\nЦена: {row['price']}\nСебестоимость: {row['selfprice']}",
                                   reply_markup=kb)  # Отсылаем клавиатуру
        # await Form.job.set()

# @dp.message_handler(lambda message: message.text not in ["Забронировать", "Изменить цену", "Изменить себестоимость"])
# async def comman_invalid(message: Message):
#     logger.error(f'invalid command')
#     return await message.reply("Не знаю такой команды. Укажи команду кнопкой на клавиатуре")

@dp.callback_query_handler()
async def process_stack(call: CallbackQuery, state: FSMContext):
    ff = call.data
    sp = ff.split(" ")
    action = sp[0]
    id = sp[1]
    url1 = int(sp[2])
    url2 = int(sp[3])
    # base_df = pd.read_sql("""select owner_id from described where id=1""", con=conn_pg)
    # owner_id = str(base_df.iloc[0][0])
    await Form.job.set()
    async with state.proxy() as data:
        data['job'] = [int(id), url1, url2]#формируем номер группы + номер поста
    # async with state.proxy() as data:
    #     data['job'] = url#формируем номер группы + номер поста
    # global SLIP
    try:
        await bot.edit_message_text(call.message.text, message_id=call.message.message_id,
                                chat_id=call.message.chat.id)
    except:
        x = 0
    if action == "price":
        # Ожидание цены
        # await bot.answer_callback_query(call.id, "Ожидайте...", show_alert=False)
        await bot.send_message(call.message.chat.id, "Пожалуйста, укажите новую цену.")
        await Form.next()
    if action == "value":
        # Ожидание себестоимости
        await bot.send_message(call.message.chat.id, "Пожалуйста, укажите новую себестоимость.")
        await Form.next()
        await Form.next()
    if action == "owner":
        # Ожидание владелец
        await bot.send_message(call.message.chat.id, "Пожалуйста, введите нового владельца.")
        await Form.next()
        await Form.next()
        await Form.next()
    if action == "del":
        # Полное удаление
        await bot.answer_callback_query(call.id, "Удаляю фотографии...", show_alert=True)
        res = vk_api.delete_lot(url1=url1, url2=url2)
        if res == False:
            await state.finish()
            return await bot.send_message(call.message.chat.id, "Ошибка удаления")
        #меняем статус в таблице на бронь
        bot_del_up = Bot1_API('БРОНь Бот', id)
        bot_del_up.delete_lot()
        await bot.send_message(call.message.chat.id, "Фотографии успешно удалены.")
        await state.finish()
    if action == "ret":
        # Вернуть фотки в случае отмены брони
        res = vk_api.replace_photos(url1=url1, url2=url2, tirget='from')
        if res == False:
            await state.finish()
            return await bot.send_message(call.message.chat.id, "Ошибка переноса")
        try:
            name_df2 = pd.read_sql("""select id, meshok_id, metka from main_base_coins where id = %(ids)s""", con=conn_pg, params={'ids': id})
            meshok_id = name_df2.iloc[0][1]
            metka = name_df2.iloc[0][2]
            metka_df = pd.read_sql("""select count(*) as num from main_base_coins where metka = %(met)s and status = 3""", con=conn_pg, params={'met': metka})
            metka_num = metka_df.iloc[0][0]
        except:
            tb = traceback.format_exc()
            logger.error(f'БРОН бот: не удалось перенсти лот мешок(read_sql)______\n{tb}')
            await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
            meshok_id = 0
            metka = ''
            metka_num = 0
        if meshok_id != 0:
            try:
                m_id = meshok.relist_item(meshok_id)
            except:
                tb = traceback.format_exc()
                logger.error(f'БРОН бот: MESHOK не удалось перевыставить лот __ {id}___{meshok_id}\n{tb}')
                m_id = 0
                await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
        query = """update main_base_coins as f
                set status = 2, metka = NULL, meshok_id = """+str(m_id)+"""::integer
                where f.id = """+str(id)+"""::integer"""
        query1 = """DELETE FROM metka  f
                            where f.name = '"""+metka+"""'
                            """
        with conn_pg.begin() as conn:
            try:
                conn.execute(query)
                if metka_num == 1:#если метка всего одна то удаляем
                    conn.execute(query1)
            except:
                tb = traceback.format_exc()
                logger.error(f'БРОН бот: не удалось переместить фото(update and delete)--{id}__{m_id}___{metka}__)\n{tb}')
                await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))

    await state.finish()
    await bot.send_message(call.message.chat.id, "Фотографии успешно перенесены.")

@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.price)
async def stack_invalid(message: Message):
    return await message.reply("Напиши число или напиши /cancel")

@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.selfprice)
async def stack_invalid(message: Message):
    return await message.reply("Напиши число или напиши /cancel")

# @dp.message_handler(lambda message: not message.text.isdigit(), state=Form.stack)
# async def stack_invalid(message: Message):
#     return await message.reply("Напиши число или напиши /cancel")

# Цена
@dp.message_handler(lambda message: message.text.isdigit(), state=Form.price)
async def stack(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = int(message.text)
    ids = data['job'][0]
    url1 = data['job'][1]
    url2 = data['job'][2]
    try:
        name_df = pd.read_sql("""select name, selfprice from main_base_coins where id = %(ids)s""", con=conn_pg, params={'ids': ids})
    except:
        tb = traceback.format_exc()
        logger.error(f'БРОН бот: изменение цены не сработал(read_sql)\n{tb}')
        await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
        await state.finish()
        return
    name1 = name_df.iloc[0][0]
    res = vk_api.rename_price(url1=url1, url2=url2, price=message.text, name=name1)
    if res == False:
        await state.finish()
        return await message.reply("Ошибка замены")
    #меняем цену в таблице
    p = message.text
    bot_del_up = Bot1_API('БРОНь Бот', ids)
    bot_del_up.rename_price(int(p))
    await state.finish()
    await message.reply("Готово")

#Себестоимость
@dp.message_handler(lambda message: message.text.isdigit(), state=Form.selfprice)
async def stack(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['selfprice'] = int(message.text)
    ids = data['job'][0]
    url1 = data['job'][1]
    url2 = data['job'][2]
    p = message.text
    res = vk_api.rename_selfprice(url1=url1, url2=url2, selfprice=p)
    if res == False:
        await state.finish()
        return await message.reply("Ошибка замены")
    #меняем цену в таблице
    query = """update main_base_coins as f
            set selfprice = """+p+"""::integer
            where f.id = """+str(ids)+"""::integer"""
    with conn_pg.begin() as conn:
        try:
            conn.execute(query)
        except:
            tb = traceback.format_exc()
            logger.error(f'БРОН бот: ошибка изменения себестоимости(update)+: {ids}\n{tb}')
            await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
    await state.finish()
    await message.reply("Готово")

@dp.message_handler(content_types=['text'], state=Form.owner)
async def stack(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['owner'] = message.text
    #достаем id
    ids = data['job'][0]
    #меняем владельца в таблице
    p = message.text
    query = """update main_base_coins as f
            set owner = '"""+p+"""'
            where f.id = """+str(ids)+"""::integer"""
    with conn_pg.begin() as conn:
        try:
            conn.execute(query)
        except:
            tb = traceback.format_exc()
            logger.error(f'БРОН бот: ошибка изменения владельца(update)+: {ids}\n{tb}')
            await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
    await state.finish()
    await message.reply("Готово")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_files(86400)) # поставим 10 секунд, в качестве теста
    executor.start_polling(dp, skip_updates=True)