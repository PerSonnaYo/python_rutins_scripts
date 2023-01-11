import datetime
from datetime import date
from sqlalchemy import create_engine
from config import loger_auot, print_error
from config import  DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_TABLE

file_log = 'lave_poster.log'
logger = loger_auot(file_log, __name__)

try:
    conn_pg = create_engine(f'postgresql+psycopg2://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TABLE}')
except:
    print_error(f'END COINS.LAVE.RU: database start error ', file_log)
    raise "JO-Jo"

today = datetime.datetime.today()
today = date(today.year, today.month, today.day)
query = """DELETE FROM public.samara_table
	                WHERE date_end = '"""+str(today)+"""'::date;"""
with conn_pg.begin() as conn:
    try:
        conn.execute(query)
    except:
        print_error(f'END COINS.LAVE.RU: update  error ', file_log)
        raise "JO-Jo"