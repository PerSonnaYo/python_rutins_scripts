# ======================================
# Новые инструкции:

# Инструкция 1. Базовая установка скрипта.
# 1. Скачиваете установщик Python и устанавливаете. 
# Ссылка на скачивание если у вас 64 битный Windows - https://www.python.org/ftp/python/3.7.4/python-3.7.4-amd64.exe
# Ссылка на скачивание если у вас 32 битный Windows - https://www.python.org/ftp/python/3.7.4/python-3.7.4.exe
# Порядок установки: в первом окне обязательно поставьте галочку "ADD Python 3.7 to PATH" и нажимайте Install Now.
# 2. Открываете командную строку Windows (Пуск - Выполнить - вводите cmd - OK)
# 3. В командной строке вводите следующие команды одну за другой (устанавливаем доп библиотеки для python):
# pip install vk
# pip install openpyxl
# pip install odnoklassniki
# pip insatll lxml
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# pip install pydrive
# 4. Файлы со скриптом распаковываете в любую удобную вам папку.
# 5. Открываете блокнотом файл config.ini, в нём необходимо заполнить несколько переменных
# 5.1 ключ доступа к приложению вконтакте (service_token), код приложения(client_id) и защищённый ключ - подробно описано в Инструкции 2
# 5.2 ID альбома, из которого нужно считать записи - открываете нужный альбом вконтакте и берёте код из ссылки. 
# Пример: если ссылка на альбом https://vk.com/album255326569_205725316, то код альбома - 205725316. Код вставляется на место XXXXXXXXX в строке album_id =
# 5.3 ID вашего профиля вконтакте. Можно также взять из ссылки на альбом.
# Пример: если ссылка на альбом https://vk.com/album255326569_205725316, то код профиля - 255326569. Код вставляется на место XXXXXXXXX в строке owner_id =
# 6. Запускаете run.bat - вы получите ошибку о том, что ваш access_token просрочен, открывается окно в браузере, подтверждаете доступ и ключ доступа сам записывается в файл.
# 7. Проходите Инструкцию 3.
# 8. Проходите Инструкцию 4.
# 9. Проходите Инструкцию 5.
# 10. Проходите Инструкцию 6.
# 11. Готово, запустите run.bat.

# Инструкция 2. Вам нужно будет зарегистрировать приложение вконтакте для того, чтобы скрипт мог через него отправлять соответствующие запросы. Для этого:
# 1. Перейдите по ссылке https://vk.com/apps?act=manage
# 2. Создать приложение
# 3. Как-нибудь назовите его. Платформа: Standalone-приложение.
# 4. После создания вы оказываетесь на странице настроек приложения. Перейдите в меню слева в раздел "Настройки".
# 5. Скопируйте ID приложения и вставьте в код ниже вместо XXXXXXXX в строке client_id = XXXXXXXX 
# 6. Скопируйте "Сервисный ключ доступа" и вставьте в код ниже вместо XXXXXXXXXXXXXXXXXXX в строке service_token = 'XXXXXXXXXXXXXXXXXXX'
# 7. Open API - выберите "Включён". 
# 8. В поле "базовый домен" впишите "localhost" (без кавычек).
# 9. В поле "Адрес сайта" впишите "http://localhost" (без кавычек).

# Инструкция 3. Google drive
# 1. Переходите по ссылке - https://developers.google.com/drive/api/v3/quickstart/python
# 2. Нажимаете синюю кнопку "Enable the Drive API"
# 3. В октрывшемя окне нажимаете "DOWNLOAD CLIENT CONFIGURATION", скачивается файл credentials.json
# 4. Перемещаете в папку со скриптом - credentials.json

# Инструкция 4. Аукцион.ru
# Внесите ваш имейл и пароль от аукцион.ру в файле config.ini в следующие строки на место XXXXXXXXXXXXXX:
# auction_email = 'XXXXXXXXXXXXXX' # <== Сюда вводить email от auction.ru 
# auction_password = 'XXXXXXXXXXXXXX' # <== Сюда вводить пароль от auction.ru 

