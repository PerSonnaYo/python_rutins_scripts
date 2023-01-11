from requests import Session, Request
import requests
from lxml import etree
from time import sleep, time
from random import random
import json
from urllib.parse import urlparse, parse_qs

from static_config import phpbb_save_requests_mode

def save_request(r, filename ='test.html'):
	with open(f'{filename}', 'wb') as fo:
		fo.write(r.content)

def add_list_request_argument(argument_name, argument_list, arguments_dict):
	"""Функция нужна для того, чтобы встроить в тело запроса (модуль requests) аргумент-список.
	Функция встраивает аргумент-список argument_list под названием argument_name
	в словарь к прочим аргументам arguments_dict.
	Словарь в будущем будет передаваться в Request под аргументов files.
	У функции есть поддержка на случай, если перечисляемые элементы окажутся словарями.

	"""
	for i, entry in enumerate(argument_list):
		if isinstance(entry, dict):
			for key in entry:
				arguments_dict[f'{argument_name}[{i}][{key}]'] = (None, entry[key])
		else:
			arguments_dict[f'{argument_name}[{i}]'] = (None, entry)

class LoginFailed(Exception):
	pass


post_request_path = f'phpbb_post_request.txt'

class PhpbbAPI:
	def __init__(self, website, username, password):
		headers = {
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
			# 'Accept-Encoding': 'gzip, deflate',
			# 'Accept-Language': 'ru,en;q=0.9',
			# 'Cache-Control': 'max-age=0',
			# 'Connection': 'keep-alive',
			# # 'Content-Length': '241',
			# 'Content-Type': 'application/x-www-form-urlencoded',
			# # 'Cookie': '__utma=65667891.774383185.1572854022.1572854022.1572854022.1; __utmc=65667891; __utmz=65667891.1572854022.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); phpbb3_nvjt51_u=1; phpbb3_nvjt51_k=; phpbb3_nvjt51_sid=75b1ddeeda04d858961f62f45e25d52c',
			# 'DNT': '1',
			# 'Host': 'testingforum.listbb.ru',
			# 'Origin': 'http://testingforum.listbb.ru',
			# 'Referer': 'http://testingforum.listbb.ru/ucp.php?mode=login',
			# 'Upgrade-Insecure-Requests': '1',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 YaBrowser/19.10.1.238 Yowser/2.5 Safari/537.36'
		}

		self.website = website
		self.s = Session()
		self.s.headers.update(headers)
		self.login(username, password)

	def login(self, username, password):
		r = self.s.get(f'{self.website}')
		login_url = f'{self.website}/ucp.php?mode=login'
		r = self.s.get(login_url)
		self.delay()

		dom = etree.HTML(r.text)

		payload = []
		creation_time = dom.xpath('//input[@name="creation_time"]/@value')
		if creation_time:
			payload.append(['creation_time', creation_time[0]])
		else:
			print('PHPBBApi: Cannot find creation_time. Trying to login without it.')

		form_token = dom.xpath('//input[@name="form_token"]/@value')
		if form_token:
			payload.append(['form_token', form_token[0]])
		else:
			print('PHPBBApi: Cannot find form_token. Trying to login without it.')			

		sid = dom.xpath('//input[@name="sid"]/@value')[0]

		payload.append(['username', username])
		payload.append(['password', password])
		payload.append(['sid', sid])
		payload.append(['redirect', './ucp.php?mode=login'])
		payload.append(['redirect', 'index.php'])
		payload.append(['login', 'Вход'])

		r = self.s.post(login_url, data=payload)
		dom = etree.HTML(r.text)
		exit_link = dom.xpath('//a[contains(@href, "?mode=logout")]')

		if exit_link:
			print('PHPBBApi: Logged in successfully.')
		else:
			if phpbb_save_requests_mode:
				save_request(r, 'exit_link test.htm')
			raise LoginFailed('PHPBBApi: Cannot log in (cannot pass exit_link test).')


	def create_thread(self, forum_id, subject, message, attach_urls = [], preview = False):
		posting_url = f'{self.website}/posting.php?mode=post&f={forum_id}'
		r = self.s.get(posting_url)
		self.delay()

		payload = {}

		dom = etree.HTML(r.text)

		self.parse_basic_arguments_to_payload(dom, payload, files_mode=True)

		payload['icon'] = (None, 0)
		payload['subject'] = (None, subject)
		payload['addbbcode20'] = (None, 100)
		payload['message'] = (None, message)
		
		payload['attach_sig'] = (None, 'on')
		payload['topic_type'] = (None, 0)
		payload['topic_time_limit'] = (None, 0)
		payload['show_panel'] = (None, 'options-panel')
		payload['poll_title'] = (None, '')
		payload['poll_option_text'] = (None, '')
		payload['poll_max_options'] = (None, 1)
		payload['poll_length'] = (None, 0)

		if preview:
			payload['preview'] = (None, 'Preview')
		else:
			payload['post']  = (None, 'Submit')

		attached_files = []
		for file_url in attach_urls:
			r = requests.get(file_url)
			file_content = r.content
			filename = file_url.split('/')[-1]
			filename = filename.split('?')[0]
			file_format = filename.split('.')[-1]

			attach_payload = dict()
			attach_payload['name'] = (None, 'o_' + format(int(time()), '0x') + format(int(random()*65535), '0x') + format(int(random()*65535), '0x') + format(int(random()*65535), '0x') + format(int(random()*65535), '0x') + format(int(random()*65535), '0x') + '.' + file_format)
			attach_payload['real_filename'] = (None, filename)
			attach_payload['chunk'] = (None, 0)
			attach_payload['chunks'] = (None, 1)
			attach_payload['add_file'] = (None, 'Add the file')

			if 'creation_time' in payload:
				attach_payload['creation_time'] = (None, payload['creation_time'][1])

			if 'form_token' in payload:
				attach_payload['form_token'] = (None, payload['form_token'][1])

			attach_payload['fileupload'] = (filename, file_content, 'image/jpeg')

			headers = {
				'x-phpbb-using-plupload': "1",
				'x-requested-with': 'XMLHttpRequest'
			}
			post_attachment_url = f'{self.website}/posting.php?mode=post&f={forum_id}'

			req = Request('POST', post_attachment_url, files=attach_payload, headers=headers)
			req = self.s.prepare_request(req)

			r = self.s.send(req)

			try:
				attach_dict	 = r.json()['data'][0]
			except json.decoder.JSONDecodeError:
				dom = etree.HTML(r.text)
				attach_dict = dict()
				attach_dict['attach_id'] = dom.xpath('//input[@name="attachment_data[0][attach_id]"]/@value')[0]
				attach_dict['is_orphan'] = dom.xpath('//input[@name="attachment_data[0][is_orphan]"]/@value')[0]
				attach_dict['real_filename'] = dom.xpath('//input[@name="attachment_data[0][real_filename]"]/@value')[0]
				attach_dict['attach_comment'] = dom.xpath('//input[@name="attachment_data[0][attach_comment]"]/@value')[0]
				attach_dict['mimetype'] = dom.xpath('//input[@name="attachment_data[0][mimetype]"]/@value')[0]
				attach_dict['thumbnail'] = dom.xpath('//input[@name="attachment_data[0][thumbnail]"]/@value')[0]

			attached_files.append(attach_dict)

		add_list_request_argument('attachment_data', attached_files, payload)
		req = Request('POST', posting_url, files=payload)
		req = self.s.prepare_request(req)

		if phpbb_save_requests_mode:
			with open(post_request_path, 'wb') as fi:
				fi.write(bytes(str(req.headers), encoding='utf-8'))
				fi.write(bytes('\n', encoding='utf-8'))
				fi.write(req.body)

		r = self.s.send(req, allow_redirects=True)
		if phpbb_save_requests_mode:
			save_request(r, 'phpbb_thread_created.htm')

		# supposed to be more general solution
		# thread_url = dom.xpath('//h2[@class="topic-title"]/a/@href')[0] 

		if not preview:
			dom = etree.HTML(r.text)
			thread_url = dom.xpath('//h2/a/@href')[0] # non general solution 
			args = parse_qs(urlparse(thread_url).query)
			thread_dict = {'forum': args['f'][0], 'thread': args['t'][0], 'url': thread_url}
			return thread_dict

	def delete_thread(self, thread_id):
		delete_url = f'{self.website}/posting.php?mode=soft_delete&&p={thread_id}'


	def parse_basic_arguments_to_payload(self, dom_parse_from, payload_to_load, files_mode=False):
		creation_time = dom_parse_from.xpath('//input[@name="creation_time"]/@value')
		if creation_time:
			payload_to_load['creation_time'] = (None, creation_time[0]) if files_mode else creation_time[0]
	
		form_token = dom_parse_from.xpath('//input[@name="form_token"]/@value')
		if form_token:
			payload_to_load['form_token'] = (None, form_token[0]) if files_mode else form_token[0]


	def post_reply(self, thread_dict, message):
		thread_url = f'{self.website}/viewtopic.php?t={thread_dict["thread"]}'
		reply_url = f'{self.website}/posting.php?mode=reply&f={thread_dict["forum"]}&t={thread_dict["thread"]}'
		r = self.s.get(reply_url)
		self.delay()

		payload = {}
		dom = etree.HTML(r.text)

		self.parse_basic_arguments_to_payload(dom, payload)

		# subject = dom.xpath('//input[@id="subject"]/@value')[0]
		subject = dom.xpath('//input[@class="post"]/@value')[0] # NON GENERAL

		payload['icon'] = 0
		payload['subject'] = subject
		payload['addbbcode20'] = 100
		payload['message'] = message
		payload['post'] = 'Submit'
		payload['attach_sig'] = 'on'
		payload['show_panel'] = 'options-panel'

		r = self.s.post(reply_url, data=payload, allow_redirects=True)


	def delay(self):
		sleep(3)

	def close_auction(self, thread_dict):
		payments_url = f'{self.website}/payments.php'

		params = {}
		params['action'] = 'auction'
		params['f'] = thread_dict['forum']
		params['t'] = thread_dict['thread']
		params['aucowner'] = 103727

		payload = {}
		payload['summ'] = 0
		payload['aucwinner_id'] = 0
		payload['close-auc-btn'] = 'Закрыть лот'

		r = self.s.post(payments_url, params = params, data=payload)


