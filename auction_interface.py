import requests
from lxml import etree
from datetime import datetime
from io import BytesIO
from time import sleep
import logging
import re
from random import randint

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import json

from gdrive import GoogleDriveAPI
from __init__ import CategoryNotFound, ListingInProgress, save_request
from old_config import google_drive_file_id
from config import yml_filename, auction_default_description
from config import auction_delivery_pochta_city, auction_delivery_pochta_country, auction_delivery_pochta_world,\
    auction_delivery_pochta_commentary, auction_delivery_pickup_commentary,\
    auction_delivery_other_city, auction_delivery_other_country, auction_delivery_other_commentary
from static_config import temp_folder_name, logs_folder_name

yml_path = f'{temp_folder_name}/{yml_filename}'

currencies = {0:['RUR', 1], 1:['USD', 65]}

categories_dict = {}

# категории с распределением по монетам:
# categories_dict['Россия'] = {'Памятные и юбилейные монеты': 78271,
# '1 копейка': 78260,
# '5 копеек': 78261,
# '10 копеек': 78262,
# '50 копеек': 78263,
# '1 рубль': 78264,
# '2 рубля': 78265,
# '3 рубля': 46101042745120,
# '5 рублей': 78266,
# '10 рублей': 78267,
# '20 рублей': 78268,
# '25 рублей': 125643,
# '50 рублей': 78269,
# '100 рублей': 78270,
# 'Разное ': 78272}

# categories_dict['СССР'] = {'Памятные и юбилейные монеты': 75693,
# '1/2 копейки': 48510,
# '1 копейка': 74401,
# '2 копейки': 74402,
# '3 копейки': 74403,
# '5 копеек': 74404,
# '10 копеек': 48511,
# '15 копеек': 74405,
# '20 копеек': 74406,
# '50 копеек': 48512,
# '1 рубль': 74407,
# 'Разное': 48513}

# Австралия и Океания
categories_dict["Австралия"] = 48516
categories_dict["Науру"] = 48516
categories_dict["Вануату"] = 48516
categories_dict["НИУЭ"] = 48516
categories_dict["Новая Зеландия"] = 48516
categories_dict["Острова Австралии"] = 48516
categories_dict["Острова Кука"] = 48516
categories_dict["Палау"] = 48516
categories_dict["Папуа - Новая Гвинея"] = 48516
categories_dict["Самоа"] = 48516
categories_dict["Соломоновы острова"] = 48516
categories_dict["Токелау"] = 48516
categories_dict["Тонга"] = 48516
categories_dict["Тувалу"] = 48516
categories_dict["Фиджи"] = 48516
categories_dict["Французские колонии"] = 48516
categories_dict["Австралия и Океания"] = 48516
categories_dict["Кирибати"] = 48516


# Азия
categories_dict["Афганистан"] = 48491
categories_dict["Бангладеш"] = 48485
categories_dict["Бутан"] = 48485
categories_dict["Вьетнам"] = 48485
categories_dict["Гонконг"] = 48485
categories_dict["Индия"] = 48483
categories_dict["Индонезия"] = 48485
categories_dict["Казахстан"] = 48515
categories_dict["Камбоджа"] = 48491
categories_dict["Китай"] = 48481
categories_dict["Киргизия"] = 48515
categories_dict["Северная Корея"] = 48485
categories_dict["Южная Корея"] = 48485
categories_dict["Кыргызстан"] = 48491
categories_dict["Лаос"] = 48485
categories_dict["Макао"] = 48485
categories_dict["Малайзия"] = 48485
categories_dict["Малайя"] = 48485
categories_dict["Борнео"] = 48485
categories_dict["Мальдивы"] = 48485
categories_dict["Монголия"] = 48485
categories_dict["Непал"] = 48485
categories_dict["Пакистан"] = 48485
categories_dict["Саравак"] = 48485
categories_dict["Сингапур"] = 48485
categories_dict["Стрейтс Сеттлементс"] = 48485
categories_dict["Таджикистан"] = 48515
categories_dict["Таиланд"] = 48485
categories_dict["Тайвань"] = 48485
categories_dict["Туркменистан"] = 48515
categories_dict["Узбекистан"] = 48515
categories_dict["Филиппины"] = 48485
categories_dict["Цейлон"] = 48485
categories_dict["Шри-Ланка"] = 48485
categories_dict["Япония"] = 48485
categories_dict["Юго-восточная Азия"] = 48485
categories_dict["Юго-западная Азия"] = 48487
categories_dict["Разное Азия"] = 48491


