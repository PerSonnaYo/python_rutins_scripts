from config import loger_auot, print_error, DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_TABLE, send_message
import time

def meshok_uved():
    send_message('МЕШОК СУЧАРА')
    time.sleep(2)
    send_message('МЕШОК Не СПАТЬ')

meshok_uved()
# drive = GoogleDrive(gauth)

# my_file = drive.CreateFile({'title': f'{file_name}'})
# my_file.SetContentFile(file_name)
# my_file.Upload()
