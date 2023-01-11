# -*- coding: utf-8 -*-
# pip install python-telegram-bot

# start - показать меню с командами
# next_cron - узнать, когда будут следующие запуски cron
# postpone - отложить следующее обновление программы cron на n минут. Например, "/postpone vk_sync" или "/postpone vk_sync 10" 
# force - принудительно вызвать запуск программы cron через минуту. Например, "/force vk_sync"
# items - показывает список активных лотов. Можно через пробел после команды добавлять ключевые слова. Например, "/items ермак 2005 серебро"
# delist - переносит лот с указанным Item ID в специальный альбом. Например, "/delist 52"
# confirm - команда для подтверждения различных операций
# cancel - команда для отмены различных операций
# send_pricelist - отправить прайс-лист на указанную почту
# whoami - узнать свой телеграм id (для внесения в конфиг бота)
import subprocess
import sys
import io
import datetime as dtm
from datetime import datetime, timedelta
from turtle import color
from dateutil import tz
from functools import wraps
from itertools import cycle, islice
import os
import shutil
from glob import glob
from time import sleep
import re

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

from email_interface import send_email

from config import PIC1_FILENAME, loger_auot, print_error, DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_TABLE
from static_config import temp_folder_name

file_log = 'teleg_email.log'
logger = loger_auot(file_log, __name__)

today = datetime.today()

try:
    conn_pg = create_engine(f'postgresql+psycopg2://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TABLE}')
except:
    print_error(f'email_daily_stat: base fail', file_log)
    raise "JO-Jo"
try:
    active_items = pd.read_sql("""select * from
                        (select sum(price) as val, kind as seria
                                from main_base_coins bbc
                                left join 
                                    (select id, kind from described) d
                                    on d.id = bbc.seria
                                where bbc.status in (4,5,6,7,8) and date_sale between '"""+str(today.year)+"""-"""+str(today.month)+"""-01' and current_date
                                group by 2
                                order by 1 desc)dd
                            limit 5
                                """, con=conn_pg)
    stat_yers = pd.read_sql("""select * from
                        (select coalesce(sum(price), 0) as val, coalesce(sum(price) - sum(selfprice), 0) as prof, coalesce(sum(amount), 0) as num
                                from main_base_coins bbc
                                where bbc.status in (4,5,6,7,8) and date_sale::date = current_date - interval '1 day'
                                )dd
                                """, con=conn_pg)
    buy_yers = pd.read_sql("""select * from
                        (select coalesce(sum(selfprice), 0) as val, count(*) as num
                                from main_base_coins bbc
                                where bbc.status in (1) and dates::date = current_date - interval '1 day'
                                )dd
                                """, con=conn_pg)
    stat_month_yers = pd.read_sql("""select * from
                        (select coalesce(sum(price), 0) as val, coalesce(sum(price) - sum(selfprice), 0) as prof, coalesce(sum(amount), 0) as num
                                from main_base_coins bbc
                                where bbc.status in (4,5,6,7,8) and date_sale between '"""+str(today.year)+"""-"""+str(today.month)+"""-01' and current_date
                                )dd
                                """, con=conn_pg)
    buy_month_yers = pd.read_sql("""select * from
                        (select coalesce(sum(selfprice), 0) as val, count(*) as num
                                from main_base_coins bbc
                                where bbc.status in (1) and dates::date between '"""+str(today.year)+"""-"""+str(today.month)+"""-01' and current_date
                                )dd
                                """, con=conn_pg)
    stat_week_yers = pd.read_sql("""select * from
                        (select coalesce(sum(price), 0) as val, coalesce(sum(price) - sum(selfprice), 0) as prof, coalesce(sum(amount), 0) as num
                                from main_base_coins bbc
                                where bbc.status in (4,5,6,7,8) and date_sale::date between cast(date_trunc('week', current_date - interval '1 day') as date) and current_date - interval '1 day'
                                )dd
                                """, con=conn_pg)
    buy_week_yers = pd.read_sql("""select * from
                        (select coalesce(sum(selfprice), 0) as val, count(*) as num
                                from main_base_coins bbc
                                where bbc.status in (1) and dates::date between cast(date_trunc('week', current_date - interval '1 day') as date) and current_date - interval '1 day'
                                )dd
                                """, con=conn_pg)
except:
    print_error(f'email_daily_stat: read_sql fail', file_log)
    raise "JO-Jo"

try:
    fig, ax = plt.subplots(1, 1, sharey=True, figsize=(15, 8))
    my_colors = list(islice(cycle(['b', 'r', 'g', 'y', 'k']), None, len(active_items)))
    ax.barh(active_items['seria'], active_items['val'], 1, color=my_colors)

    fig.suptitle(t='Топ 5 самых доходных серий в текущем месяце',
    fontsize=15)
    # f
    ax.grid(axis='x')
    fig.savefig(f'{temp_folder_name}/{PIC1_FILENAME}', facecolor = 'green')
except:
    print_error(f'email_daily_stat: ошибка в графике', file_log)
    raise "JO-Jo"

receiver_email = 'monetaspb@bk.ru'
email_text = f"""
Продано за вчера:
    - Валовый доход: {stat_yers.iloc[0][0]:_}
    - Прибыль: {stat_yers.iloc[0][1]:_}
    - Кол-во: {stat_yers.iloc[0][2]:_}

Куплено за вчера:
    - Всего потрачено: {buy_yers.iloc[0][0]:_}
    - Кол-во: {buy_yers.iloc[0][1]:_}

Приток денежных средств (дневной):
    - {(stat_yers.iloc[0][0] - buy_yers.iloc[0][0]):_}

Продано за месяц:
    - Валовый доход: {stat_month_yers.iloc[0][0]:_}
    - Прибыль: {stat_month_yers.iloc[0][1]:_}
    - Кол-во: {stat_month_yers.iloc[0][2]:_}

Куплено за месяц:
    - Всего потрачено: {buy_month_yers.iloc[0][0]:_}
    - Кол-во: {buy_month_yers.iloc[0][1]:_}

Приток денежных средств (месячный):
    - {(stat_month_yers.iloc[0][0] - buy_month_yers.iloc[0][0]):_}

Продано за неделю:
    - Валовый доход: {stat_week_yers.iloc[0][0]:_}
    - Прибыль: {stat_week_yers.iloc[0][1]:_}
    - Кол-во: {stat_week_yers.iloc[0][2]:_}

Куплено за неделю:
    - Всего потрачено: {buy_week_yers.iloc[0][0]:_}
    - Кол-во: {buy_week_yers.iloc[0][1]:_}

Приток денежных средств (недельный):
    - {(stat_week_yers.iloc[0][0] - buy_week_yers.iloc[0][0]):_}
    
    """
attachment = {PIC1_FILENAME : f'{temp_folder_name}/{PIC1_FILENAME}'}
try:
    send_email(receiver_email, 'Daily analize', email_text, attachment)
    logger.info('email: успешно отправлено')
except:
    print_error(f'email_daily_stat: В процессе отправки файла возникла ошибка. Подробнее:\n', file_log)
    raise "JO-Jo"