# Инструкция 5. Мешок.ру
# 1. Перейдите по ссылке https://meshok.net/profile.php?what=sAPI
# 2. В разделе "Создать новый ключ досутпа" поставьте галочки на "Право на чтение" 
# и "Право на изменение и внесение новых данных" и нажмите кнопку "Создать."
# 3. Скопируйте ключ из раздела "Ваши ключи доступа к API" в файле config.ini в следующую строку на место XXXXXXXXXXXXXX:
# meshok_token = 'XXXXXXXXXXXXXX' # <== Сюда вводить ключ доступа от мешок.ру 
# 4. Для того, чтобы размещать лоты на мешке с помощью API, нужны очки API. Их стоимость - 1 руб за 1000 очков, 1 размещение лота = 100 очков.
# Проверьте, что у вас на балансе есть как минмум более 100 API очков.
# Это можно проверить по той же ссылке в разделе "API-счёт" -> "Баланс".
# 5. Если их недостаточно, то нужно пополнить счёт - это можно сделать
# на той же страницей, в разделе "Пополнить API-счёт", достаточно добавить несколько рублей.

# Инструкция 6. Одноклассники
# 1. Зайдите на ok.ru/devaccess и подтвердите доступ. 
# 2. Переходите в список приложений - https://ok.ru/vitrine/myuploaded
# 3. Добавьте приложение и дайте ему какое-нибудь название. В разделе права для PHOTO_CONTENT ставите маркер на "обязательно".
# В раздел "Список разрешённый redirect_uri" впишите "http://localhost" (без кавычек).
# 4. Зайдите на почту, на которую зарегистрирован профиль Одноклассники, - туда должно прийти письмо с данными приложения.
# 5. Вставляете данные из этого письма на место XXXXXXXXX в следующих переменных в файле config.ini:
# - Application ID = > ok_client_id
# - Публичный ключ приложения = > ok_client_key
# - Секретный ключ приложения = > ok_client_secret
# 6. Пишите письмо с этой почты на "api-support@ok.ru". Большинство прав для приложения можно получить только запросив их у API поддержки одноклассников. Ждёте ответа на письмо (может занять день).
# Тема: Запрос прав для приложения. 
# Пример текста письма (обратите внимание, что на место XXXXXXXXXXX нужно внести ваш Application ID): 
# "Здравствуйте. Я создал приложение (application ID = XXXXXXXXXXX). Я буду использовать его для просмотра и загрузки фотографий в профиль. Соответственно, мне нужны следующие права - VALUABLE_ACCESS, PHOTO_CONTENT, LONG_ACCESS_TOKEN (поправьте, если что-то забыл). Прошу выдать."
# 7. Запускаете run.bat. Вы получите ошибку о том, что сессия устарела, открывается окно в браузере, подтверждаете доступ и ключ доступа сам записывается в файл.
# 8. Заходите в одноклассники и находите альбом, в который нужно загружать фотографии.
# Ссылка на альбом имеет следующий вид: https://ok.ru/profile/YYYYYYYYYY/album/XXXXXXXXXX
# Вам нужно скопировать XXXXXXXXXX из неё и вставить в config.ini в с


# формат описания вконтакте следующий - обратите внимание, что разделение идёт строго по точкам.
# Формула: {Номинал}. {Название}. {Год}г. {Состояние}. {Страна}. {Металл}. Цена {Цена} руб.
# Пример: 10 песо. Цветы, Биденс пилоса. 1997г. Пруф. Куба. Серебро. Цена 2000 руб. По всем вопросам в Л.С.

import configparser
# from . import get_auth_parameters
import requests
import json 
from static_config import files_folder_name, logs_folder_name
import logging
import traceback
import telebot

undefined_value = 'XXXXXXXXXXXXXXXXXX'
config_path = f'{files_folder_name}/config.ini'

def save_config():
	with open(config_path, 'w', encoding='utf-8-sig') as configfile:
		config.write(configfile)

def check_undefined(config, section, parameter):
	value = config[section][parameter]
	if value == undefined_value:
		raise Exception(f'Не заполнено значения для параметра {parameter}, раздел {section}.')

	return value

