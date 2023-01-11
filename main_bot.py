import time
from math import ceil
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery, Message,\
    InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
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
import traceback
import datetime
from datetime import date
from static_config import logs_folder_name, temp_folder_name
from meshok_interface import MeshokAPI
from config import TELEGRAM_BOT_TOKEN_MAIN, TELEGRAM_ADMIN_CHAT_ID, VK_ACCESS_TOKEN_EGOR, VK_VERSION, VK_LIMIT_TRY, VK_ALBUM_ID_FROM,VK_ALBUM_ID_BRON, VK_OWNER_ID, loger_auot, DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_TABLE, meshok_token
from vk_photo_interface import Vk_Photo_API
from utils_for_bots import Bot1_API
# TOKEN = "5519156028:AAGLUl2TzOjrJU94MOzCuFnB0mKzLgZWZ2M"
file_log = f'{logs_folder_name}/telega_vk.log'
logger = loger_auot('telega_vk.log', __name__)

file_config = f'{temp_folder_name}/old_config.conf'#файл для ссылки на прайс
# session = vk.Session(access_token=VK_ACCESS_TOKEN_EGOR)
vk_api = Vk_Photo_API('Основной Бот')  # подключаем вк

meshok = MeshokAPI(meshok_token)#подключаем мешок

conn_pg = create_engine(f'postgresql+psycopg2://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TABLE}')#подтягиваем данные о вк

# создаём форму и указываем поля для порядка команды
bot = Bot(token=TELEGRAM_BOT_TOKEN_MAIN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
class Form(StatesGroup):
    # date = State()
    job = State()
    price = State()
    selfprice = State()
    owner = State()
    stack = State()
    stack_new = State()
    bron = State()

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await message.reply('ОК')

@dp.message_handler(commands=['прайс'])
async def return_url(message: Message):
    with open(file_config, mode='r') as f:
        url = f.readline().split(' = ')[1]
        await message.reply(url)

@dp.message_handler(content_types=['text'])
async def date_start(message: Message):
    try:
        base_df = pd.read_sql("""select id, name, price, photo_id1, photo_id2, photo_url1, photo_url2, selfprice from main_base_coins where status = 2 and name ilike %(slo)s order by dates""", con=conn_pg, params={'slo': f'%{message.text}%'})
    except:
        tb = traceback.format_exc()
        logger.error(f'основной бот: поиск монет не сработал(read_sql)\n{tb}')
        await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
        return
    base_df.reset_index(inplace=True)  # make sure indexes pair with number of rows
    if len(base_df) == 0:
        await bot.send_message(message.chat.id, "Ничего не найдено")
    else:
        await bot.send_message(message.chat.id, f"Найдено {len(base_df)} штук")
    for index, row in base_df.iterrows():
        if index == 25:
            break
        b1 = InlineKeyboardButton("Забронировать",
                                            callback_data="move {} {} {}".format(row['id'], row['photo_id1'], row['photo_id2']))
        b2 = InlineKeyboardButton("Изменить цену",
                                            callback_data="price {} {} {}".format(row['id'], row['photo_id1'], row['photo_id2']))
        b3 = InlineKeyboardButton("Изменить себестоимость",
                                            callback_data="value {} {} {}".format(row['id'], row['photo_id1'], row['photo_id2']))
        b4 = InlineKeyboardButton("Изменить владельца",
                                            callback_data="owner {} {} {}".format(row['id'], row['photo_id1'], row['photo_id2']))
        b5 = InlineKeyboardButton("Удалить",
                                            callback_data="del {} {} {}".format(row['id'], row['photo_id1'], row['photo_id2']))
        b6 = InlineKeyboardButton("Ставка Самара",
                                            callback_data="stac {} {} {}".format(row['id'], row['photo_id1'], row['photo_id2']))
        kb = InlineKeyboardMarkup(row_width=2).add(b1, b4, b3, b5, b2, b6)  # Создаем клавиатуру
        try:
            await bot.send_media_group(message.chat.id, [InputMediaPhoto(row['photo_url1']),
                                                    InputMediaPhoto(row['photo_url2'])])  # Отсылаем сразу 2 фото
        except:
            logger.error('основной бот: не отправилось фото')
            await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
        await bot.send_message(message.chat.id, f"{row['id']} ^ {row['name']}\nЦена: {row['price']}\nСебестоимость: {row['selfprice']}",
                                   reply_markup=kb)  # Отсылаем клавиатуру
        # await Form.job.set()

# @dp.message_handler(lambda message: message.text not in ["Забронировать", "Изменить цену", "Изменить себестоимость", "Изменить владельца", "Удалить", "Ставка Самара"])
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
        logger.error('основной бот: не удалилось меню')
    if action == 'move':
        await bot.send_message(call.message.chat.id, "Пожалуйста, введите метку.")
        await Form.last()
        # await Form.next()
        # await Form.next()
        # await Form.next()
        # await Form.next()
        # await Form.next()
        # await Form.next()
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
    if action == "stac":
        # Ожидание ставка Самара
        try:
            base_df1 = pd.read_sql("""select id from samara_table""", con=conn_pg)
        except:
            tb = traceback.format_exc()
            logger.error(f'основной бот: LAVE поиск монет не сработал(read_sql)\n{tb}')
            await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
            await state.finish()
            return
        lst = base_df1['id'].to_list()
        if int(id) in lst:
            await bot.send_message(call.message.chat.id, "Уже выставлено.")
            await state.finish()
        else:
            await bot.send_message(call.message.chat.id, "Пожалуйста, введите аукционную цену.")
            await Form.next()
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
        bot_del_up = Bot1_API('Основной Бот', id)
        bot_del_up.delete_lot()
        await bot.send_message(call.message.chat.id, "Фотографии успешно удалены.")
        await state.finish()

@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.price)
async def stack_invalid(message: Message):
    return await message.reply("Напиши число или напиши /cancel")

