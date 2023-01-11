from pickle import FALSE
from unicodedata import category
import requests
from time import sleep
from math import ceil
import vk
from vk_api import exceptions as exp


from config import VK_ACCESS_TOKEN_EGOR, VK_VERSION, VK_LIMIT_TRY, VK_ALBUM_ID_FROM,VK_ALBUM_ID_BRON, VK_OWNER_ID, VK_ALBUM_ID_END
from config import  DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_TABLE, loger_auot, print_error, meshok_token
from __init__ import  IncorrectLotName, DelistError

from sqlalchemy import create_engine
import pandas as pd
import subprocess
from meshok_interface import MeshokAPI
from vk_market_interface import Vk_Market_API
from static_config import sites_env_name, dags_folder_name, scripts_folder_name


file_log = f'telega_vk.log'
logger = loger_auot(file_log, __name__)

class Bot1_API:
    def __init__(self, name_bot: str, ids: int):
        query1 = """
        select mbc.id, mbc.name, meshok_id, ot.ok_photo_id1, ot.ok_photo_id2, vk_market_id, mbc.status
        from main_base_coins mbc
        left join ok_table ot on ot.id = mbc.id
        left join vk_market_table mvt on mvt.id = mbc.id
        where mbc.id = %(ids)s
        """
        self.name_bot = name_bot
        self.id = ids
        try:
            self.conn_pg = create_engine(f'postgresql+psycopg2://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TABLE}')
            self.lot = pd.read_sql(query1, con=self.conn_pg, params={'ids': self.id})
        except:
            print_error(f'{self.name_bot}: read_sql(price or delete)', file_log)
            raise "JO-Jo"
        try:
            self.meshok = MeshokAPI(meshok_token)#подключаем мешок
        except:
            print_error(f'{self.name_bot}: meshok autenfication error(price or delete)', file_log)
            raise "JO-Jo"
        try:
            self.market = Vk_Market_API()
        except:
            print_error(f'{self.name_bot}: vk Market autenfication error(price or delete)', file_log)
            raise "JO-Jo"

    def delete_lot(self):
        for i, row in self.lot.iterrows():
            query = """DELETE FROM main_base_coins  f
                        where f.id = """+str(self.id)+"""::integer"""
            query1 = """update ok_table as f
                set status_ok = 2
                where f.id = """+str(self.id)+"""::integer"""
            if row['status'] in [2,3,4,5]:
                if row['meshok_id'] != 0:
                    try:
                        self.meshok.delist_item(row['meshok_id'])
                    except:
                        print_error(f'{self.name_bot}: Meshok remove_item error {row["meshok_id"]}', file_log)
                if row['vk_market_id'] is not None:
                    try:
                        self.market.kill_item(self.id, row['vk_market_id'])
                    except DelistError as de:
                        break
                    except:
                        print_error(f'{self.name_bot}: vk Market remove_item error {row["vk_market_id"]}', file_log)
                if row['ok_photo_id1'] is not None and  row['ok_photo_id2'] is not None:
                    try:
                        with self.conn_pg.begin() as conn:
                            conn.execute(query1)
                        subprocess.check_call(f"{sites_env_name} {scripts_folder_name}/ok_bot.py", shell=True)
                    except:
                        print_error(f'{self.name_bot}: OK remove_item error', file_log)
                        break
                with self.conn_pg.begin() as conn:
                    try:
                        conn.execute(query)
                    except:
                        print_error(f'{self.name_bot}: update remove_item in table error {self.id}', file_log)
                        raise "JO-Jo"
            elif row['status'] == 6:
                if row['vk_market_id'] is not None:
                    try:
                        self.market.kill_item(self.id, row['vk_market_id'])
                    except DelistError as de:
                        break
                    except:
                        print_error(f'{self.name_bot}: vk Market remove_item error {row["vk_market_id"]}', file_log)
                if row['ok_photo_id1'] is not None and  row['ok_photo_id2'] is not None:
                    try:
                        with self.conn_pg.begin() as conn:
                            conn.execute(query1)
                        subprocess.check_call(f"{sites_env_name} {scripts_folder_name}/ok_bot.py", shell=True)
                    except:
                        print_error(f'{self.name_bot}: OK remove_item error', file_log)
                        break
                with self.conn_pg.begin() as conn:
                    try:
                        conn.execute(query)
                    except:
                        print_error(f'{self.name_bot}: update remove_item in table error {self.id}', file_log)
                        raise "JO-Jo"
            elif row['status'] == 7:
                if row['vk_market_id'] is not None:
                    try:
                        self.market.kill_item(self.id, row['vk_market_id'])
                    except DelistError as de:
                        break
                    except:
                        print_error(f'{self.name_bot}: vk Market remove_item error {row["vk_market_id"]}', file_log)
                with self.conn_pg.begin() as conn:
                    try:
                        conn.execute(query)
                    except:
                        print_error(f'{self.name_bot}: update remove_item in table error {self.id}', file_log)
                        raise "JO-Jo"
            elif row['status'] == 8:
                with self.conn_pg.begin() as conn:
                    try:
                        conn.execute(query)
                    except:
                        print_error(f'{self.name_bot}: update remove_item in table error {self.id}', file_log)
                        raise "JO-Jo"

    # https://meshok.net/help_api.php#updateItem
    def rename_price(self, price: int):
        for i, row in self.lot.iterrows():
            query = """update main_base_coins as f
                set price = """+str(price)+"""::integer
                where f.id = """+str(self.id)+"""::integer"""
            query1 = """update ok_table as f
                set status_ok = 3
                where f.id = """+str(self.id)+"""::integer"""
            if row['status'] == 2 or row['status'] == 3:
                if row['meshok_id'] != 0:
                    try:
                        self.meshok.update_price(row['meshok_id'], ceil(price/100*1.02)*100)
                    except:
                        print_error(f'{self.name_bot}: Meshok change price error {row["meshok_id"]}', file_log)
                if row['vk_market_id'] is not None:
                    try:
                        self.market.update_price(self.id, row['vk_market_id'], str(price))
                    except:
                        print_error(f'{self.name_bot}: vk Market change price error {row["vk_market_id"]}', file_log)
                with self.conn_pg.begin() as conn:
                    try:
                        conn.execute(query)
                    except:
                        print_error(f'{self.name_bot}: update price in table error {self.id}', file_log)
                        raise "JO-Jo"
                if row['ok_photo_id1'] is not None and  row['ok_photo_id2'] is not None:
                    try:
                        with self.conn_pg.begin() as conn:
                            conn.execute(query1)
                        subprocess.check_call(f"{sites_env_name} {scripts_folder_name}/ok_bot.py", shell=True)
                    except:
                        print_error(f'{self.name_bot}: OK change price error', file_log)
            elif row['status'] in [4,5,6,7,8]:
                with self.conn_pg.begin() as conn:
                    try:
                        conn.execute(query)
                    except:
                        print_error(f'{self.name_bot}: update price in table error {self.id}', file_log)
                        raise "JO-Jo"