config = configparser.ConfigParser()
# print(config_path)
config.read(config_path, encoding='utf-8-sig')
# for r in config.keys(): 
# 	print(r)

upload_limit = int(config['GENERAL']['upload_limit'])

VK_ACCESS_TOKENS = json.loads(config['VK']['vk_access_tokens'])#токен
VK_ACCESS_TOKEN_EGOR = check_undefined(config, 'VK', 'vk_access_token')#альбом в наличии
VK_ALBUM_ID_FROM = int(check_undefined(config, 'VK', 'vk_album_id_from'))#альбом в наличии
VK_ALBUM_ID_BRON = int(check_undefined(config, 'VK', 'vk_album_id_bron'))#альбом для брони
VK_ALBUM_ID_END = int(check_undefined(config, 'VK', 'vk_album_id_end'))#альбом проданных монет
VK_OWNER_ID = int(check_undefined(config, 'VK', 'vk_owner_id'))#владелец аккаунта
VK_LIMIT_TRY = int(check_undefined(config, 'VK', 'vk_limit_try'))# количество попыток для операций в вк
VK_VERSION = config['VK']['vk_version']#версия вк апи
# VK_ACCESS_TOKENS = {int(owner_id): VK_ACCESS_TOKENS[owner_id] for owner_id in VK_ACCESS_TOKENS}

VK_SECOND_LISTING_ALBUMS = json.loads(config['VK']['vk_second_listing_albums'])
VK_SECOND_LISTING_ALBUMS = {
	int(owner_id): int(VK_SECOND_LISTING_ALBUMS[owner_id]) 
	for owner_id in VK_SECOND_LISTING_ALBUMS
}
# try:
# 	VK_ACCESS_TOKEN = check_undefined(config, 'VK', 'vk_access_token')
# except:
# 	import vk
# 	s = vk.Session()
# 	api =vk.API(s, v=vk_version, lang='ru', timeout=10)
# 	try:
# 		r = api.secure.checkToken(token=undefined_value, access_token=VK_SERVICE_TOKEN)
# 	except vk.exceptions.VkAPIError as e:
# 		manual_auth_url = auth_url = f'https://oauth.vk.com/authorize?client_id={VK_CLIENT_ID}'\
# 		'&display=page&redirect_uri=https://oauth.vk.com/blank.html&response_type=token'\
# 		f'&v={VK_VERSION}&scope=offline,photos'
# 		redirect_uri = 'http://localhost/'
# 		auth_url = f'https://oauth.vk.com/authorize?client_id={VK_CLIENT_ID}'\
# 		f'&display=page&redirect_uri={redirect_uri}&response_type=code'\
# 		f'&v={VK_VERSION}&scope=offline,photos'
# 		print(f'Ошибка! Ваш access_token просрочен. Обновите access_token в файле.')
# 		print(f'Техническое описание попытки подключения: {str(e)}\n')
# 		print(f'Обновление access_token (ключ доступа профиля вконтакте): ')
# 		print(f'1. Подтвердите доступ к приложению в вашем браузере '\
# 			'(должно было открыться соответствующее окно).')

# 		auth_parameters = get_auth_parameters(auth_url)
# 		code = auth_parameters['code'][0]
# 		access_token_url = f'https://oauth.vk.com/access_token?client_id={VK_CLIENT_ID}'\
# 		f'&client_secret={VK_CLIENT_SECRET}&redirect_uri={redirect_uri}&code={code}'
# 		r = requests.get(access_token_url)
# 		fetched_access_token = r.json()['access_token']
# 		config['VK']['vk_access_token'] = fetched_access_token
# 		save_config()
# 		print(f'2. Ваш access_token = {fetched_access_token} был успешно сохранён.')


meshok_token = check_undefined(config, 'MESHOK', 'meshok_token')
meshok_balance_limit = int(config['MESHOK']['meshok_balance_limit'])
meshok_default_description = config['MESHOK']['meshok_default_description']
meshok_price_index = float(config['MESHOK']['meshok_price_index'])
meshok_local_delivery_price = int(config['MESHOK']['meshok_local_delivery_price'])
meshok_country_delivery_price = int(config['MESHOK']['meshok_country_delivery_price'])
meshok_world_delivery_price = int(config['MESHOK']['meshok_world_delivery_price'])
meshok_delivery_text = config['MESHOK']['meshok_delivery_text']