# Америка
categories_dict["Антильские острова"] = 48477
categories_dict["Антигуа и Барбуда"] = 48477
categories_dict["Аргентина"] = 48452
categories_dict["Аруба"] = 48477
categories_dict["Багамы"] = 48477
categories_dict["Барбадос"] = 48477
categories_dict["Белиз"] = 48477
categories_dict["Бермуды"] = 48477
categories_dict["Боливия"] = 48477
categories_dict["Бразилия"] = 48450
categories_dict["Венесуэла"] = 48477
categories_dict["Виргинские острова"] = 48477
categories_dict["Гаити"] = 48477
categories_dict["Гайана"] = 48477
categories_dict["Гватемала"] = 48477
categories_dict["Гондурас"] = 48477
categories_dict["Доминиканская республика"] = 48477
categories_dict["Канада"] = 48448
categories_dict["Колумбия"] = 48477
categories_dict["Коста-Рика"] = 48477
categories_dict["Куба"] = 48453
categories_dict["Мексика"] = 48449
categories_dict["Никарагуа"] = 48477
categories_dict["Ньюфаундленд"] = 48477
categories_dict["Панама"] = 48477
categories_dict["Парагвай"] = 48477
categories_dict["Перу"] = 48477
categories_dict["Перу"] = 48455
categories_dict["Сальвадор"] = 48477
categories_dict["Суринам"] = 48477
categories_dict["США"] = 48446
categories_dict["Тринидад и Тобаго"] = 48477
categories_dict["Уругвай"] = 48477
categories_dict["Фолклендские острова"] = 48477
categories_dict["Чили"] = 48456
categories_dict["Эквадор"] = 48458
categories_dict["Ямайка"] = 48477
categories_dict["Острова Карибского бассеина"] = 48477
categories_dict["Каймановы острова"] = 48477
categories_dict["Разное Америка"] = 48477


# Африка
categories_dict["Алжир"] = 48499
categories_dict["Ангола"] = 48499
categories_dict["Бенин"] = 48499
categories_dict["Ботсвана"] = 48499
categories_dict["Бурунди"] = 48496
categories_dict["Габон"] = 48499
categories_dict["Гамбия"] = 48499
categories_dict["Гана"] = 48499
categories_dict["Гвинея"] = 48499
categories_dict["Гвинея-Бисау"] = 48499
categories_dict["Джибути"] = 48496
categories_dict["Египет"] = 48494
categories_dict["Заир"] = 48499
categories_dict["Замбия"] = 48496
categories_dict["Зимбабве"] = 48496
categories_dict["Кабо-Верде"] = 48499
categories_dict["Камерун"] = 48499
categories_dict["Кения"] = 48496
categories_dict["Конго"] = 48495
categories_dict["Кот-д Ивуар"] = 48496
categories_dict["Лесото"] = 48499
categories_dict["Либерия"] = 48499
categories_dict["Ливия"] = 48499
categories_dict["Маврикий"] = 48496
categories_dict["Мавритания"] = 48496
categories_dict["Мадагаскар"] = 48495
categories_dict["Малави"] = 48496
categories_dict["Марокко"] = 48499
categories_dict["Мозамбик"] = 48496
categories_dict["Намибия"] = 48499
categories_dict["Нигерия"] = 48499
categories_dict["Республика Конго"] = 48495
categories_dict["Родезия"] = 48499
categories_dict["Руанда"] = 48496
categories_dict["Сан-Томе"] = 48499
categories_dict["Острова Святой Елены"] = 48499
categories_dict["Принсипи"] = 48499
categories_dict["Сахара"] = 48495
categories_dict["Свазиленд"] = 48499
categories_dict["Сейшелы"] = 48496
categories_dict["Сомали"] = 48496
categories_dict["Сомалиленд"] = 48496
categories_dict["Судан"] = 48496
categories_dict["Сьерра-Леоне"] = 48495
categories_dict["Танзания"] = 48496
categories_dict["Того"] = 48499
categories_dict["Тунис"] = 48499
categories_dict["Уганда"] = 48496
categories_dict["Эритрея"] = 48496
categories_dict["Эфиопия"] = 48496
categories_dict["ЮАР"] = 48498
categories_dict["Чад"] = 48495
categories_dict["Восточная Африка"] = 48496
categories_dict["Острова Африки"] = 48499
categories_dict["Центральная Африка"] = 48495
categories_dict["Южная Африка"] = 48497
categories_dict["Разное в странах Африки"] = 48499

