# -*- coding: utf-8 -*-
from cmath import exp
import re

from random import randint
from time import sleep
from datetime import datetime, timedelta
# from openpyxl import load_workbook

from phpbb_interface import PhpbbAPI

from static_config import lave_poster_preview_mode
from config import lave_password, lave_login, loger_auot, print_error, DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_TABLE
from sqlalchemy import create_engine, text
import pandas as pd

file_log = 'lave_poster.log'
logger = loger_auot(file_log, __name__)

forum_id1 = [120, 139]#номера форумов на сайте
lave_daily_limit = 12
lave_base_message = 'Антиснайпер: ставка, сделанная менее чем за 10 минут до окончания торгов, переносит окончание торгов на 10 минут вперед от времени этой ставки. Продление неоднократное. Местонахождение лота: Санкт-Петербург. Доставка и стоимость пересылки: 250 руб 1-ый класс. За работу почты ответственность не несу. Оплата: карта СБ, наличные и другое. Примечания: Выкуп лотов в течение 7 дней после окончания торгов. Связь по телефону через различные мессенджеры'

class LavePoster:
    def __init__(self):
        try:
            self.phpbb = PhpbbAPI('https://coins.lave.ru/forum/', lave_login, lave_password)
        except:
            print_error(f'Lave_Poster: php start error', file_log)
            raise "JO-Jo"
        try:
            self.db = create_engine(f'postgresql+psycopg2://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TABLE}')
        except:
            print_error(f'Lave_Poster: database start error', file_log)
            raise "JO-Jo"
        
    def prepare_for_lave(self, name, price, condition, ids):
        auction_ending_date = datetime.today() + timedelta(days=6)
        sp = name.split('.')
        parsed_year = int(re.findall(r'(\d+)', sp[2])[0])
        if 'Россия' in sp[4]:
            capsule = 'Монета вне капсулы на фото.' if parsed_year < 2013\
            else 'Монета в неоткрывайке на фото.'
        else:
            capsule = 'Монета вне капсулы на фото.'
        blitz_price = (int(price*1.2) // 100 * 100) if price < 3000 else (int(price*1.1) // 100 * 100)
        step = 30 if price <= 1500 else 50 if price <= 10000 else 100
        if 'Россия' in sp[4] or 'СССР' in sp[4]:
            subject = f"{sp[0]} {parsed_year} {sp[1]} до {auction_ending_date.strftime('%d.%m')}"
        else:
            subject = f"{sp[0]} {sp[4]} {parsed_year} {sp[1]} до {auction_ending_date.strftime('%d.%m')}"
        if condition == 1:
            condition = 'Идеал'
        else:
            condition = 'Есть дефекты'
        message = f"Старт: {price}\n"\
            f"Шаг: {step}\n"\
            f"Блиц: {blitz_price}\n"\
            f"Год: {parsed_year}\n"\
            f"Описание лота: Состояние монеты: {condition}. {capsule} Предоплата\n"\
            f"Окончание: до 22:00 {auction_ending_date.strftime('%d.%m.%y')}\n"\
            f"{lave_base_message}"
        if 'Россия' in sp[4] or 'СССР' in sp[4]:
            forum_id = forum_id1[0]
        else:
            forum_id = forum_id1[1]
        query = """ update samara_table as f
                    set date_end = '"""+str(auction_ending_date)+"""'
                    where f.id = """+str(ids)+"""::integer"""
        with self.db.begin() as conn:
            try:
                conn.execute(query)
            except:
                print_error(f'Lave_Poster: database start error {ids}\n', file_log)
                raise "JO-Jo"
        return forum_id, subject, message

    def announce(self, s='1'):
        logger.info(f'COINS.LAVE.RU: {s}')

    def post_items(self):
        query="""
            select distinct st.*, mbc.name, mbc.photo_url1, mbc.photo_url2
            from samara_table st
            left join main_base_coins mbc
                on st.id = mbc.id
            where st.status = 1 and mbc.status = 2 limit 14
        """
        #прасим монеты и выставляем
        try:
            items = pd.read_sql(text(query), con=self.db)
        except:
            print_error(f'Lave_Poster: read_sql end', file_log)
            raise "JO-Jo"
        for i, item in items.iterrows():
            # print(item['name'])
            try:
                forum_id, subject, message = self.prepare_for_lave(item['name'], item['price'], item['condition'], item['id'])
                images = [item['photo_url1'], item['photo_url2']]
            except:
                hi = item['id']
                print_error(f'Lave_Poster: parsing error {hi}\n', file_log)
                raise "JO-Jo"
            try:
                thread_dict = self.phpbb.create_thread(forum_id, subject, message, attach_urls=images, preview=lave_poster_preview_mode)
            except:
                hi = item['id']
                print_error(f'Lave_Poster: php function end samara table1 {hi}\n', file_log)
                query1 = """ update samara_table as f
                    set date_end = NULL
                    where f.id = """+str(hi)+"""::integer"""
                with self.db.begin() as conn:#подтираем дату окончания в случае ошибки
                    conn.execute(query1)
                raise "JO-Jo"
            query = """update samara_table as f
            set status = 0
            where f.id = """+str(item['id'])+"""::integer"""
            with self.db.begin() as conn:
                try:
                    conn.execute(query)
                except:
                    hi = item['id']
                    print_error(f'Lave_Poster: update STATUS 0 {hi}\n', file_log)
                    raise "JO-Jo"
            if not lave_poster_preview_mode:
                self.announce(f'Была создана тема с лотом - {thread_dict["url"]} '\
                    f'(IID {item["name"]}).')
                thread_id = thread_dict['thread']
            # self.db.set_lave_listing(item.item_id, forum_id, thread_id)
            if i != len(items) - 1:
                sleep_time = randint(120, 240)
                self.announce(f'Ожидание перед следующим постом составит {sleep_time} секунд.')
                sleep(sleep_time)

        self.announce('Загрузка лотов завершена.')

if __name__ == '__main__':
    poster = LavePoster()
    logger.info('COINS.LAVE.RU: start succsses')
    poster.post_items()
