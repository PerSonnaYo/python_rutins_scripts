import odnoklassniki
import requests
from time import sleep
from old_config import validate_odnoclassnici
from old_config import ok_client_key, ok_client_secret, ok_access_token, ok_client_id, ok_album_id
from requests import exceptions as rex
from ssl import SSLEOFError
from urllib3 import exceptions as uex
class OKApi:
	def __init__(self, ok_client_id, ok_client_key, ok_client_secret, ok_access_token):
		self.ok = odnoklassniki.Odnoklassniki(ok_client_key, ok_client_secret, ok_access_token)
		validate_odnoclassnici(self.ok)

	def upload_photo(self, album_id, filename = '', url = '', description=''):

		upload_url_response = self.ok.photosV2.getUploadUrl(aid=album_id)
		upload_url = upload_url_response['upload_url']
		photo_id = upload_url_response['photo_ids'][0]
		payload = {}

		if filename == '' and url == '':
			raise Exception('OKApi.upload_photo - filename and url both are empty!')
		sleep(10)
		if filename == '':
			r = requests.get(url)
			pic_content = r.content
		else:
			with open(filename, 'rb') as fi:
				pic_content = fi.read()

		payload['pic1'] = (filename, pic_content, 'image/jpeg')
		headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 YaBrowser/21.8.3.607 Yowser/2.5 Safari/537.36',
            'accept-language': 'ru',
        }
		sleep(10)
		upload_r = requests.post(upload_url, files=payload, headers=headers)
		token = upload_r.json()['photos'][photo_id]['token']
		sleep(10)
		commit_r = self.ok.photosV2.commit(token = token, 
				photo_id = photo_id, comment = description)

		return commit_r['photos'][0]['assigned_photo_id']

	def change_photo_description(self, photo_id, description):
		r = self.ok.photos.editPhoto(photo_id=photo_id, description=description)

	def remove_photo(self, photo_id):
		r = self.ok.photos.deletePhoto(photo_id=photo_id)

if __name__ == "__main__":
	ok = OKApi(ok_client_id, ok_client_key, ok_client_secret, ok_access_token)
	# a = ok.upload_photo(filename='test.jpg', album_id=ok_album_id, description='testtest')
	# print(a)

	# url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Google_Images_2015_logo.svg/1200px-Google_Images_2015_logo.svg.png'
	# a = ok.upload_photo(url=url, album_id=ok_album_id, description='testtest')

	photo_id = 887461703465
	ok.remove_photo(photo_id)