# Ближний Восток
categories_dict["Бахрейн"] = 48489
categories_dict["Израиль"] = 48489
categories_dict["Иордания"] = 48489
categories_dict["Ирак"] = 48489
categories_dict["Иран"] = 48489
categories_dict["Йемен"] = 48489
categories_dict["Катар"] = 48489
categories_dict["Кувейт"] = 48489
categories_dict["Ливан"] = 48489
categories_dict["ОАЭ"] = 48489
categories_dict["Оман"] = 48489
categories_dict["Палестина"] = 48489
categories_dict["Саудовская Аравия"] = 48489
categories_dict["Сирия"] = 48489
categories_dict["Турция"] = 48489
categories_dict["Разное Ближний Восток"] = 48489


# Европа
categories_dict["Абхазия"] = 48515
categories_dict["Австрия"] = 48425
categories_dict["Азербайджан"] = 48515
categories_dict["Азоры"] = 48422
categories_dict["Албания"] = 52883
categories_dict["Андорра"] = 48422
categories_dict["Армения"] = 48515
categories_dict["Беларусь"] = 48515
categories_dict["Бельгия"] = 73775
categories_dict["Богемия и Моравия"] = 48422
categories_dict["Болгария"] = 52882
categories_dict["Босния и Герцеговина"] = 48422
categories_dict["Ватикан"] = 48411
categories_dict["Великобритания"] = 48442
categories_dict["Венгрия"] = 52880
categories_dict["Германия"] = 48430
categories_dict["Гернси"] = 48421
categories_dict["Гибралтар"] = 48422
categories_dict["Гренландия"] = 73769
categories_dict["Греция"] = 73761
categories_dict["Грузия"] = 48515
categories_dict["Дания"] = 73770
categories_dict["Данциг"] = 48422
categories_dict["Джерси"] = 48421
categories_dict["Ирландия"] = 48422
categories_dict["Исландия"] = 73771
categories_dict["Испания"] = 48415
categories_dict["Италия"] = 48411
categories_dict["Кипр"] = 48422
categories_dict["Крит"] = 48422
categories_dict["Латвия"] = 48515
categories_dict["Литва"] = 48515
categories_dict["Лихтенштейн"] = 48422
categories_dict["Люксембург"] = 73776
categories_dict["Македония"] = 73764
categories_dict["Мальта"] = 48422
categories_dict["Молдова"] = 48422
categories_dict["Монако"] = 48422
categories_dict["Нагорный Карабах"] = 48515
categories_dict["Нидерланды"] = 73777
categories_dict["Норвегия"] = 73772
categories_dict["Нотгельды"] = 48422
categories_dict["Остров Мэн"] = 48421
categories_dict["Олдерни"] = 48444
categories_dict["Польша"] = 52878
categories_dict["Португалия"] = 73760
categories_dict["Приднестровье"] = 48515
categories_dict["Румыния"] = 52881
categories_dict["Сан-Марино"] = 48422
categories_dict["Сербия"] = 73763
categories_dict["Скандинавия"] = 73767
categories_dict["Словакия"] = 52879
categories_dict["Словения"] = 52877
categories_dict["Украина"] = 48515
categories_dict["Фарерские острова"] = 48422
categories_dict["Фареры"] = 48422
categories_dict["Финляндия"] = 73773
categories_dict["Франция"] = 48409
categories_dict["Хорватия"] = 73765
categories_dict["Черногория"] = 73766
categories_dict["Чехия"] = 52879
categories_dict["Чехословакия"] = 48422
categories_dict["Швейцария"] = 73762
categories_dict["Швеция"] = 73774
categories_dict["Элдерни"] = 48422
categories_dict["Эстония"] = 48515
categories_dict["Югославия"] = 48422

