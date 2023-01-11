import requests
from time import sleep
from math import ceil

from config import meshok_default_description, meshok_token, meshok_balance_limit, meshok_price_index
from config import meshok_local_delivery_price, meshok_country_delivery_price, meshok_world_delivery_price, meshok_delivery_text, loger_auot, print_error
from __init__ import CategoryNotFound, IncorrectLotName
from static_config import meshok_ignore_mode

file_log = 'all_sync.log'
logger = loger_auot(file_log, __name__)

categories_dict = {}

# Австралия и океания
categories_dict["Австралия"] = 12935
categories_dict["Науру"] = 12934
categories_dict["Вануату"] = 12938
categories_dict["НИУЭ"] = 13384
categories_dict["Новая Зеландия"] = 12936
categories_dict["Острова Австралии"] = 12940
categories_dict["Острова Кука"] = 14817
categories_dict["Палау"] = 14926
categories_dict["Папуа - Новая Гвинея"] = 12941
categories_dict["Самоа"] = 12937
categories_dict["Соломоновы острова"] = 13382
categories_dict["Токелау"] = 14818
categories_dict["Тонга"] = 12939
categories_dict["Тувалу"] = 14293
categories_dict["Фиджи"] = 14680
categories_dict["Французские колонии"] = 12942
categories_dict["Разное Австралия и Океания"] = 12934
categories_dict["Кирибати"] = 16165

# Азия
categories_dict["Афганистан"] = 12943
categories_dict["Бангладеш"] = 13390
categories_dict["Бутан"] = 15403
categories_dict["Вьетнам"] = 12969
categories_dict["Гонконг"] = 12956
categories_dict["Индия"] = 2159
categories_dict["Индонезия"] = 12968
categories_dict["Казахстан"] = 12960
categories_dict["Камбоджа"] = 12958
categories_dict["Китай"] = 2158
categories_dict["Северная Корея"] = 12955
categories_dict["Южная Корея"] = 12954
categories_dict["Кыргызстан"] = 15371
categories_dict["Лаос"] = 12959
categories_dict["Макао"] = 16025
categories_dict["Малайзия"] = 12964
categories_dict["Малайя"] = 16146
categories_dict["Борнео"] = 16146
categories_dict["Мальдивы"] = 12963
categories_dict["Монголия"] = 12962
categories_dict["Непал"] = 12965
categories_dict["Пакистан"] = 12948
categories_dict["Саравак"] = 15188
categories_dict["Сингапур"] = 12966
categories_dict["Стрейтс Сеттлементс"] = 15189
categories_dict["Таджикистан"] = 15370
categories_dict["Таиланд"] = 12957
categories_dict["Тайвань"] = 16026
categories_dict["Туркменистан"] = 15372
categories_dict["Узбекистан"] = 15375
categories_dict["Филиппины"] = 12961
categories_dict["Цейлон"] = 12970
categories_dict["Шри-Ланка"] = 12967
categories_dict["Япония"] = 2875
categories_dict["Юго-восточная Азия"] = 2161
categories_dict["Юго-западная Азия"] = 2162
categories_dict["Разное Азия"] = 2157

# Америка
categories_dict["Антильские острова"] = 13383
categories_dict["Антигуа и Барбуда"] = 12888
categories_dict["Аргентина"] = 2153
categories_dict["Аруба"] = 13130
categories_dict["Багамы"] = 2879
categories_dict["Барбадос"] = 16142
categories_dict["Белиз"] = 15386
categories_dict["Бермуды"] = 12873
categories_dict["Боливия"] = 12875
categories_dict["Бразилия"] = 2152
categories_dict["Венесуэла"] = 12887
categories_dict["Виргинские острова"] = 13385
categories_dict["Гаити"] = 12878
categories_dict["Гайана"] = 16027
categories_dict["Гватемала"] = 12886
categories_dict["Гондурас"] = 12884
categories_dict["Доминиканская республика"] = 16030
categories_dict["Канада"] = 2149
categories_dict["Колумбия"] = 12882
categories_dict["Коста-Рика"] = 12876
categories_dict["Куба"] = 2150
categories_dict["Мексика"] = 2151
categories_dict["Никарагуа"] = 12885
categories_dict["Ньюфаундленд"] = 12874
categories_dict["Панама"] = 12879
categories_dict["Парагвай"] = 12883
categories_dict["Перу"] = 2154
categories_dict["Сальвадор"] = 16028
categories_dict["Суринам"] = 16029

