import ast
import asyncio
import threading
import time
import traceback
from data_base import DataBase
from datetime import datetime


class LeaderboardsCollector:
    def __init__(self, main_collector) -> None:
        self.main_collector = main_collector
        self.vime = main_collector.vime_archive.vime
        self.status = 'Starting'

        threading.Thread(target=self.run).start()
        threading.Thread(target=self.run_update_custom_lb).start()

    def run(self) -> None:
        asyncio.run(self.check_leaderboards())

    def run_update_custom_lb(self) -> None:
        asyncio.run(self.update_user_lb_cycle())

    def check_leaderboards(self):
        last_leaderboards = {}

        while True:
            try:
                self.status = 'Getting Leaderboards'
                leaderboard_list = self.vime.get_leaderboard_list()
                self.status = 'Processing Leaderboards'
                for leaderboard_data in leaderboard_list:
                    table_type = leaderboard_data['type']
                    table_sorts = leaderboard_data['sort']
                    if table_type == 'guild': continue
                    for sort in table_sorts:
                        name = f'{table_type}_{sort}'
                        while self.vime.limit_remaining <= 10:
                            time.sleep(1)
                        leaderboard = self.vime.get_leaderboard(lb_type=table_type, sort=sort, size=1000)
                        users_list = []
                        for player in leaderboard['records']:
                            user_id = (player['user']['id']) if 'user' in player else (player['id'])
                            users_list.append(user_id)

                        last_users_list = (last_leaderboards[name]) if name in last_leaderboards else (None)
                        last_leaderboards[name] = users_list
                        if last_users_list is None: 
                            continue

                        for user_id in users_list:
                            last_index = 1000 
                            index = users_list.index(user_id)
                            try:
                                last_index = last_users_list.index(user_id)
                            except:
                                pass
                            diff = last_index-index
                            if diff == 0: continue
                            actions = {'leaderboard': {'type': table_type, 'sort': sort, 'diff': diff, 'place': (index+1)}}
                            self.main_collector.db.insert_async('actions', f'{user_id}, {int(datetime.now().timestamp())}, "{actions}"')

                        for user_id in last_users_list:
                            if not user_id in users_list:
                                last_index = last_users_list.index(user_id) 
                                index = 1000
                                diff = last_index-index
                                if diff == 0: continue
                                actions = {'leaderboard': {'type': table_type, 'sort': sort, 'diff': diff, 'place': '>1000'}}
                                self.main_collector.db.insert_async('actions', f'{user_id}, {int(datetime.now().timestamp())}, "{actions}"')
                self.status = 'Waiting'
                time.sleep(1800)
            except Exception as e:
                self.status = 'Waiting'
                time.sleep(10)

    async def update_user_lb_cycle(self):
        self.user_lb_data = {}
        await asyncio.sleep(1)
        db = DataBase('', file_name='user_lb.db')
        await self.load_user_lb_data(self.user_lb_data, db)
        date = datetime.now()

        while True:
            try:
                xp_top = {}
                online_top = {}
                wins_top = {}
                games_top = {}
                if date.day != datetime.now().day:
                    date = datetime.now()
                    self.user_lb_data = {}

                lb_data_copy = self.user_lb_data.copy()
                for user in lb_data_copy:
                    xp_top[user] = lb_data_copy[user]['xp']
                    online_top[user] = lb_data_copy[user]['online']
                    wins_top[user] = lb_data_copy[user]['wins']
                    games_top[user] = lb_data_copy[user]['games']

                xp_top = dict(sorted(xp_top.items(), key=lambda item: item[1], reverse=True))
                online_top = dict(sorted(online_top.items(), key=lambda item: item[1], reverse=True))
                wins_top = dict(sorted(wins_top.items(), key=lambda item: item[1], reverse=True))
                games_top = dict(sorted(games_top.items(), key=lambda item: item[1], reverse=True))
                self.save_user_lb_data(db, lb_data_copy, xp_top, online_top, wins_top, games_top)
            except Exception as e:
                self.main_collector.exceptions.append(traceback.format_exc())
                time.sleep(10)
            time.sleep(600)

    async def load_user_lb_data(self, user_lb_data, db):
        data = await db.get_async('daily_activity', '*', type='all')
        if data is None: return
        for d in data:
            user_lb_data[d[0]] = ast.literal_eval(d[1])

    def save_user_lb_data(self, db, user_lb_data, xp_top, online_top, wins_top, games_top):
        db.delete_async('daily_activity')
        db.delete_async('xp_top')
        db.delete_async('online_top')
        db.delete_async('wins_top')
        db.delete_async('games_top')
        for i in range(1000):
            n = i
            if len(xp_top) > n:
                db.insert_async('xp_top', f'{list(xp_top.keys())[n]}, {list(xp_top.values())[n]}')
            if len(online_top) > n:
                db.insert_async('online_top', f'{list(online_top.keys())[n]}, {list(online_top.values())[n]}')
            if len(wins_top) > n:
                db.insert_async('wins_top', f'{list(wins_top.keys())[n]}, {list(wins_top.values())[n]}')
            if len(games_top) > n:
                db.insert_async('games_top', f'{list(games_top.keys())[n]}, {list(games_top.values())[n]}')
        for user in user_lb_data:
            db.insert_async('daily_activity', f'{user}, "{user_lb_data[user]}"')

    def add_user_lb_stat(self, user_id: int, stat_name: str, count: int):
        if user_id not in self.user_lb_data:
            self.user_lb_data[user_id] = {'xp': 0, 'online': 0, 'wins': 0, 'games': 0}
            
        self.user_lb_data[user_id][stat_name] += count

    def get_status(self) -> str:
        return self.status