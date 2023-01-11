import configparser
from __init__ import get_auth_parameters
import requests
import json 
from static_config import files_folder_name, logs_folder_name
import logging
import traceback
import telebot
from gdrive import GoogleDriveAPI
import odnoklassniki

    
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
config.read(config_path, encoding='utf-8-sig')

TELEGRAM_BOT_TOKEN_INFO = check_undefined(config, 'TELEGRAM', 'telegram_bot_token_info')
TELEGRAM_ADMIN_CHAT_ID = int(check_undefined(config, 'TELEGRAM', 'telegram_admin_chat_id'))

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

file_log = 'config_log.log'
logger = loger_auot(file_log, __name__)

def print_error(body, filename):
	tb = traceback.format_exc()
	logger.error(f"{body}______{tb}")
	bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(f'{logs_folder_name}/{filename}', 'rb'))

def print_error1(body, filename):
	# tb = traceback.format_exc()
	logger.error(f"{body}__")
	bot.send_document(TELEGRAM_ADMIN_CHAT_ID, open(f'{logs_folder_name}/{filename}', 'rb'))

try:
	gdrive = GoogleDriveAPI()
	# x = int('gi')
except:
    print_error('КОНФИГ: ошибка подключения к гуглу', file_log)

yml_filename = config['GDRIVE']['yml_filename']
try:
	google_drive_file_id = check_undefined(config, 'GDRIVE', 'google_drive_file_id')
except:
    try:
        google_drive_file_id = gdrive.create_file(yml_filename, share=True)
    except:
        print_error('КОНФИГ: ошибка создания гугл файла', file_log)
    config['GDRIVE']['google_drive_file_id'] = google_drive_file_id
    save_config()

pricelist_file = config['GDRIVE']['pricelist_file']
try:
	file_id_pricelist = check_undefined(config, 'GDRIVE', 'file_id_pricelist')
except:
    try:
        file_id_pricelist = gdrive.create_file(pricelist_file, share=True)
    except:
        print_error('КОНФИГ: ошибка создания гугл файла', file_log)
    config['GDRIVE']['file_id_pricelist'] = file_id_pricelist
    save_config()

ok_client_id = int(check_undefined(config, 'OK', 'ok_client_id'))
ok_client_key = check_undefined(config, 'OK', 'ok_client_key')
ok_client_secret = check_undefined(config, 'OK', 'ok_client_secret')
ok_album_id = int(check_undefined(config, 'OK', 'ok_album_id'))

def validate_odnoclassnici(ok):
	try: 
		user = ok.users.getCurrentUser()
	except odnoklassniki.api.OdnoklassnikiError:
		print_error1('Одноклассники - ваш токен устарел. Вам нужно его обновить. \n Инструкция как это сделать \n 1. Подтвердите доступ к приложению в вашем браузере (должно было открыться соответствующее окно.', file_log)

		redirect_uri = 'http://localhost'
		auth_url = f'https://connect.ok.ru/oauth/authorize?client_id={ok_client_id}&scope=VALUABLE_ACCESS,LONG_ACCESS_TOKEN,PHOTO_CONTENT&response_type=code&redirect_uri={redirect_uri}&layout=w'
		auth_parameters = get_auth_parameters(auth_url)
		code = auth_parameters['code'][0]
		access_token_url = f'https://api.ok.ru/oauth/token.do?code={code}&client_id={ok_client_id}&client_secret={ok_client_secret}&redirect_uri={redirect_uri}&grant_type=authorization_code'
		r = requests.post(access_token_url)
		ok_access_token = r.json()['access_token']
		
		print_error1(f'2. Ваш access_token = {ok_access_token} был успешно сохранён.', file_log)
		config['OK']['ok_access_token'] = ok_access_token
		save_config()

try:
	ok_access_token = check_undefined(config, 'OK', 'ok_access_token')
except:
	ok = odnoklassniki.Odnoklassniki(ok_client_key, ok_client_secret, undefined_value)
	validate_odnoclassnici(ok)