categories_dict['США'] = {
    '1 доллар': 14815,
    '1 цент': 14809,
    '10 центов': 14811,
    '25 центов': 14812,
    '5 центов': 14810,
    '50 центов': 14813,
    'Наборы': 14815,
    'Разное': 14808
}

categories_dict["Тринидад и Тобаго"] = 12880
categories_dict["Уругвай"] = 12881
categories_dict["Фолклендские острова"] = 16141
categories_dict["Чили"] = 2155
categories_dict["Эквадор"] = 2156
categories_dict["Ямайка"] = 12877
categories_dict["Разное Америка"] = 2148
categories_dict["Острова Карибского бассеина"] = 12888
categories_dict["Каймановы острова"] = 12888

# Африка
categories_dict["Алжир"] = 12889
categories_dict["Ангола"] = 12890
categories_dict["Бенин"] = 12930
categories_dict["Ботсвана"] = 12925
categories_dict["Бурунди"] = 12924
categories_dict["Гамбия"] = 12915
categories_dict["Гана"] = 12901
categories_dict["Гвинея"] = 12900
categories_dict["Габон"] = 16336
categories_dict["Гвинея-Бисау"] = 16337
categories_dict["Джибути"] = 16140
categories_dict["Египет"] = 2165
categories_dict["Заир"] = 16031
categories_dict["Замбия"] = 12931
categories_dict["Зимбабве"] = 12932
categories_dict["Кабо-Верде"] = 13111
categories_dict["Камерун"] = 12929
categories_dict["Кения"] = 12899
categories_dict["Конго"] = 12895
categories_dict["Кот-д Ивуар"] = 16340
categories_dict["Лесото"] = 12906
categories_dict["Либерия"] = 12910
categories_dict["Ливия"] = 12911
categories_dict["Маврикий"] = 12920
categories_dict["Мавритания"] = 12921
categories_dict["Мадагаскар"] = 12907
categories_dict["Малави"] = 12927
categories_dict["Марокко"] = 12892
categories_dict["Мозамбик"] = 12891
categories_dict["Намибия"] = 12926
categories_dict["Нигерия"] = 12893
categories_dict["Острова Святой Елены"] = 16343
categories_dict["Республика Конго"] = 2168
categories_dict["Родезия"] = 12922
categories_dict["Руанда"] = 12923
categories_dict["Сан-Томе"] = 12898
categories_dict["Принсипи"] = 12898
categories_dict["Сахара"] = 2168
categories_dict["Свазиленд"] = 12908
categories_dict["Сейшелы"] = 12916
categories_dict["Сомали"] = 12902
categories_dict["Сомалиленд"] = 12903
categories_dict["Судан"] = 12905
categories_dict["Сьерра-Леоне"] = 12904
categories_dict["Танзания"] = 12917
categories_dict["Того"] = 15207
categories_dict["Тунис"] = 12896
categories_dict["Уганда"] = 12909
categories_dict["Эритрея"] = 12928
categories_dict["Эфиопия"] = 12897
categories_dict["ЮАР"] = 2164
categories_dict["Чад"] = 2168
categories_dict["Восточная Африка"] = 2166
categories_dict["Острова Африки"] = 12918
categories_dict["Центральная Африка"] = 2168
categories_dict["Южная Африка"] = 2167
categories_dict["Британская Западная Африка"] = 15186
categories_dict["Восточно-Африканский валютный союз"] = 15206
categories_dict["Западно-Африканский валютный союз"] = 15207
categories_dict["Африканские штаты"] = 12933
categories_dict["Бельгийские колонии"] = 15187
categories_dict["Итальянские колонии"] = 12913
categories_dict["Немецкие колонии"] = 12914
categories_dict["Несуществующие государства Африка"] = 12919
categories_dict["Французские колонии"] = 12912
categories_dict["Разное Африка"] = 2163

