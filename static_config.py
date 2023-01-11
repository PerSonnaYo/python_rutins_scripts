import os

# Файл static_config отделён от config.py во избежаание конфликта с util.py
# Конфликтная ситуация: config.py <-> util.py (взаимозависимость)
# Текущая ситуация:
# util <- config.py
#  |         V
#  |----> static_config.py

# SOFT CONSTANTS
# Включить/выключить тестирование в vk_interface
# (работает при перемещении фотографий)
vk_testing_mode = False

# Задержка перед запуском команды с помощью /force
telegram_cron_forced_run_delay = 60
# задержка перед тем, как активировать job после того, как он был отложен.
# Также данной переменной равно минимальное время на которое можно отложить job.
telegram_cron_postpone_activation_delay = 10
# Время, на которое будет отложен job,
# если команда /postpone запущена без указания времени
telegram_cron_quick_postpone_time = 60*10
telegram_enable_proxy = False
telegram_proxy_url = 'socks5://127.0.0.1:9050/'
telegram_logging_period = 60*10

# Не выкладывать лоты на lave.ru
# а сохранять предварительные просмотры тредов с ними
lave_poster_preview_mode = False

# Сохранять этапы работы phpbb_interface в виде html файлов
phpbb_save_requests_mode = True
#temp_folder_name = r"C:\Users\flman\Google Диск\Импорт1\temp"
#output_folder_name = r"C:\Users\flman\Google Диск\Импорт1\output"
#logs_folder_name = r"C:\Users\flman\Google Диск\Импорт1\temp/log"
#temp_folder_name = r"G:\My Drive\Импорт1\temp"
#output_folder_name = r"G:\My Drive\Импорт1\output"
#logs_folder_name = r"G:\My Drive\Импорт1\temp/log"

temp_folder_name = r"/mnt/c/Users/Administrator/dags/scripts/temp"
temp_gdrive_folder_name = temp_folder_name# r"/mnt/g/Мой диск/Импорт1/temp"
output_folder_name = r"/mnt/c/Users/Administrator/dags/scripts/output"
logs_folder_name = r"/mnt/c/Users/Administrator/dags/scripts/temp/logs"
files_folder_name = r"/mnt/c/Users/Administrator/dags/scripts/additions"
dags_folder_name = r"/mnt/c/Users/Administrator/dags"
scripts_folder_name = r"/mnt/c/Users/Administrator/dags/scripts"
vk_comment_env_name = r"/mnt/c/Users/Administrator/venvs/vk_comments/bin/python" 
django_manage_name = r"/mnt/c/Users/Administrator/dags/avito/manage.py"
sites_env_name = r"/mnt/c/Users/Administrator/venvs/sites_r/bin/python"
psql_folder_name = r"/mnt/c/program files/postgresql/14/data"
airflow_folder_name = r"/root/airflow-data"
# Использовать базовый конфиг для bigjpg
# (небазовый конфиг не доступен без премиума)
bigjpg_base_conf = False

# other preparations
if not os.path.exists(f'{temp_folder_name}'):
    os.makedirs(f'{temp_folder_name}')

if not os.path.exists(f'{output_folder_name}'):
    os.makedirs(f'{output_folder_name}')

if not os.path.exists(f'{logs_folder_name}'):
    os.makedirs(f'{logs_folder_name}')

if not os.path.exists(f'{files_folder_name}'):
    os.makedirs(f'{files_folder_name}')

testing_mode = False
meshok_ignore_mode = False
if testing_mode:
    telegram_enable_proxy = True
    telegram_cron_forced_run_delay = 1
    vk_testing_mode = True
    lave_poster_preview_mode = True
    bigjpg_base_conf = True
