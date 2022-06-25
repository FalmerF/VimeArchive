import ast
import asyncio
from datetime import datetime, timedelta
import threading
import time
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

        self.main_collector = MainCollector(self, self.db, self.db_p)
        threading.Thread(target=self.run_log).start()

    def run_log(self) -> None:
        asyncio.run(self.log_cycle())

    async def log_cycle(self):
        while True:
            cls()

            print('Collectors')
            print(f'    Main Collector: {self.main_collector.get_status()}')
            print(f'    Matches Collector: {self.main_collector.matches_collector.get_status()}')
            print(f'    Leaderboards Collector: {self.main_collector.lb_collector.get_status()}')
            print(f'    Players Collector: {self.main_collector.players_collector.get_status()}')
            print(f'Vime')
            print(f'    Limit Remaining: {self.vime.limit_remaining}')
            print('Exceptions')
            for e in self.main_collector.exceptions:
                print(e)

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

    def load_locale(self):
        f = open('locale.txt', 'r', encoding='utf-8')
        self.locale = ast.literal_eval(f.read())
        f.close()

vime_archive = VimeArchive()