# Ближний Восток
categories_dict["Бахрейн"] = 12952
categories_dict["Израиль"] = 12989
categories_dict["Иордания"] = 12946
categories_dict["Ирак"] = 12945
categories_dict["Иран"] = 12944
categories_dict["Йемен"] = 12951
categories_dict["Катар"] = 16032
categories_dict["Кувейт"] = 16033
categories_dict["Ливан"] = 12949
categories_dict["ОАЭ"] = 12950
categories_dict["Оман"] = 16034
categories_dict["Палестина"] = 12947
categories_dict["Саудовская Аравия"] = 16035
categories_dict["Сирия"] = 14681
categories_dict["Турция"] = 16475
categories_dict["Разное Ближний Восток"] = 12953

# Европа
categories_dict["Абхазия"] = 15376
categories_dict["Австрия"] = 2129
categories_dict["Азербайджан"] = 15373
categories_dict["Азоры"] = 13013
categories_dict["Албания"] = 12972
categories_dict["Андорра"] = 12290
categories_dict["Армения"] = 12975
categories_dict["Беларусь"] = 12976
categories_dict["Бельгия"] = 12980
categories_dict["Бенилюкс"] = 2135
categories_dict["Богемия и Моравия"] = 13014
categories_dict["Болгария"] = 12981
categories_dict["Босния и Герцеговина"] = 16036
categories_dict["Ватикан"] = 16037
categories_dict['Великобритания'] = 2144
categories_dict["Венгрия"] = 12987
categories_dict['Германия'] = 12406
categories_dict["Гибралтар"] = 13011
categories_dict["Гренландия"] = 13009
categories_dict["Греция"] = 2670
categories_dict["Грузия"] = 12978
categories_dict["Дания"] = 12985
categories_dict["Данциг"] = 13016
categories_dict["Джерси"] = 2138
categories_dict["Гернси"] = 2138
categories_dict["Остров Мэн"] = 2138
categories_dict["Ирландия"] = 12988
categories_dict["Исландия"] = 13008
categories_dict["Испания"] = 2136
categories_dict["Италия"] = 2131
categories_dict["Кипр"] = 2772
categories_dict["Крит"] = 12986
categories_dict["Латвия"] = 12979
categories_dict["Литва"] = 2763
categories_dict["Лихтенштейн"] = 13006
categories_dict["Люксембург"] = 13004
categories_dict["Македония"] = 12997
categories_dict["Мальта"] = 11380
categories_dict["Молдова"] = 12998
categories_dict["Монако"] = 13005
categories_dict["Нагорный Карабах"] = 13017
categories_dict["Нидерланды"] = 13007
categories_dict["Норвегия"] = 12990
categories_dict["Нотгельды"] = 2667
categories_dict["Олдерни"] = 13010
categories_dict["Польша"] = 12991
categories_dict["Португалия"] = 2137
categories_dict["Приднестровье"] = 15374
categories_dict["Румыния"] = 12992
categories_dict["Сан-Марино"] = 12993
categories_dict["Сербия"] = 12994
categories_dict["Скандинавия"] = 2134
categories_dict["Словакия"] = 12995
categories_dict["Словения"] = 12996
categories_dict["Украина"] = 13002
categories_dict["Фареры"] = 13012
categories_dict["Фарерские острова"] = 13012
categories_dict["Финляндия"] = 11448
categories_dict["Франция"] = 2130
categories_dict["Хорватия"] = 12982
categories_dict["Черногория"] = 12999
categories_dict["Чехия"] = 12983
categories_dict["Чехословакия"] = 12984
categories_dict["Швейцария"] = 2764
categories_dict["Швеция"] = 13000
categories_dict["Элдерни"] = 13010
categories_dict["Эстония"] = 12977
categories_dict["Югославия"] = 13003
categories_dict["Восточная Европа"] = 2133
categories_dict["Другое в Европе"] = 2139

categories_dict['Россия'] = {
    'years': {
            1997: {
                '1 рубль': 14727,
                '10 рублей': 14730,
                '2 рублей': 14728,
                '25 рублей': 14731,
                '3 рубля': 14939,
                '5 рублей': 14729,
                'Разное': 14715,
            },
            1991: 14712
    }
}
categories_dict['СССР'] = 14701

categories_dict['жетоны'] = {
    'СССР': 14362,
    'Россия': 14363,
    'Германия': 14354,
    "Южная Корея": 14357
}

