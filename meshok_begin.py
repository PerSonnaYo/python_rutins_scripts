# -*- coding: utf-8 -*-
from datetime import datetime
from time import sleep

from __init__ import get_auth_parameters, CategoryNotFound, IncorrectLotName, ListingInProgress

from config import meshok_token, loger_auot, print_error, upload_limit
from config import  DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_TABLE
from meshok_interface import MeshokAPI

from sqlalchemy import create_engine
import pandas as pd
#подключаем логгер из конфига
file_log = 'all_sync.log'
logger = loger_auot(file_log, __name__)

try:     
    conn_pg = create_engine(f'postgresql+psycopg2://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TABLE}')
    passive_items = pd.read_sql("""select id, name, price, photo_url3, photo_url4 from main_base_coins where status = 2 and meshok_id = 0 order by dates""", con=conn_pg)
    active_items = pd.read_sql("""select id, meshok_id from main_base_coins where status = 5   order by dates""", con=conn_pg)
except:
    #отправка ошибки в телеграмм бот
    print_error(f'Мешок: read_sql unsucses', file_log)
    raise "JO-Jo"
try:
    meshok = MeshokAPI(meshok_token)
except:
    print_error(f'Мешок: Error API. ', file_log)
    raise "JO-Jo"
# мешок
def list_new_items():
    logger.info('МЕШОК: Выставляем новые лоты...')
    global passive_items
    items = []
        # 3 руб. Башкирия Башкортостан. 2007г. Пруф. Россия. Серебро   
    uploaded_items_ids = []
    for i, item in passive_items.iterrows():
        face_value,name1,year,condition,country,metal = item['name'].split('. ')
        item_to_list = {}
        metal = metal.replace('.', '')
        # item_to_list['item_id'] = item['id']
        item_to_list['country'] = country
        item_to_list['name'] = name1         
        item_to_list['year'] = int(year[:-1])
        item_to_list['face_value'] = face_value
        item_to_list['coin_grade'] = condition
        item_to_list['coin_metal'] = metal
        item_id = item['id']
        try:
            item_to_list['category_id'] = meshok.get_category_id(country, face_value, year[:-1])
        except CategoryNotFound as e:
            print_error(
                        f'МЕШОК: Не удалось привязать категорию для IID {item_id}. '
                        f'Описание ошибки: {str(e)}.',  file_log)
            continue

        price = meshok.get_meshok_price(item['price'])
        item_to_list['price'] = price
        item_to_list['tags'] = f'{face_value},{condition},{country},{metal}'
        pictures = [item['photo_url3'], item['photo_url4']]
        item_to_list['pictures'] = ','.join(pictures)

        items.append(item_to_list)
        uploaded_items_ids.append(item_id)
        # break

    # listed_meshok_items = []
    for i, item in enumerate(items[:upload_limit]):
        sleep(2)
        item_id = uploaded_items_ids[i]
        try:
            lot_id = meshok.list_item(**item)
        except IncorrectLotName as e:
            print_error(f'МЕШОК. Некорректное название лота IID {item_id}, лот не выставлен. '\
                        f'Сообщение об ошибке: {str(e)}', file_log)
            continue
        except:
            print_error(f'МЕШОК. Error {item_id}', file_log)
            continue
                    
        query = """ update main_base_coins as f
                    set meshok_id = """+str(lot_id)+"""::integer
                    where f.id = """+str(item_id)+"""::integer"""
        with conn_pg.begin() as conn:
            try:
                conn.execute(query)
            except:
                print_error(f'MEshok: update meshok_id error {item_id} __ {lot_id}\n', file_log)
        logger.info(f'МЕШОК: Добавлен лот под номером {lot_id} (IID {item_id}).')
            # self.db.set_listing_multiple([[item_id, lot_id]])

    logger.info('Все лоты на сайтах обновлены...')

def delist_deactivated_items_ids():
        # Итемы для делиста определяются не исходя из того, 
        # какие лоты были отмечены как неактивные в ходе текущего запуска.
        # А в принципе исходя из наличия флага неактивности 
        # (например, во время предыдущего провального запуска)
        # и записей об их листинге.
        # Причина - это безопаснее, так как выполнение скрипта может оборваться.
        # мешок
    logger.info('МЕШОК: Снимаем лоты с торгов...')

    for i, row in active_items.iterrows():
        meshok_id = row['meshok_id']
        item_id = row['id']
        try:
            if meshok_id != 0:
                meshok.delist_item(meshok_id)
        except:
            print_error(f'МЕШОК. Лот не снят {item_id}, {meshok_id}', file_log)
            continue
        query = """ update main_base_coins as f
                    set status = 6
                    where f.id = """+str(item_id)+"""::integer"""
        with conn_pg.begin() as conn:
            try:
                conn.execute(query)
            except:
                print_error(f'MEshok: update DELIST error {item_id} __ {meshok_id}\n', file_log)
        logger.info(f'МЕШОК: Лот под номером {meshok_id} (IID {item_id}) снят с торгов.')

if __name__ == '__main__':
    list_new_items()
    delist_deactivated_items_ids()