# phpbb = PhpbbAPI('http://localhost/phpBB3', username, password)
# subject = 'test1'
# message = 'test 1 reply'
# # phpbb.create_thread(subject, message)
# thread_dict = {'forum': 2, 'thread': 9}

# phpbb.post_reply(thread_dict, message)


# https://coins.lave.ru/forum/viewforum.php?f=23
# https://yadi.sk/i/kzmvvPbBS98LOQ - ПОСТИНГ

# Закрытие аукциона: https://coins.lave.ru/forum/payments.php?action=auction&f=118&t=2137951&aucowner=103727
# https://yadi.sk/i/14kbtWFT9ZTCzQ

def login_lave_ru():
	from config import lave_login, lave_password

	phpbb = PhpbbAPI('https://coins.lave.ru/forum/', lave_login, lave_password)
	subject = 'test1'
	message = 'test 1 reply'
	forum_id = 118
	attach = ['https://i.imgur.com/REM4kQU.jpg', 'https://i.imgur.com/REM4kQU.jpg']
	t = phpbb.create_thread(forum_id, subject, message, attach_urls=attach, preview=True)
	print(t)
	# print(t)
	# phpbb.close_auction(t)
	# thread_dict = {'forum': '118', 'thread': '2137953'}
	# phpbb.post_reply(thread_dict, message)

def login_test_forum():
	from config import phpbb_test_login, phpbb_test_password

	phpbb = PhpbbAPI('http://localhost/phpBB3', phpbb_test_login, phpbb_test_password)
	subject = 'test1'
	message = 'test 1 reply'
	forum_id = 2

	images = ['https://i.imgur.com/REM4kQU.jpg', 'https://i.imgur.com/REM4kQU.jpg']

	t = phpbb.create_thread(forum_id, subject, message, attach_urls=images, preview=True)
	print(t)


if __name__ == "__main__":
	login_lave_ru()