categories_dict["Восточная Европа"] = 52877

categories_dict["Разное в странах Европы"] = 48422
categories_dict["Разное в странах Скандинавии"] = 73767
categories_dict["Разное в странах Бенилюкса"] = 73768
categories_dict["Разное Восточная Европа"] = 52877

categories_dict['Россия'] = 78271
categories_dict['СССР'] = 75693

categories_dict['жетоны'] = {
    'СССР': 100577,
    'Россия': 100578,
    'Германия': 100581,
    "Южная Корея": 100584
}


# NOTE. Описание структуры словарей.
# Актуальный вопрос - есть ли нужда в виртуальных категориях?
# name - уникальное название категории
# cid - реальный category_id на auction.ru
# virtual_category_id - это виртуальный category_id, не равен cid
# virtual_categories_dict = {
#     virtual_category_id: {
#         'name': name,
#         'cid': cid
#     }
# }
#
# name - уникальное название категории
# virtual_categories_dict_by_name = {
#     name: 'virtual_category_id'
# }
#
# multilevel_category_name - название многоуровневой категории. Например, "жетоны"
# category_name - неуникальное название категории. Ей соответствует своё уникальное название.
# Например, может быть уникальная категория "Россия" - для всех монет из России,
# а параллельно её существовать неуникальная категория жетонов "Россия", которой соответствует
# уникальное название - "жетоны (Россия)"
# virtual_multilevel_categories_by_name = {
#     multilevel_category_name: {
#         category_name: virtual_category_id
#     }
# }

virtual_categories_dict = {}
virtual_categories_dict_by_name = {}
virtual_multilevel_categories_by_name = {}


metal_dict = {
    'Алюминиевая Бронза': 'ал.бронза',
    'Алюминий': 'алюминий',
    'Биметалл': 'биметалл',
    'Бронза': 'бронза',
    'Железо': 'железо',
    'Золото': 'золото',
    'Латунь': 'латунь',
    'Медь': 'медь',
    'Медно-никель': 'медно-ник.',
    'Мельхиор': 'мельхиор',
    'Никелевая бронза': 'никелевая бронза',
    'Плакированная сталь': 'плакированная сталь',
    'Платина': 'платина',
    'Серебро': 'серебро',
    'Цинк': 'цинк'
}

i = 10001
for key in sorted(categories_dict):
    category_element = categories_dict[key]

    if not isinstance(category_element, dict):
        virtual_categories_dict[i] = {'name': key, 'cid': category_element}
        virtual_categories_dict_by_name[key] = i
        i += 1
    else:
        multilevel_category = {}
        for second_key in category_element:
            category_name = f'{key} ({second_key})'
            virtual_categories_dict[i] = {
                'name': category_name,
                'cid': category_element[second_key]}
            virtual_categories_dict_by_name[category_name] = i
            multilevel_category[second_key] = i

            i += 1

        virtual_multilevel_categories_by_name[key] = multilevel_category


def get_metal_name(coin_metal):
    coin_metal = coin_metal.lower()
    valid_metal = [metal for metal in metal_dict if coin_metal == metal.lower()]
    if valid_metal:
        return metal_dict[valid_metal[0]]
    return ''