metal_dict = {
    'Алюминиевая Бронза': '32',
    'Алюминий': '24',
    'Аурихалк': '33',
    'Белый Металл': '34',
    'Биллон': '35',
    'Биметалл': '44',
    'Бронза': '19',
    'Вирениум': '36',
    'Железо': '25',
    'Золото': '17',
    'Колокольный металл': '37',
    'Коронное золото': '38',
    'Латунь': '39',
    'Магний': '26',
    'Марганец': '27',
    'Медь': '20',
    'Медно-никель': '21',
    'Медь-Цинк': '22',
    'Нержавеющая сталь': '42',
    'Никелевая латунь': '40',
    'Никелевое серебро': '41',
    'Никель': '23',
    'Олово': '28',
    'Палладий': '15710',
    'Пинчбек': '43',
    'Платина': '29',
    'Потин': '45',
    'Пушечный металл': '44',
    'Пьютер': '46',
    'Серебро': '18',
    'Спекулум': '47',
    'Сталь': '48',
    'Томпак': '49',
    'Хром': '30',
    'Цинк': '31',
    'Электр': '50'
}

grades_dict = {
    'AG': '13',
    'AU': '7',
    'AU+': '167',
    'Basal': '15',
    'F': '10',
    'Fair': '14',
    'G': '12',
    'Пруф': '5',
    'АЦ': '6',
    'VF': '9',
    'VF+': '165',
    'VG': '11',
    'XF': '8',
    'XF+': '166'
}


