from unicodedata import category
import requests
from time import sleep
from math import ceil
import vk
import vk_api
from vk_api import exceptions as exp


from config import VK_ACCESS_TOKEN_EGOR, VK_VERSION, VK_LIMIT_TRY, VK_ALBUM_ID_FROM,VK_ALBUM_ID_BRON, VK_MARKET_OWNER_ID, VK_MARKET_CATEGORY_ID, DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_TABLE
from config import loger_auot, print_error
from __init__ import  IncorrectLotName, DelistError
from static_config import temp_folder_name

from sqlalchemy import create_engine
import pandas as pd

file_log = 'all_sync.log'
logger = loger_auot(file_log, __name__)
pic1 = f"{temp_folder_name}/pic11.jpg"
pic2 = f"{temp_folder_name}/pic12.jpg"

class Vk_Market_API:
    def __init__(self):
        try:
            # session = vk.Session(access_token=VK_ACCESS_TOKEN_EGOR)
            # self.vk_api = vk.API(session, v=VK_VERSION)  # подключаем вк
            self.vk_session = vk_api.VkApi(token=VK_ACCESS_TOKEN_EGOR, api_version=VK_VERSION)
        # vk_session.auth(token_only=True)
        # session = vk.Session(access_token=vk_access_token)
        # self.vk_api = vk.API(session, v='5.102')  # подключаем вк
            self.upload = vk_api.VkUpload(self.vk_session)
        except:
            print_error(f'VK_MARKET: vk autification fail', file_log)
            raise "JO-Jo"
        try:     
            self.conn_pg = create_engine(f'postgresql+psycopg2://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TABLE}')
            self.passive_items = pd.read_sql("""
                select mbc.id, name, price, photo_url3, photo_url4 
                from main_base_coins mbc 
                where status = 2 and id not in (select id from vk_market_table)
                order by dates""", con=self.conn_pg)
            self.active_items = pd.read_sql("""
                select mbc.id, vk_market_id
                from main_base_coins mbc 
                join vk_market_table vmt on mbc.id = vmt.id
                where mbc.status = 7
                order by dates""", con=self.conn_pg)
        except:
            #отправка ошибки в телеграмм бот
            print_error(f'VK_MARKET: read_sql unsucses', file_log)
            raise "JO-Jo"

    def get_item(self, item_id):
        r = self.vk_api.market.getById(item_ids='-87564111_5523914')
        return r

    # https://meshok.net/help_api.php#updateItem
    def list_item(self):
        logger.info('VK_MARKET: Выставляем новые лоты...')
        items = []
        # 3 руб. Башкирия Башкортостан. 2007г. Пруф. Россия. Серебро   
        uploaded_items_ids = []
        for i, item in self.passive_items.iterrows():
            sleep(2)
            face_value,name1,year,condition,country,metal = item['name'].split('. ')
            year = int(year[:-1])
            metal = metal.replace('.', '')
            name = f"{face_value} {name1} {year} {country} {metal}"
            item_id = item['id']
            price = str(item['price'])
            main_photo_id = item['photo_url3']
            photo_ids = item['photo_url4']
            description = """В продаже только ОРИГИНАЛЬНЫЕ монеты
Монета находится именно в том состоянии, в котором она на фото. Поэтому возврат по причине «монета не в том состоянии, в котором я рассчитывал» невозможен.
По запросу высылаем дополнительные фотографии и прайс-лист
Личная встреча в районах станций метро Гражданский проспект и Московские ворота
Отправка Почтой России 1-ым классом. Стоимость 250-350 руб в зависимости от веса
Ответственность за работу почты не несу
Отзывы: авито - https://clck.ru/338AV7
https://vk.com/photo255326569_369965356
"""
            headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 YaBrowser/21.8.3.607 Yowser/2.5 Safari/537.36',
            'accept-language': 'ru',
            }
            rt = True
            for i in range(VK_LIMIT_TRY):
                try:
                    r1 = requests.get(main_photo_id, headers=headers)
                    with open(pic1, 'wb') as fd:
                        fd.write(r1.content)
                    sleep(2)
                    r2 = requests.get(photo_ids, headers=headers)
                    with open(pic2, 'wb') as fd:
                        fd.write(r2.content)
                except:
                    if i == VK_LIMIT_TRY - 1:
                        print_error(f'VK_MARKET: load lot requests error {item_id}', file_log)
                        rt = False
                    else:
                        sleep(5)
                        continue
            if rt == False:
                break
            h = False
            for i in range(VK_LIMIT_TRY):
                try:
                    photo = self.upload.photo_market(  # Подставьте свои данные
                                [pic1, pic2],
                                # 'C:/Users/flman/Desktop/eZdxVQU39dk.jpg',
                                group_id = (VK_MARKET_OWNER_ID*-1), main_photo=True#, crop_x=1000, crop_y=1000, crop_width=1000
                            )
                    sleep(2)
                    market_id = self.vk_session.get_api().market.add(owner_id=VK_MARKET_OWNER_ID, name=name,
                                            category_id=VK_MARKET_CATEGORY_ID, price=price,
                                            main_photo_id=photo[0]['id'], photo_ids = str(photo[1]['id']),
                                            description=description)  # удаляем первую фотку
                    h = True
                    break
                except exp.Captcha:
                    print_error(f'VK_MARKET: load lot', file_log)
                    raise "JO-Jo"
                except:
                    if i == VK_LIMIT_TRY - 1:
                        print_error(f'VK_MARKET: load lot {item_id}', file_log)
                        continue
                    else:
                        sleep(2)
                        continue
            if h == True:
                query = """ INSERT INTO public.vk_market_table(
	                    id, main_photo_id, second_photo_id, vk_market_id)
	                        VALUES ("""+str(item_id)+"""::integer, """+str(photo[0]['id'])+"""::bigint, """+str(photo[1]['id'])+"""::bigint, """+str(market_id['market_item_id'])+"""::bigint)"""
                with self.conn_pg.begin() as conn:
                    try:
                        conn.execute(query)
                    except:
                        print_error(f'VK_MARKET: update market_id error {item_id} __ {market_id}\n', file_log)
                logger.info(f'VK_MARKET: Добавлен лот под номером {market_id} (IID {item_id}).')
            # break

    def delist_item(self):
        logger.info('VK_MARKET: Снимаем лоты с торгов...')

        for i, row in self.active_items.iterrows():
            market_id = row['vk_market_id']
            item_id = row['id']
            try:
                if market_id != 0:
                    self.vk_session.get_api().market.delete(owner_id=VK_MARKET_OWNER_ID, item_id=market_id)
            except:
                print_error(f'VK_MARKET. Лот не снят {item_id}, {market_id}', file_log)
                continue
            query = """ update main_base_coins as f
                        set status = 8
                        where f.id = """+str(item_id)+"""::integer"""
            with self.conn_pg.begin() as conn:
                try:
                    conn.execute(query)
                except:
                    print_error(f'VK_MARKET: update DELIST error {item_id} __ {market_id}\n', file_log)
            logger.info(f'VK_MARKET: Лот под номером {market_id} (IID {item_id}) снят с торгов.')

    def kill_item(self, item_id, market_id):
            try:
                if market_id != 0:
                    self.vk_session.get_api().market.delete(owner_id=VK_MARKET_OWNER_ID, item_id=market_id)
            except:
                print_error(f'VK_MARKET. Лот не снят {item_id}, {market_id}', file_log)
                raise "Jo-jo"
            query = """DELETE FROM vk_market_table  f
                        where f.id = """+str(item_id)+"""::integer"""
            with self.conn_pg.begin() as conn:
                try:
                    conn.execute(query)
                except:
                    print_error(f'VK_MARKET: delete Удаление error in table {item_id} __ \n', file_log)
                    raise DelistError('Er-er')

    def relist_item(self, item_id, market_id):
        try:
            if market_id != 0:
                self.vk_session.get_api().market.restore(owner_id=VK_MARKET_OWNER_ID, item_id=market_id)
        except:
            print_error(f'VK_MARKET. Лот не перевыставлен {item_id}, {market_id}', file_log)
            raise "Jo-jo"

    def update_price(self, item_id, market_id, price: str):
        try:
            if market_id != 0:
                self.vk_session.get_api().market.edit(owner_id=VK_MARKET_OWNER_ID, item_id=market_id, price=price)
        except:
            print_error(f'VK_MARKET. Лот не обновлен {item_id}, {market_id}', file_log)
            raise "Jo-jo"

    # def get_item_list(self):
    #     r = self.req('getItemList')
    #     if meshok_ignore_mode:
    #         return []
    #     return [r['result'][key] for key in r['result']]