auction_email = check_undefined(config, 'AUCTION', 'auction_email')
auction_password = check_undefined(config, 'AUCTION', 'auction_password')
auction_default_description = config['AUCTION']['auction_default_description']
auction_active_lots = int(config['AUCTION']['auction_active_lots'])
auction_delivery_pochta_city = int(config['AUCTION']['auction_delivery_pochta_city'])
auction_delivery_pochta_country = int(config['AUCTION']['auction_delivery_pochta_country'])
auction_delivery_pochta_world = int(config['AUCTION']['auction_delivery_pochta_world'])
auction_delivery_pochta_commentary = config['AUCTION']['auction_delivery_pochta_commentary']
auction_delivery_pickup_commentary = config['AUCTION']['auction_delivery_pickup_commentary']
auction_delivery_other_city = int(config['AUCTION']['auction_delivery_other_city'])
auction_delivery_other_country = int(config['AUCTION']['auction_delivery_other_country'])
auction_delivery_other_commentary = config['AUCTION']['auction_delivery_other_commentary']


yml_filename = config['GDRIVE']['yml_filename']
pricelist_file = config['GDRIVE']['pricelist_file']
# try:
# 	google_drive_file_id = check_undefined(config, 'GDRIVE', 'google_drive_file_id')
# except:
# 	from gdrive import GoogleDriveAPI
# 	gdrive = GoogleDriveAPI()
# 	google_drive_file_id = gdrive.create_file(yml_filename, share=True)
# 	config['GDRIVE']['google_drive_file_id'] = google_drive_file_id
# 	save_config()
# try:
# 	file_id_pricelist = check_undefined(config, 'GDRIVE', 'file_id_pricelist')
# except:
# 	from gdrive import GoogleDriveAPI
# 	gdrive = GoogleDriveAPI()
# 	file_id_pricelist = gdrive.create_file(pricelist_file, share=True)
# 	config['GDRIVE']['file_id_pricelist'] = file_id_pricelist
# 	save_config()

# ok_client_id = int(check_undefined(config, 'OK', 'ok_client_id'))
# ok_client_key = check_undefined(config, 'OK', 'ok_client_key')
# ok_client_secret = check_undefined(config, 'OK', 'ok_client_secret')
# ok_album_id = int(check_undefined(config, 'OK', 'ok_album_id'))

# try:
# 	ok_access_token = check_undefined(config, 'OK', 'ok_access_token')
# except:
# 	import odnoklassniki
# 	ok = odnoklassniki.Odnoklassniki(ok_client_key, ok_client_secret, undefined_value)
# 	try: 
# 		user = ok.users.getCurrentUser()
# 	except odnoklassniki.api.OdnoklassnikiError:
# 		print('Одноклассники - ваш токен устарел. Вам нужно его обновить.')
# 		print(f'Инструкция как это сделать')
# 		print(f'1. Подтвердите доступ к приложению в вашем браузере (должно было открыться соответствующее окно.')

# 		redirect_uri = 'http://localhost'
# 		auth_url = f'https://connect.ok.ru/oauth/authorize?client_id={ok_client_id}&scope=VALUABLE_ACCESS,LONG_ACCESS_TOKEN,PHOTO_CONTENT&response_type=code&redirect_uri={redirect_uri}&layout=w'
# 		auth_parameters = get_auth_parameters(auth_url)
# 		code = auth_parameters['code'][0]
# 		access_token_url = f'https://api.ok.ru/oauth/token.do?code={code}&client_id={ok_client_id}&client_secret={ok_client_secret}&redirect_uri={redirect_uri}&grant_type=authorization_code'
# 		r = requests.post(access_token_url)
# 		ok_access_token = r.json()['access_token']

# 		print(f'2. Ваш access_token = {ok_access_token} был успешно сохранён.')
# 		config['OK']['ok_access_token'] = ok_access_token
# 		save_config()

