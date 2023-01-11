# -*- coding: utf-8 -*-
from datetime import datetime
import sys
from time import sleep
from math import ceil

from auction_interface import AuctionAPI

from __init__ import get_auth_parameters, CategoryNotFound, IncorrectLotName, ListingInProgress

from config import auction_email, auction_password, auction_active_lots, loger_auot, print_error, DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_TABLE

from sqlalchemy import create_engine
import pandas as pd
#подключаем логгер из конфига
logger = loger_auot('all_sync.log', __name__)

try:     
    conn_pg = create_engine(f'postgresql+psycopg2://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TABLE}')
    active_items = pd.read_sql("""select id, name, price, photo_url3, photo_url4 from main_base_coins where status = 2 order by dates""", con=conn_pg)
except:
    #отправка ошибки в телеграмм бот
    print_error(f'Аукцион: read_sql sucses', 'all_sync.log')
    raise "JO-Jo"
try:
    auction = AuctionAPI(auction_email, auction_password)
    auction_is_busy = False
except ListingInProgress as e:
    print_error(f'Аукцион: На данный момент уже идёт загрузка лотов на аукцион. {str(e)}', 'all_sync.log')
    raise "JO-Jo"

        # auction
if not auction_is_busy:
    logger.info('Аукцион: Обновляем выставленные лоты...')
    items = []
    # 3 руб. Башкирия Башкортостан. 2007г. Пруф. Россия. Серебро
    for i, item in active_items.iterrows():
        face_value,eee,year,condition,country,metal = item['name'].split('. ')
        item_to_list = {}
        item_to_list['item_id'] = item['id']
        item_to_list['country'] = country
        item_to_list['name'] = item['name']
        item_to_list['year'] = int(year[:-1])
        item_to_list['face_value'] = face_value
        item_to_list['coin_grade'] = condition
        item_to_list['coin_metal'] = metal.replace('.', '')
        #увеличиваем цену на 2%
        item_to_list['price'] = ceil(item['price']/100*1.02)*100

        uid = item['id']
        try:
            virtual_category_id = auction.get_virtual_category_id(country, face_value, year)
        except CategoryNotFound as e:
            print_error(f'Аукцион: Не удалось привязать категорию для IID {uid}.\n {str(e)}', 'all_sync.log')
            continue

        item_to_list['virtual_category_id'] = virtual_category_id
        item_to_list['pictures'] = [item['photo_url3'], item['photo_url4']]


        items.append(item_to_list)
    logger.info('Аукцион: Лоты обновлены...')

    try:
        auction.generate_yml(items[:auction_active_lots], update=True)
    except:
        print_error(f'Аукцион: yaml error', 'all_sync.log')
        raise "JO-Jo"
        # self.auction.yml_switch_sync()