if __name__ == '__main__':
    meshok = Vk_Market_API()
    meshok.list_item()
    meshok.delist_item()
    # exit()

    # coin = '3 руб'
    # country = 'Россия'
    # year = 1997
    # # print(meshok.get_category_id(country, coin, year))
    # # exit()

    # pictures = ['http://www.coins-spb.ru/images/coins/archive/34952/0/4b0cd1315e36e.jpg', 'http://www.coins-spb.ru/images/coins/archive/34952/0/4b0cd13181a01.jpg']

    # item_dict = {}
    # name = 'a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a '
    # item_dict['name'] = name # REQUIRED
    # item_dict['category_id'] = 14712  # REQUIRED
    # item_dict['price'] = 333 #
    # item_dict['tags'] = '5 руб,Пруф,СССР,Серебро'
    # item_dict['category_params'] = [18, 5]
    # # item_dict['category_params'] = '324,656,22465'
    # # item_dict['common_descriptions'] = '64'
    # item_dict['pictures'] = ','.join(pictures)

    # meshok_id = meshok.list_item(**item_dict)
    # print(meshok_id)

    # item_id = '145674043'
    # meshok.delist_item(item_id)
    # item_id = '145344039'
    # print(meshok.get_item(item_id))

    # item_id = '145344039'
    # meshok.update_price(item_id, 1666)