class MeshokAPI:
    def __init__(self, token):
        self.token = token
        self.s = requests.Session()
        balance = self.check_wallet()
        logger.info(f'МЕШОК. Вход завершён. Ваш баланс API - {balance} очков.')

    def check_wallet(self):
        r = self.req('getAccountInfo')
        if 'balance' not in r:
            raise Exception('Мешок. Ошибка - не найдено значение баланса '
                f'при запросе к API. Результат запроса: {r}')
        balance = r['balance']
        if balance < meshok_balance_limit:
            raise Exception(f'Недостаточно очков API на сайте Мешок. Сейчас на балансе {balance} очков (необходимый минимум - {meshok_balance_limit}).\n'
                'Перейдите по ссылке, чтобы пополнить счёт: https://meshok.net/profile.php?what=sAPI')
        return balance

    def get_meshok_price(self, price):
        return ceil(price/100*meshok_price_index)*100

    def get_category_id(self, country, coin_name, coin_year):
        country, coin_name = country.lower(), coin_name.lower()
        try:
            coin_year = int(coin_year.split('-')[0]) if not isinstance(coin_year, int) else coin_year
        except ValueError:
            raise CategoryNotFound(f'Ошибка! Не удалось подобрать категорию на мешке для "{coin_name} {country} {coin_year}".')

        try:
            if 'жетон' in coin_name:
                country = [
                    country_name for country_name in categories_dict['жетоны']
                    if country_name.lower() == country][0]
                return categories_dict['жетоны'][country]

            country = [country_name for country_name in categories_dict if country_name.lower() == country][0]
            country_dict = categories_dict[country]

            if isinstance(country_dict, dict) and 'years' in country_dict:
                years = sorted(country_dict['years'].keys(), reverse=True)
                closest_year = [year for year in years if coin_year >= year][0]

                country_dict = country_dict['years'][closest_year]

            if isinstance(country_dict, dict):
                coin_search = [coin for coin in country_dict if coin.lower().startswith(coin_name)]
                coin_name = coin_search[0] if coin_search else 'Разное'
                return country_dict[coin_name]
            else:
                return country_dict
        except IndexError:
            raise CategoryNotFound(f'Ошибка! Не удалось подобрать категорию на мешке для "{coin_name} {country} {coin_year}".')


    def req(self, method, payload = {}):
        api_url = f'https://api.meshok.net/sAPIv1/{method}/{self.token}'
        r = self.s.post(api_url, data=payload)

        result_json = r.json()
        if result_json['success'] == -9:
            if meshok_ignore_mode:
                return {'balance':100}
            raise Exception(f'Недостаточно очков API для совершения операции на Мешок.Нет. Операция {method}.')

        sleep(1)
        return r.json()

    def get_item(self, item_id):
        r = self.req('getItemInfo', {'id':item_id})
        return r

    # https://meshok.net/help_api.php#updateItem
    def list_item(
            self, name, category_id, pictures, price,tags,
            sale_type = 'Sale',
            category_params = None,
            minimal_buyer_rate=0, 
            condition='new',
            common_descriptions = '', 
            coin_metal = '', coin_grade = '',
            year='', country='', face_value='',):

        if category_params is None:
            category_params = []

        if sale_type != 'Sale':
            raise Exception(f'MeshokAPI.list_item - тип продажи {sale_type} не предусмотрен.')

        if country.lower() == 'россия':
            lot_name = f'{face_value} {name} {year} {coin_metal}'
        elif country.lower() == 'ссср':
            lot_name = f'{face_value} {name} {year} {country} {coin_grade} {coin_metal}'
        else:
            lot_name = f'{face_value} {name} {year} {country} {coin_metal}'

        if len(lot_name) > 100:
            raise IncorrectLotName(f'Ошибка! Название лота на мешке не может превышать 100 символов. Название лота: {lot_name}.')

        payload = {}
        payload['name'] = lot_name
        payload['category'] = category_id
        payload['saleType'] = sale_type
        payload['price'] = price
        payload['quantity'] = 1
        payload['longevity'] = 100
        payload['curencyId'] = 2
        payload['tags'] = tags.replace('/', ' ')

        if 'комплект' in name.lower():
            category_params.append('784')

        if coin_metal:
            coin_metal = coin_metal.lower()
            valid_metal = [metal for metal in metal_dict if coin_metal == metal.lower()]
            if valid_metal:
                category_params.append(metal_dict[valid_metal[0]])
            else:
                print_error(f'МЕШОК. Не смогли найти подходящий металл для {coin_metal} __ {lot_name}.', file_log)
                raise Exception(f'Ошибка при загрузке лота на мешок!')

        if coin_grade:
            coin_grade = coin_grade.lower()
            valid_grade = [grade for grade in grades_dict if coin_grade.lower() == grade.lower()]
            if valid_grade:
                category_params.append(grades_dict[valid_grade[0]])
            else:
                print_error(f'МЕШОК. Не смогли найти подходящее состояние для {coin_grade} __ {lot_name}.', file_log)
                raise Exception(f'Ошибка при загрузке лота на мешок!')

        if category_params:
            payload['categoryParams'] = ','.join(str(i) for i in category_params)

        payload['payment'] = 'CASH,CARD,YANDEX,BITCOIN'
        payload['localDelivery'] = 'SELF'
        payload['delivery'] = 'WORLD'
        payload['localDeliveryPrice'] = meshok_local_delivery_price
        payload['countryDeliveryPrice'] = meshok_country_delivery_price
        payload['worldDeliveryPrice'] = meshok_world_delivery_price

        payload['minimalBuyerRate'] = minimal_buyer_rate
        payload['condition'] = condition
        payload['city'] = 59
        payload['deliveryText'] = meshok_delivery_text
        payload['description'] = meshok_default_description
        payload['pictures'] = pictures

        payload['commonDescriptions'] = common_descriptions
        payload['bestOffer'] = 'Y'
        r = self.req('listItem', payload)
        
        if 'result' in r:
            return r['result']['id']
        else:
            raise Exception(f'Ошибка при загрузке лота на мешок!\nОтправленный запрос: {payload}.\nПолученный от сервера ответ: {r}.')

    def delist_item(self, item_id):
        r = self.req('stopSale', {'id': item_id})
        return r
    def get_item(self, item_id):
        return self.req('getItemInfo', {'id': item_id})
    
    def relist_item(self, item_id):
        r = self.req('relistItem', {'id': item_id})
        #ffgrgrgergreg
        if 'result' in r:
            return r['result']
        else:
            raise Exception(f'Ошибка при загрузке лота на мешок!\nОтправленный запрос: {item_id}.\nПолученный от сервера ответ: {r}.')
    
    def update_price(self, item_id, price):
        payload = {}
        payload['id'] = item_id
        payload['price'] = price
        r = self.req('updateItem', payload)