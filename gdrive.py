# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from static_config import files_folder_name as temp_folder_name

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
'https://www.googleapis.com/auth/drive']

pickle_path = f'{temp_folder_name}/token.pickle'
credentials_path = f'{temp_folder_name}/credentials.json'

class GoogleDriveAPI:
    def __init__(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(pickle_path):
            print(pickle_path)
            with open(pickle_path, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                print('У вас должен был открыться браузер - нужно разрешить доступ приложению к Google Drive.')
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(pickle_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('drive', 'v3', credentials=creds)

    def files_list(self, folder_id):
        results = self.service.files().list(q=f"'{folder_id}' in parents and trashed = false").execute()
        items = results.get('files', [])
        return items

    def trash(self, file_id):
        self.service.files().trash(fileId=file_id).execute()

    def update(self, file_id, file_path, filename = None):
        if not filename:
            filename = file_path.split('/')[-1]

        # print(self.create_file(f'{filename}1'))
        file_metadata = {'name': filename}
        media = MediaFileUpload(file_path)
        # file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file = self.service.files().update(fileId=file_id, body=file_metadata, media_body=media).execute()

    def create_file(self, filename, folder_id=None, share=False):
        file_metadata = {
            'name': filename,
            'parents': [folder_id] if folder_id else []}
        r = self.service.files().create(body=file_metadata).execute()
        file_id = r['id']

        if share:
            self.share_file(file_id)

        return file_id

    def create_file_with_link(self, filename, folder_id=None, share=True):
        file_metadata = {
            'name': filename,
            'parents': [folder_id] if folder_id else []}
        r = self.service.files().create(body=file_metadata, fields='webViewLink, id').execute()

        file_id = r.get('id')
        file_url = r.get("webContentLink")
        if share:
            self.share_file(file_id)

        return file_id, file_url

    def get_urls(self, file_id, folder_id=None, share=True):
        b = self.service.files().get(fileId = file_id, fields='webContentLink').execute()
        return b['webContentLink']

    def share_file(self, file_id):
        self.service.permissions().create(body={'role':'reader', 'type':'anyone'}, fileId = file_id).execute()
