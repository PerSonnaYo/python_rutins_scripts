from pickle import FALSE
from unicodedata import category
import requests
from time import sleep
from math import ceil
import vk
from vk_api import exceptions as exp


from config import VK_ACCESS_TOKEN_EGOR, VK_VERSION, VK_LIMIT_TRY, VK_ALBUM_ID_FROM,VK_ALBUM_ID_BRON, VK_OWNER_ID, VK_ALBUM_ID_END
from config import loger_auot, print_error

from sqlalchemy import create_engine
import pandas as pd

file_log = f'telega_vk.log'
logger = loger_auot(file_log, __name__)

class Vk_Photo_API:
    def __init__(self, name_bot):
        try:
            session = vk.Session(access_token=VK_ACCESS_TOKEN_EGOR)
            self.vk_api = vk.API(session, v=VK_VERSION)  # подключаем вк
            self.name_bot = name_bot
        except:
            print_error(f'{self.name_bot}: vk autification fail', file_log)
            raise "JO-Jo"

    def delete_lot(self, url1, url2):
        for i in range(VK_LIMIT_TRY):
            try:
                self.vk_api.photos.delete(owner_id=VK_OWNER_ID, photo_id=url1)  # удаляем первую фотку
                break
            except exp.Captcha:
                print_error(f'{self.name_bot}: КАПЧА delete foto', file_log)
                return False      
            except:
                if i == VK_LIMIT_TRY - 1:
                    print_error(f'{self.name_bot}: ошибка удаления+ фото: {url1}\n', file_log)
                else:
                    sleep(2)
                    continue
        for i in range(VK_LIMIT_TRY):
            try:
                self.vk_api.photos.delete(owner_id=VK_OWNER_ID, photo_id=url2) # удаляем вторую фотку
                break
            except:
                if i == VK_LIMIT_TRY - 1:
                    print_error(f'{self.name_bot}: ошибка удаления+ фото: {url2}\n', file_log)
                else:
                    sleep(2)
                    continue

    # https://meshok.net/help_api.php#updateItem
    def rename_price(self, url1: str, url2: str, price: str, name: str):
        for i in range(VK_LIMIT_TRY):
            try:
                photos1 = self.vk_api.photos.edit(
                            owner_id=VK_OWNER_ID, 
                            photo_id=url1,
                            caption=f"{name} Цена {price} руб. По всем вопросам в Л.С."
                            )  # Получаем старую цену
                photos2 = self.vk_api.photos.edit(
                            owner_id=VK_OWNER_ID, 
                            photo_id=url2,
                            caption=f"{name} Цена {price} руб. По всем вопросам в Л.С."
                            )  # Получаем старую цену
                break
            except exp.Captcha:
                print_error(f'{self.name_bot}: КАПЧА не удалось поменять цену\n', file_log)
                return False
            except:
                if i == VK_LIMIT_TRY - 1:
                    print_error(f'{self.name_bot}: ошибка замены цены+ фото: {url1}, {url2}\n', file_log)
                    return False
                else:
                    sleep(2)
                    continue

    def rename_selfprice(self, url1: str, url2: str, selfprice: str):
        for i in range(VK_LIMIT_TRY):
            try:
                id_comment_1 = self.vk_api.photos.createComment(
                            owner_id=VK_OWNER_ID,
                            photo_id=url1,
                            message=selfprice
                            )  # Добавляем коммент  
                id_comment_2 = self.vk_api.photos.createComment(
                            owner_id=VK_OWNER_ID,
                            photo_id=url2,
                            message=selfprice
                            )  # Добавляем коммент     
                break  
            except exp.Captcha:
                print_error(f'{self.name_bot}: КАПЧА не удалось поменять себестоимость\n', file_log)
                return False
            except:
                if i == VK_LIMIT_TRY - 1:
                    print_error(f'{self.name_bot}: ошибка замены себестоимости+ фото: {url1}, {url2}\n', file_log)
                    return False
                else:
                    sleep(2)
                    continue

    def replace_photos(self,  url1: str, url2: str, tirget: str = 'bron'):
        if tirget == 'bron':
            al = VK_ALBUM_ID_BRON
        elif tirget == 'from':
            al = VK_ALBUM_ID_FROM
        else:
            al = VK_ALBUM_ID_END
        for i in range(VK_LIMIT_TRY):
            try:
                # logger.error(f'основной бот: 11 {VK_OWNER_ID} {VK_ALBUM_ID_BRON}\n')
                self.vk_api.photos.move(owner_id=VK_OWNER_ID, photo_id=url1, target_album_id=al)  # Перемещение в альбом
                self.vk_api.photos.move(owner_id=VK_OWNER_ID, photo_id=url2, target_album_id=al)      
                break
            except exp.Captcha:
                print_error(f'{self.name_bot}: КАПЧА не удалось переместить фото\n', file_log)
                return False
            except:
                if i == VK_LIMIT_TRY - 1:
                    print_error(f'{self.name_bot}: ошибка переместить фото+ фото: {url1}, {url2}\n', file_log)
                    return False
                else:
                    sleep(2)
                    continue

#     def update_price(self, item_id, price):
#         payload = {}
#         payload['id'] = item_id
#         payload['price'] = price
#         r = self.req('updateItem', payload)

#     def get_item_list(self):
#         r = self.req('getItemList')
#         if meshok_ignore_mode:
#             return []
#         return [r['result'][key] for key in r['result']]


# if __name__ == '__main__':
#     meshok = Vk_Market_API()
#     print(meshok.list_item())
#     exit()

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
