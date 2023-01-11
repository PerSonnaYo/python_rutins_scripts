from gdrive import GoogleDriveAPI
from sqlalchemy import create_engine
import pandas as pd
import os
from static_config import temp_folder_name, output_folder_name
from config import loger_auot, print_error, DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_TABLE, pricelist_file
from old_config import file_id_pricelist
import time
# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive

# gauth = GoogleAuth()
# client_json_path = '/mnt/c/Users/Administrator/dags/scripts/client_secrets.json'    
# GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = client_json_path
# gauth.LocalWebserverAuth()
file_config = f'{temp_folder_name}/old_config.conf'
file_log = 'teleg_email.log'
logger = loger_auot(file_log, __name__)
try:
    gdrive = GoogleDriveAPI()#подключаемся к гуглу
except:
    print_error(f'back_up: google login fail', file_log)
    raise "JO-Jo"

file_name = f"{temp_folder_name}/backup_coins_base.xlsx"
pricelist_name = f"{output_folder_name}/{pricelist_file}"

def make_hyperlink(value, names):
    url = "https://custom.url/{}"
    return '=HYPERLINK("%s", "%s")' % (value, names)


def handle_df(df):
    # print(df)
    # df['nominal'],df['name1'],df['year'],df['condition'],df['country'],df['metal'], df['d'] = df['name'].str.split('.')
    df['name1'] = df['name'].str.split('.')
    df['nominal'] = df['name1'].str[0]
    df['name'] = df['name1'].str[1].str.strip(' ')
    df['year'] = df['name1'].str[2].str.strip(' ')
    df['condition'] = df['name1'].str[3].str.strip(' ')
    df['country'] = df['name1'].str[4].str.strip(' ')
    df['metal'] = df['name1'].str[5].str.strip(' ')
    # df['name1'] = df['name1'].str.strip(' ')
    # nominal,name1,year,condition,country,metal = df.split('. ')
    df['year'] = pd.to_numeric(df['year'].str[:-1])
    df['hyperlink1'] = df['photo_url1'].apply(lambda x: make_hyperlink(x, 'Фото1'))
    df['hyperlink2'] = df['photo_url2'].apply(lambda x: make_hyperlink(x, 'Фото2'))
    df = df[['nominal', 'name', 'year', 'condition', 'country', 'metal', 'price', 'hyperlink1', 'hyperlink2', 'photo_url1', 'photo_url2']]
    return df
    # df['metal'] = df['metal'].str.replace('.', '')
    # print(df)
    # print(len(df.iloc[4][8]))
try:
    conn_pg = create_engine(f'postgresql+psycopg2://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TABLE}')
    df = pd.read_sql("""select bbc.id, name, price, selfprice, dd.status, amount, kind as seria, client, data_contact, ddd.method_sale, date_sale,
                               photo_id1, photo_id2, photo_url1, photo_url2, photo_url3, photo_url4, meshok_id, vmt.main_photo_id, vmt.second_photo_id, vmt.vk_market_id,
                               ot.ok_photo_id1, ot.ok_photo_id2
                            from main_base_coins bbc
                            left join 
                                (select id, kind from described) d
                                on d.id = bbc.seria
                            left join 
                                (select id, status from described) dd
                                on dd.id = bbc.status
                            left join 
                                (select id, method_sale from described) ddd
                                on ddd.id = bbc.method_sale
                            left join 
                                vk_market_table vmt on bbc.id = vmt.id
                            left join 
                                ok_table ot on ot.id = bbc.id
                            order by bbc.id
                        """, con=conn_pg)
    df1 = pd.read_sql("""select name, price, photo_url1, photo_url2
                            from main_base_coins bbc
                            where status = 2
                            order by bbc.id
                        """, con=conn_pg)
except:
    print_error(f'back_up: read_sql fail', file_log)
    raise "JO-Jo"

df2 = handle_df(df1)
try:
    gdrive.update(file_id_pricelist, pricelist_name)
    url = gdrive.get_urls(file_id_pricelist)
    url1 = f'url_pricelist = {url}'
    with open(file_config, mode='w') as f:
        f.write(url1)
except:
    print_error(f'back_up_pricelist: update DRIVE fail', file_log)

try:
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:  
        df.to_excel(writer, sheet_name='Sheet_name_1', index=False)
    with pd.ExcelWriter(pricelist_name, engine='xlsxwriter') as writer:  
        df2.to_excel(writer, sheet_name='Sheet_name_1', index=False)
except:
    print_error(f'back_up: excel fail', file_log)
    raise "JO-Jo"

# drive = GoogleDrive(gauth)

# my_file = drive.CreateFile({'title': f'{file_name}'})
# my_file.SetContentFile(file_name)
# my_file.Upload()