global logger
logger = logging.getLogger('auction_interface')
logger.setLevel(logging.DEBUG)
logger.propagate = False

log_fh = logging.FileHandler(
        f'{logs_folder_name}/all_sync.log', 
        encoding='utf-8')
log_fh.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_fh.setFormatter(formatter)
logger.addHandler(log_fh)

class AuctionAPI:
    def __init__(self, login, password, google_drive_file_id=google_drive_file_id):
        self.gdrive = GoogleDriveAPI()
        self.google_drive_file_id = google_drive_file_id
        self.s = requests.Session()
        self.s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 YaBrowser/19.9.3.314 Yowser/2.5 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        })

        # self.login(login, password)

    def get_virtual_category_id(self, country, coin_name, coin_year):
        """Функция возвращает виртуальную категорию, а не реальную категорию на auction.ru."""
        country, coin_name = country.lower(), coin_name.lower()
        # coin_year = int(coin_year.split('-')[0]) if not isinstance(coin_year, int) else coin_year
        try:
            if 'жетон' in coin_name:
                country = [
                    country_name for country_name in virtual_multilevel_categories_by_name['жетоны']
                    if country_name.lower() == country][0]
                return virtual_multilevel_categories_by_name['жетоны'][country]

            country = [
                country_name for country_name in virtual_categories_dict_by_name
                if country_name.lower() == country][0]
            return virtual_categories_dict_by_name[country]
        except IndexError:
            raise CategoryNotFound(f'Ошибка! Не удалось подобрать категорию на аукционе для "{coin_name} {country} {coin_year}".')

    def yml_sync_file(self, use_sync_id = True):
        payload = {}
        url = f'https://docs.google.com/uc?export=download&id={self.google_drive_file_id}'
        payload['path2yml'] = url
        payload['sync_assignment_id'] = self.sync_id if use_sync_id else ''
        r = self.s.post('https://auction.ru/syncassignmentajax/sync_assignment_download_yml', 
            data = payload)
        logger.info(f'Аукцион. Загрузка YML файла. JSON: {r.json()}')

    def yml_manual_associate_categories(self, toggle_off = False):
        payload = {}
        payload['sync_assignment_id'] = self.sync_id

        if toggle_off:
            payload['flag'] = True
            r = self.s.post(
                'https://auction.ru/syncassignmentajax/toggle_need_check_required_category_links', 
                data=payload)
            logger.info(f'Аукцион. Пропуск проверки привязки категорий. JSON: {r.json()}')
            return

        # headers = {
        #   "Accept" : "application/json, text/javascript, */*; q=0.01",
        #   "DNT" : "1",
        #   "X-Requested-With" : "XMLHttpRequest",
        #   "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 YaBrowser/19.9.3.314 Yowser/2.5 Safari/537.36",
        #   "Sec-Fetch-Mode" : "cors",
        #   "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
        #   "Origin" : "https://auction.ru",
        #   "Sec-Fetch-Site" : "same-origin",
        #   "Referer" : "https://auction.ru/cabinet/feed_sync_assignment_task/links_between_categories/143221272708608",
        #   "Accept-Encoding" : "gzip, deflate, br",
        #   "Accept-Language" : "ru,en;q=0.9",
        #   "Cookie" : "hascn_lt=1570972810; scn_ftw=SX3m5zWFdKCsT; _ga=GA1.2.1325183943.1570972818; _ym_uid=1570972818221388894; _ym_d=1570972818; hascn=sZH; _gid=GA1.2.230169911.1571335831; Irj62h9eB=oN8Cx1pZbPY5JgniFI5DCmAPAub; _ym_isad=1; formvalidationcookie=daa851555b5ad1c5cbe944a597e69eb4; _gaclientid=1325183943.1570972818; _gasessionid=20191019|01460220; _ym_visorc_31879331=w; sessionid=i07kkimjnnkkg8qcg9d9otp67f4ogmp7; _gahitid=09:26:29; _dc_gtm_UA-66145044-1=1"
        # }

        r = self.s.post('https://auction.ru/syncassignmentajax/clearing_associate_categories', data=payload)
        logger.info(f'Аукцион. Обнуление привязки категорий. JSON: {r.json()}')

        for virtual_category_id in virtual_categories_dict:
            payload['internal_category_id'] = virtual_categories_dict[virtual_category_id]['cid']
            payload['external_category_id'] = virtual_category_id
            r = self.s.post('https://auction.ru/syncassignmentajax/associate_category', data=payload)
            # print(payload)
            # print(f'Аукцион. Регистрация category id {virtual_category_id}. JSON: {r.json()}')

    def yml_manual_associate_params(self):
        payload = {}
        payload['sync_assignment_id'] = self.sync_id

        r = self.s.post('https://auction.ru/syncassignmentajax/clearing_associate_parameters', data=payload)
        logger.info(f'Аукцион. Обнуление привязки параметров. JSON: {r.json()}')

        payload['internal_parameter_ids[]'] = 2090
        payload['external_parameter_id'] = "coin_metal"
        r = self.s.post('https://auction.ru/syncassignmentajax/associate_parameter', data=payload)
        logger.info(f'Аукцион. Регистрация параметра coin_metal. JSON: {r.json()}')

    def yml_set_settings(self):
        payload = {}
        payload['sync_assignment_id'] = self.sync_id
        par = {
            "params[11019400744350115]":"1",
            "params[10]":"156",            
            "params[12]":"1",
            "params[11]":"Санкт-Петербург",
            "params[11019400751336539]":"[{\"id\":\"0\",\"data\":true}]",
            "params[11019400749971521]":"[{\"id\":\"0\",\"data\":true}]",
            "params[11019400748881414]": f"""[{{\"id\":\"1\",\"data\":{{\"city\":\"{auction_delivery_pochta_city}\",\"country\":\"{auction_delivery_pochta_country}\",\"world\":\"{auction_delivery_pochta_world}\",\"comment\":\"{auction_delivery_pochta_commentary}\"}}}},
            {{\"id\":\"4\",\"data\":{{\"comment\":\"{auction_delivery_pickup_commentary}\"}}}},
            {{\"id\":\"0\",\"data\":{{\"city\":\"{auction_delivery_other_city}\",\"country\":\"{auction_delivery_other_country}\",\"comment\":\"{auction_delivery_other_commentary}\"}}}}]"""
        }
        payload['parameters'] = json.dumps(par)
        r = self.s.post('https://auction.ru/syncassignmentajax/set_settings', data=payload)
        logger.info(f'Аукцион. Сохранение настроек синхронизации. JSON: {r.json()}')


    def yml_switch_sync(self, on = True):
        self.yml_manual_associate_categories()
        sleep(5)
        self.yml_set_settings()
        sleep(5)
        headers = {"Accept" : "application/json, text/javascript, */*; q=0.01",
            "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
            "DNT" : "1",
            "Referer" : f"https://auction.ru/cabinet/feed_sync_assignment_task/sync_assignment_parameters/{self.sync_id}",
            "Sec-Fetch-Mode" : "cors",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 YaBrowser/19.9.3.314 Yowser/2.5 Safari/537.36",
            "X-Requested-With" : "XMLHttpRequest"
            }
        payload = {}
        payload['sync_assignment_id'] = self.sync_id
        if on:
            payload['is_active'] = True

        r = self.s.get(f'https://auction.ru/cabinet/feed_sync_assignment_task/sync_assignment_parameters/{self.sync_id}')
        dom = etree.HTML(r.text)
        
        # оставляем текущую опцию с описанием
        selected_description = dom.xpath('//select[@id="standart_description_ids"]/option[@selected="selected"]/@value')
        description_options = dom.xpath('//select[@id="standart_description_ids"]/option/@value')
        if selected_description:
            payload['standart_description_ids[]'] = selected_description[0]
        elif len(description_options) > 1:
            payload['standart_description_ids[]'] = description_options[1]

        # обрезаем название лотов до 100 символов
        payload['is_need_trim_long_titles'] = True

        r = self.s.post('https://auction.ru/syncassignmentajax/create_sync_assignment', data=payload, headers=headers)
        if r.json()['status'] == 'ERROR':
            raise Exception(
                'Аукцион: Ошибка! Не удалось изменить статус синхронизации. '
                f'Причина: {r.json["message"]}')

        logger.info(f'Аукцион. Статус синхронизации изменён на {on}. JSON: {r.json()}')
        r = self.s.get(f'https://auction.ru/cabinet/listing/sync_assignment?flt_prp_owner={self.user_id}')

    def login(self, login, password):
        payload = {}
        payload['email_or_login'] = login
        payload['password'] = password
        r = self.s.get('https://auction.ru/auth')
        dom = etree.HTML(r.text)    
        csrf = dom.xpath('//input[@name="csrf"]/@value')[0]
        payload['csrf'] = csrf
        payload['wsd'] = '1920|1080|24|ru-RU|3'

        r = self.s.post('https://auction.ru/auth', data = payload)
        logger.info(f'Аукцион: Вы успешно вошли как {login}.')

        dom = etree.HTML(r.text)
        save_request(r, 'login_failure.html', temp_folder_name)
        try:
            cabinet_url = dom.xpath('//a[span[text()="Мои лоты"]]/@href')[0]
            user_id = re.findall(r'flt_prp_owner=(\d+)', cabinet_url)[0]
        except IndexError:
            raise Exception(
                'Аукцион. Ошибка! Не удалось залогиниться на сайт (IndexError at user_id search). '
                'Попробуйте зайти на сайт через браузер, чтобы удостовериться, что есть подключение к сайту.')
        self.user_id = user_id

        r = self.s.get(f'https://auction.ru/cabinet/listing/sync_assignment?flt_prp_owner={self.user_id}')
        dom = etree.HTML(r.text)
        sync_id_parse = dom.xpath('//a[@title="Изменить синхронизацию"]/@href')
        
        if not sync_id_parse:
            in_progess_indicators = dom.xpath('//td[normalize-space(text())="В процессе"]')
            if in_progess_indicators:
                raise ListingInProgress('На данный момент уже идёт загрузка лотов на аукцион! Выставление новых лотов приостановлено, чтобы исключить задвоения.')

            save_request(r, f'auction_sync_page_new_sync.html', temp_folder_name)
            # можно отключить, если есть уверенность, что проверка на наличие синхронизации надёжна
            # т.к. код ниже создаст новую синхронизацию, если не найдёт старую, а это может задвоить лоты
            raise ListingInProgress('На данный момент уже идёт загрузка лотов на аукцион! Выставление новых лотов приостановлено, чтобы исключить задвоения.')            

            self.generate_yml(update=True)
            self.yml_sync_file(use_sync_id = False)
            sleep(5)
            r = self.s.get(f'https://auction.ru/cabinet/listing/sync_assignment?flt_prp_owner={self.user_id}')
            dom = etree.HTML(r.text)
            sync_id_parse = dom.xpath('//a[@title="Изменить синхронизацию"]/@href')
            self.sync_id = sync_id_parse[0].split('/')[-1]
            self.yml_manual_associate_categories()
            sleep(5)
            self.yml_manual_associate_params()
            sleep(5)
            self.yml_set_settings()
            sleep(5)
        else:
            self.sync_id = sync_id_parse[0].split('/')[-1]
        
        logger.info(f'Аукцион: Ваш sync_id = {self.sync_id}.')

    # DEPRECATED
    # def list_item(self, base_item = None):
    #   # https://auction.ru/new_offer
    #   s.post('https://auction.ru/new_offer')

    #   if base_item is not None:
    #       # https://auction.ru/offer/copy_offer/142774648478630
    #       pass

    #   lot_url = 'http://auction.ru/offer/moneta-i142774648478630.html'
    #   print(f'Лот успешно выставлен. Ссылка на лот: {lot_url}')

    def generate_yml(self, items = None, update=False):
        if items is None:
            item = {}
            item['item_id'] = 1
            item['name'] = 'test'
            item['price'] = 1000
            item['virtual_category_id'] = virtual_categories_dict_by_name['Франция']
            items = [item]

        yml = YMLGenerator()
        for item in items:
            yml.add_item(**item)

        yml.export_yml(yml_path)

        if update:
            self.update_yml()

    def update_yml(self):
        self.gdrive.update(self.google_drive_file_id, yml_path)