lave_login = check_undefined(config, 'LAVE', 'lave_login')
lave_password = check_undefined(config, 'LAVE', 'lave_password')
lave_daily_limit = int(config['LAVE']['lave_daily_limit'])
lave_base_message = config['LAVE']['lave_base_message']

TELEGRAM_BOT_TOKEN_INFO = check_undefined(config, 'TELEGRAM', 'telegram_bot_token_info')
TELEGRAM_ADMIN_CHAT_ID = int(check_undefined(config, 'TELEGRAM', 'telegram_admin_chat_id'))
TELEGRAM_BOT_TOKEN_MAIN = check_undefined(config, 'TELEGRAM', 'telegram_bot_token_main')
TELEGRAM_BOT_TOKEN_BRON = check_undefined(config, 'TELEGRAM', 'telegram_bot_token_bron')
TELEGRAM_CRON_LAVE_POSTER_INTERVAL = int(config['TELEGRAM']['telegram_cron_lave_poster_interval'])
TELEGRAM_CRON_INSTAGRAM_INTERVAL = int(config['TELEGRAM']['telegram_cron_instagram_interval'])
TELEGRAM_CRON_YOULA_PREMIUM_INTERVAL = int(config['TELEGRAM']['telegram_cron_youla_premium_interval'])
TELEGRAM_CRON_YOULA_SECOND_INTERVAL = int(config['TELEGRAM']['telegram_cron_youla_second_interval'])
TELEGRAM_CRON_VK_LISTING_MAIN_INTERVAL = int(config['TELEGRAM']['telegram_cron_vk_listing_main_interval'])
TELEGRAM_CRON_VK_LISTING_SECOND_INTERVAL = int(config['TELEGRAM']['telegram_cron_vk_listing_second_interval'])

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN_INFO)

def loger_auot(filename, name):
	file_log = f'{logs_folder_name}/{filename}'
	global logger
	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)
	logger.propagate = False

	log_fh = logging.FileHandler(
			file_log, 
			encoding='utf-8')
	log_fh.setLevel(logging.ERROR)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	log_fh.setFormatter(formatter)
	logger.addHandler(log_fh)

	log_ch = logging.StreamHandler()
	log_ch.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(message)s')
	log_ch.setFormatter(formatter)
	logger.addHandler(log_ch)
	return logger

def print_error(body, filename):
	tb = traceback.format_exc()
	logger.error(f"{body}______{tb}")
	bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(f'{logs_folder_name}/{filename}', 'rb'))

def send_message(mess):
	bot.send_message(TELEGRAM_ADMIN_CHAT_ID, f'{mess}')

# YOULA_PHONES = [int(l) for l in check_undefined(config, 'YOULA', 'youla_phones').splitlines() if l.strip()] # должны начинаться с "7"
# YOULA_PREMIUM_PHONE = int(check_undefined(config, 'YOULA', 'youla_premium_phone'))
# YOULA_PREMIUM_SESSION_UPLOAD_LIMIT = int(config['YOULA']['youla_premium_session_upload_limit'])
# YOULA_SECOND_SESSION_UPLOAD_LIMIT = int(config['YOULA']['youla_second_session_upload_limit'])

EMAIL_LOGIN = check_undefined(config, 'EMAIL', 'email_login')          
EMAIL_PASSWORD  = check_undefined(config, 'EMAIL', 'email_password')
PRICELIST_FILENAME = check_undefined(config, 'EMAIL', 'pricelist_filename')          
PIC1_FILENAME = check_undefined(config, 'EMAIL', 'pic1_name')

DB_LOGIN = check_undefined(config, 'POSTGRESQL', 'login')          
DB_PASSWORD  = check_undefined(config, 'POSTGRESQL', 'password')
DB_HOST = check_undefined(config, 'POSTGRESQL', 'host')          
DB_PORT = check_undefined(config, 'POSTGRESQL', 'port')
DB_TABLE = check_undefined(config, 'POSTGRESQL', 'current_db')

VK_MARKET_CATEGORY_ID = int(check_undefined(config, 'VK_MARKET', 'vk_market_category_id'))
VK_MARKET_OWNER_ID = int(check_undefined(config, 'VK_MARKET', 'vk_market_owner_id'))
