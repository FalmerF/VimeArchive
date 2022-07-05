import ast
import asyncio
import threading
import time
from datetime import datetime, timedelta
from collector.main_collector import MainCollector
from data_base import DataBase
from keys import VIME_TEST_TOKEN
from keys import VIME_TOKEN, VIME_TEST_TOKEN
from utils import cls
from vime_api.vime import Vime


TEST_MODE = False

if TEST_MODE: 
	VIME_TOKEN = VIME_TEST_TOKEN

CONFIG_FILE = 'config.cfg'

class VimeArchive:
    def __init__(self) -> None:
        self.vime = Vime(VIME_TOKEN)
        self.load_config()
        self.make_db()
        self.load_locale()
        self.log_list = []
        self.threads = []

        self.main_collector = MainCollector(self, self.db, self.db_p)
        self.run_async_thread(self.log_cycle())

    async def log_cycle(self):
        while True:
            print_text = f'Threads'
            print_text += f'\n    Count: {len(self.threads)}'
            print_text += f'\nCollectors'
            print_text += f'\n    Main Collector:          {self.main_collector.get_status()}'
            print_text += f'\n    Matches Collector:       {self.main_collector.matches_collector.get_status()}'
            print_text += f'\n    Leaderboards Collector:  {self.main_collector.lb_collector.get_status()}'
            print_text += f'\n    Players Collector:       {self.main_collector.players_collector.get_status()}'
            print_text += f'\n    Rank Collector:          {self.main_collector.rank_collector.get_status()}'
            print_text += f'\nVime'
            print_text += f'\n    Limit Remaining: {self.vime.limit_remaining}'
            print_text += f'\nDataBase users.db'
            print_text += f'\n    Update:  {len(self.users_db.update_list)}'
            print_text += f'\n    Insert:  {len(self.users_db.insert_list)}'
            print_text += f'\n    Delete:  {len(self.users_db.delete_list)}'
            print_text += f'\n    Get:     {len(self.users_db.get_dict)}'
            print_text += '\nLogs'
            for m in self.log_list:
                print_text += f'\n    {m}'
            print_text += '\nExceptions'
            for e in self.main_collector.exceptions:
                print_text += f'\n{e}'
            cls()
            print(print_text)
            time.sleep(1)

    def load_config(self):
        self.activeUsers = []
        self.last_match_id = 0
        try:
            f = open(CONFIG_FILE, 'r', encoding='utf-8')
            data = f.read()
            config = {}
            if data != '':
                config = ast.literal_eval(data)
            try:
                self.last_match_id = config['last_match_id']
            except:
                self.last_match_id = None
            try:
                self.activeUsers = config['active_users']
            except:
                self.activeUsers = []
            f.close()
        except FileNotFoundError:
            open(CONFIG_FILE, 'a', encoding='utf-8')

    def save_config(self):
        open(CONFIG_FILE, 'a', encoding='utf-8')
        f = open(CONFIG_FILE, 'w', encoding='utf-8')
        f.write(str({'last_match_id': self.main_collector.matches_collector.last_match_id, 'active_users': self.main_collector.players_collector.activeUsers}))
        f.close()

    def make_db(self):
        date = datetime.now()
        self.db = DataBase(f'{date.day}.{date.month}.{date.year}')
        date_p = datetime.now() - timedelta(days=1)
        self.db_p = DataBase(f'{date_p.day}.{date_p.month}.{date_p.year}')
        self.users_db = DataBase(date='', file_name='users.db')

    def load_locale(self):
        f = open('locale.txt', 'r', encoding='utf-8')
        self.locale = ast.literal_eval(f.read())
        f.close()

    def log(self, message: str):
        self.log_list.append(message)

    def run_async_thread(self, target):
        thread = threading.Thread(target=self.run_async, args=[target])
        self.threads.append(thread)
        thread.start()

    def run_async(self, target):
        asyncio.run(target)

vime_archive = VimeArchive()