# https://auction.ru/category_tree
# список категорий

class YMLGenerator:
    def __init__(self):
        self.root = etree.Element('yml_catalog', date=datetime.now().strftime('%Y-%m-%d %H:%M'))
        self.shop = etree.SubElement(self.root, 'shop')
        self.currencies = etree.SubElement(self.shop, 'currencies')
        for currency in currencies.values():
            etree.SubElement(self.currencies, 'currency', id=currency[0], rate=str(currency[1])) 

        self.categories = etree.SubElement(self.shop, 'categories')
        for virtual_category_id in virtual_categories_dict:
            etree.SubElement(self.categories, 'category', id = str(virtual_category_id)).text = virtual_categories_dict[virtual_category_id]['name']

        self.offers = etree.SubElement(self.shop, 'offers')

    def add_item(self, item_id, name, price, 
        virtual_category_id, pictures=None, currency_id = 'RUR', coin_metal = '', 
        country = '', face_value='', year='', coin_grade=''):
        if pictures is None:
            pictures = []

        item = etree.SubElement(self.offers, 'offer', id = str(item_id))\

        if (len(name) > 100):
            logger.info(f'Аукцион. У лота IID {item_id} наименование превышает 100 символов. Наименование: {name}.')

        if country.lower() == 'россия':
            lot_name = f'{face_value} {name} {year} {coin_metal}'
        elif country.lower() == 'ссср':
            lot_name = f'{face_value} {name} {year} {country} {coin_grade} {coin_metal}'
        else:
            lot_name = f'{face_value} {name} {year} {country} {coin_metal}'

        etree.SubElement(item, 'name').text = lot_name
        etree.SubElement(item, 'price').text = str(price)
        etree.SubElement(item, 'currencyId').text = currency_id     
        etree.SubElement(item, 'categoryId').text = str(virtual_category_id)                
        etree.SubElement(item, 'category').text = virtual_categories_dict[virtual_category_id]['name']  
        etree.SubElement(item, 'externalCategoryId').text = str(virtual_categories_dict[virtual_category_id]['cid'])
        etree.SubElement(item, 'description').text = auction_default_description

        auction_coin_metal = get_metal_name(coin_metal) if coin_metal else ''
        if not auction_coin_metal:
            logger.error(f'Аукцион. Не задан металл для IID {item_id}. Металл: "{coin_metal}".')

        etree.SubElement(item, 'param', name = "coin_metal").text = auction_coin_metal

        for picture in pictures:
            etree.SubElement(item, 'picture').text = picture

    def export_yml(self, filename):
        s = etree.tostring(self.root, pretty_print=True, xml_declaration=True, encoding='utf-8')
        with open(filename, 'wb') as fo:
            fo.write(s)


if __name__ == '__main__':
    item = {}
    item['item_id'] = 5
    item['name'] = 'Testing95'
    item['price'] = 1020
    item['pictures'] = ['https://www.numizmatik.ru/shopcoins/images/1253/1253001b.jpg']
    item['category_id'] = 78266

    # yml = YMLGenerator()
    # yml.add_item(**item)
    # yml.export_yml()

    from util.config import auction_email, auction_password

    auction = AuctionAPI(auction_email, auction_password)
    # auction.update_yml()
    # upload = True
    # if upload:
    #   auction.update_yml()
    auction.yml_switch_sync()