@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.selfprice)
async def stack_invalid(message: Message):
    return await message.reply("Напиши число или напиши /cancel")

@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.stack)
async def stack_invalid(message: Message):
    return await message.reply("Напиши число или напиши /cancel")

# Меняем цену
@dp.message_handler(lambda message: message.text.isdigit(), state=Form.price)
async def stack(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = int(message.text)
    ids = data['job'][0]
    url1 = data['job'][1]
    url2 = data['job'][2]
    try:
        name_df = pd.read_sql("""select name, meshok_id from main_base_coins where id = %(ids)s""", con=conn_pg, params={'ids': ids})
    except:
        tb = traceback.format_exc()
        logger.error(f'основной бот: не удалось поменять цену(read_sql)\n{tb}')
        await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
        await state.finish()
        return
    name1 = name_df.iloc[0][0]
    res = vk_api.rename_price(url1=url1, url2=url2, price=message.text, name=name1)
    if res == False:
        await state.finish()
        return await message.reply("Ошибка замены")
    
    p = int(message.text)
    bot_del_up = Bot1_API('Основной Бот', ids)
    bot_del_up.rename_price(p)
    await state.finish()
    await message.reply("Готово")

#изменение себестоимости
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
    #меняем себестоимость в таблице
    query = """update main_base_coins as f
            set selfprice = """+p+"""::integer
            where f.id = """+str(ids)+"""::integer"""
    with conn_pg.begin() as conn:
        try:
            conn.execute(query)
        except:
            tb = traceback.format_exc()
            logger.error(f'основной бот: не удалось поменять себестоимость(update) __ {ids}\n{tb}')
            await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
    await state.finish()
    await message.reply("Готово")

#менять владельца
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
            logger.error(f'основной бот: не удалось поменять владельца(update) __ {ids}\n{tb}')
            await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
    await state.finish()
    await message.reply("Готово")

#cамара цена
@dp.message_handler(lambda message: message.text.isdigit(), state=Form.stack)
async def stack(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['stack'] = message.text
    ids = data['job'][0]
    url1 = data['job'][1]
    url2 = data['job'][2]
    b1 = InlineKeyboardButton("Идеал", callback_data="ide {} {}".format(str(ids), data['stack']))
    b2 = InlineKeyboardButton("Царапан", callback_data="bad {} {}".format(str(ids), data['stack']))
    kb1 = InlineKeyboardMarkup(row_width=2).add(b1, b2)  # Создаем клавиатуру
    await bot.send_message(message.chat.id, f"Выберете состояние", reply_markup=kb1)  # Отсылаем клавиатуру
    await Form.next()
    # await message.reply("Готово")

#самара состояние
@dp.callback_query_handler(state=Form.stack_new)
async def process_stack(call: CallbackQuery, state: FSMContext):
    ff = call.data
    sp = ff.split(" ")
    action = sp[0]
    ids = int(sp[1])
    stacc = int(sp[2])
    async with state.proxy() as data:
        data['job'] = [ids, stacc]#формируем номер группы + номер поста
    try:
        await bot.edit_message_text(call.message.text, message_id=call.message.message_id,
                                chat_id=call.message.chat.id)
    except:
        logger.error('основной бот: не удалилось меню')
    if action == 'ide': #1 идеал 0 царапан
        df = pd.DataFrame([{'id': ids, 'price': stacc, 'status': 1, 'condition': 1}])
        try:
            df.to_sql('samara_table', if_exists='append', con=conn_pg, index=False)
        except:
            tb = traceback.format_exc()
            logger.error(f'основной бот: не удалось ДОБАВИТЬ в самару(to_sql)\n{tb}')
            await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
    if action == "bad":
        df = pd.DataFrame([{'id': ids, 'price': stacc, 'status': 1, 'condition': 0}])
        try:
            df.to_sql('samara_table', if_exists='append', con=conn_pg, index=False)
        except:
            tb = traceback.format_exc()
            logger.error(f'основной бот: не удалось ДОБАВИТЬ в самару(to_sql)\n{tb}')
            await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
    await bot.send_message(call.message.chat.id, "Добавлено самара")
    await state.finish()

@dp.message_handler(content_types=['text'], state=Form.bron)
async def stack(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['bron'] = message.text
    #достаем id
    ids = data['job'][0]
    url1 = data['job'][1]
    url2 = data['job'][2]
    res = vk_api.replace_photos(url1=url1, url2=url2, tirget='bron')
    if res == False:
        await state.finish()
        return await message.reply("Ошибка переноса")
    #меняем статус в таблице на бронь  и добавляем метку
    df_met = pd.DataFrame([{'name': data['bron']}])
    try:
        df_met.to_sql('metka', if_exists='append', con=conn_pg, index=False)
    except:
        x=0
    query = """update main_base_coins as f
            set status = 3, 
                date_sale = CURRENT_TIMESTAMP, metka = '"""+data['bron']+"""'
            where f.id = """+str(ids)+"""::integer"""
    with conn_pg.begin() as conn:
        try:
            conn.execute(query)
        except:
            tb = traceback.format_exc()
            logger.error(f'основной бот: не удалось не удалолось переместить фото(update)--{ids}__)\n{tb}')
            await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
    try:
        name_df2 = pd.read_sql("""select id, meshok_id from main_base_coins where id = %(ids)s""", con=conn_pg, params={'ids': ids})
        meshok_id = name_df2.iloc[0][1]
    except:
        tb = traceback.format_exc()
        logger.error(f'основной бот: не удалось снять лот мешок(read_sql)\n{tb}')
        await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
        meshok_id = 0

    if meshok_id != 0:
        try:
            meshok.delist_item(meshok_id)
        except:
            tb = traceback.format_exc()
            logger.error(f'основной бот: MESHOK не удалось СНЯТЬ лот __ {ids}___{meshok_id}\n{tb}')
            await bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(file_log, 'rb'))
    await state.finish()
    await message.reply ("Фотографии успешно перенесены.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)