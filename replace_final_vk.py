import vk
from sqlalchemy import create_engine
import pandas as pd
from vk_api import exceptions as exp
import time
from config import VK_ACCESS_TOKEN_EGOR, VK_VERSION, VK_LIMIT_TRY, VK_ALBUM_ID_END, VK_OWNER_ID, loger_auot, print_error
from config import  DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_TABLE
from vk_photo_interface import Vk_Photo_API

file_log = 'telega_vk.log'
logger = loger_auot(file_log, __name__)

try:
    vk_api = Vk_Photo_API('vk_hourly_replace')  # подключаем вк
except:
    print_error(f'vk_hourly_replace:vk autification fail', file_log)
    raise "JO-Jo"
try:
    conn_pg = create_engine(f'postgresql+psycopg2://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TABLE}')
    df = pd.read_sql("""select bbc.id, photo_id1, photo_id2, bbc.status, ddd.method_sale
                            from main_base_coins bbc
                            left join 
                                (select id, method_sale from described) ddd
                                on ddd.id = bbc.method_sale
                            where bbc.status = 4
                            order by bbc.id
                        """, con=conn_pg)
except:
    print_error(f'vk_hourly_replace: read_sql fail', file_log)
    raise "JO-Jo"

h1 = False
h2 = False
if len(df) >= 1:
    for index, row in df.iterrows():
        time.sleep(12)
        place = row['method_sale']
        url1 = row['photo_id1']
        url2 = row['photo_id2']
        ids = str(row['id'])
        res = vk_api.replace_photos(url1=url1, url2=url2, tirget='end')
        if res == False:
            raise "JO-Jo"
        vk_api.rename_selfprice(url1=url1, url2=url2, selfprice=f'Продано на {place}')#добавляем коммент с инфой где продано

        query = """ update main_base_coins as f
                                    set status = 5, photo_url1 = null, photo_url2 = null, photo_url3 = null, photo_url4 = null
                                where f.id = """+ids+"""::integer"""
        with conn_pg.begin() as conn:
            try:
                conn.execute(query)
            except:
                print_error(f'vk_hourly_replace: update fail {ids}', file_log)
                raise "JO-Jo"
