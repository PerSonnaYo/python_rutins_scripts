# -*- coding: utf-8 -*-
from datetime import datetime
from time import sleep
from requests import exceptions as rex
from ssl import SSLEOFError
from urllib3 import exceptions as uex
# from . import get_auth_parameters, CategoryNotFound, IncorrectLotName, ListingInProgress

from old_config import ok_client_key, ok_client_secret, ok_access_token, ok_client_id, ok_album_id
from config import  DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_TABLE, loger_auot, print_error, upload_limit
from ok_interface import OKApi
from static_config import temp_folder_name
from sqlalchemy import create_engine
import pandas as pd

class OKiItems:
    def __init__(self):
        try:
            self.file_log = 'all_sync.log'
            # self.delist_file = f"{temp_folder_name}/delist_ok.txt"
            self.logger = loger_auot(self.file_log, __name__)
            self.conn_pg = create_engine(f'postgresql+psycopg2://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TABLE}')
            self.passive_items = pd.read_sql("""select id, name, price, photo_url3, photo_url4 from main_base_coins where status = 2 and id not in (select id from ok_table) order by dates""", con=self.conn_pg)
            self.active_items = pd.read_sql("""select mbc.id, ot.ok_photo_id1, ot.ok_photo_id2
                from main_base_coins mbc
                join ok_table ot on ot.id = mbc.id
                where mbc.status = 6 order by dates""", con=self.conn_pg)
            self.killed_items = pd.read_sql("""select mbc.id, ot.ok_photo_id1, ot.ok_photo_id2
                from main_base_coins mbc
                join ok_table ot on ot.id = mbc.id  
                where status_ok = 2 order by dates""", con=self.conn_pg)
            self.change_items = pd.read_sql("""select mbc.id, mbc.name, price, ot.ok_photo_id1, ot.ok_photo_id2
                from main_base_coins mbc
                join ok_table ot on ot.id = mbc.id  
                where status_ok = 3 order by dates""", con=self.conn_pg)
        except:
            print_error(f'Odnoclassniki: read_sql unsucses', self.file_log)
            raise "JO-Jo"
        try:
            self.ok = OKApi(ok_client_id, ok_client_key, ok_client_secret, ok_access_token)
        except:
            print_error(f'Odnoclassniki: ok initial unsucses', self.file_log)
            raise "JO-Jo"

    def list_new_items(self):
        # OK
        self.logger.info('????: ???????????????????? ?????????? ????????...')

        items = {}
        items_to_upload = 0#?????????? ?????? ???????????????? ?? ????????????????????????????
        # 3 ??????. ???????????????? ????????????????????????. 2007??. ????????. ????????????. ??????????????   
        # uploaded_items_ids = []
        for i, item in self.passive_items.iterrows():
            if items_to_upload >= upload_limit:
                break
            face_value,name1,year,condition,country,metal = item['name'].split('. ')
            # item_to_list['item_id'] = item['id']
            name2 = item['name']
            price = item['price']
            item_id = item['id']
            items[item_id] = []
            # print(item['photo_url3'], item['photo_url4'])
            for picture_url in [item['photo_url3'], item['photo_url4']]:
                # print(picture_url)
                item_to_list = {}
                item_to_list['description'] = f"{name2} ???????? {price} ??????. ???? ???????? ???????????????? ?? ??.??."        
                item_to_list['album_id'] = ok_album_id
                item_to_list['url'] = picture_url
                # print(item_to_list)
                # if item_id not in items:
                items[item_id].append(item_to_list)
            # print(items)
                # uploaded_items_ids.append(item_id)
            items_to_upload += 1
        items_to_upload =1
        for item_id, value in items.items():
            try:
                ok_photo_id1 = self.ok.upload_photo(**value[0])
            except:
                print_error(f'Odnoclassniki: load photo error {item_id} __ END \n', self.file_log)
                raise "Jo-jo"
            sleep(10)
            gt = 0
            while True:
                try:
                    ok_photo_id2 = self.ok.upload_photo(**value[1])
                    break
                except:
                    sleep(20)
                    gt += 1
                    if gt == 10:
                        with open(self.delist_file, mode='a') as f:
                            f.write(str(ok_photo_id1))
                        print_error(f'Odnoclassniki: load photo error {item_id} __ {ok_photo_id1} ?????????????? ??????????\n', self.file_log)
                        raise "Jo-jo"
                    continue
            query = """ INSERT INTO public.ok_table(
	                    id, ok_photo_id1, ok_photo_id2)
	                        VALUES ("""+str(item_id)+"""::integer, """+str(ok_photo_id1)+"""::bigint, """+str(ok_photo_id2)+"""::bigint)"""
            with self.conn_pg.begin() as conn:
                try:
                    conn.execute(query)
                except:
                    print_error(f'Odnoclassniki: update ok_id error {item_id} __ {ok_photo_id1} __ {ok_photo_id2}\n', self.file_log)
            self.logger.info(f'????: ?????????????????? ?????????? ???????????????????? {ok_photo_id1} (IID {item_id}).')
            items_to_upload += 1
            # exit()

    def delist_deactivated_items_ids(self):
        # ?????????? ?????? ?????????????? ???????????????????????? ???? ???????????? ???? ????????, 
        # ?????????? ???????? ???????? ???????????????? ?????? ???????????????????? ?? ???????? ???????????????? ??????????????.
        # ?? ?? ???????????????? ???????????? ???? ?????????????? ?????????? ???????????????????????? 
        # (????????????????, ???? ?????????? ?????????????????????? ?????????????????????? ??????????????)
        # ?? ?????????????? ???? ???? ????????????????.
        # ?????????????? - ?????? ????????????????????, ?????? ?????? ???????????????????? ?????????????? ?????????? ????????????????????.
        # ??????????????????????????
        self.logger.info('????: ?????????????? ???????????????????? ???????????? ??????????..')

        for i, row in self.active_items.iterrows():
            item_id = row['id']
            for photo_id in [row['ok_photo_id1'], row['ok_photo_id2']]:
                if photo_id != 0:
                    try:
                        self.ok.remove_photo(photo_id)
                    except:
                        print_error(f'Odnoclassniki. ???? ?????????????? ?????????? {item_id}, {photo_id}', self.file_log)
                        continue
            query = """ update main_base_coins as f
                        set status = 7
                        where f.id = """+str(item_id)+"""::integer"""
            with self.conn_pg.begin() as conn:
                try:
                    conn.execute(query)
                except:
                    print_error(f'Odnoclassniki: update DELIST error {item_id} __ \n', self.file_log)
            self.logger.info(f'????: ???????????????????? (IID {item_id}) ??????????????.')

    def kill_deactivated_items_ids(self):
        # ???????????????? ???????????????? ????????
        self.logger.info('????: ?????????????? ???????????????????? ???????????? ??????????..')
        # print(self.killed_items)
        for i, row in self.killed_items.iterrows():
            item_id = row['id']
            for photo_id in [row['ok_photo_id1'], row['ok_photo_id2']]:
                if photo_id != 0:
                    try:
                        self.ok.remove_photo(photo_id)
                    except:
                        print_error(f'Odnoclassniki. ???? ?????????????? ?????????? {item_id}, {photo_id}', self.file_log)
                        continue
            query = """DELETE FROM ok_table  f
                        where f.id = """+str(item_id)+"""::integer"""
            with self.conn_pg.begin() as conn:
                try:
                    conn.execute(query)
                except:
                    print_error(f'Odnoclassniki: delete ???????????????? error from table{item_id} __ \n', self.file_log)
                    raise "Jo-jo"
            self.logger.info(f'????: ???????????????????? (IID {item_id}) ??????????????.')

    def update_prices(self):
        self.logger.info('????: ?????????????????? ????????...')

        for i, row in self.change_items.iterrows():
            item_id = row['id']
            for photo_id in [row['ok_photo_id1'], row['ok_photo_id2']]:
                try:
                    if photo_id != 0:
                        description = f"{row['name']} ???????? {row['price']} ??????. ???? ???????? ???????????????? ?? ??.??."
                        self.ok.change_photo_description(photo_id, description)
                except:
                    print_error(f'Odnoclassniki. ???? ?????????????? ?????????? {item_id}, {photo_id}', self.file_log)
                    continue
            query = """ update ok_table as f
                        set status_ok = 1
                        where f.id = """+str(item_id)+"""::integer"""
            with self.conn_pg.begin() as conn:
                try:
                    conn.execute(query)
                except:
                    print_error(f'Odnoclassniki: update change status_ok error {item_id} __ \n', self.file_log)
            self.logger.info(f'????: ???????????????????? (IID {item_id}) ????????????????.')

if __name__ == '__main__':
    vk_items = OKiItems()

    vk_items.delist_deactivated_items_ids()
    # vk_items.kill_deactivated_items_ids()
    vk_items.list_new_items()
# vk_items.update_prices()

