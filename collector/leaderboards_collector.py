import ast
import asyncio
import time
import traceback
import rank_calc
from data_base import DataBase
from datetime import datetime


class LeaderboardsCollector:
    def __init__(self, main_collector) -> None:
        self.main_collector = main_collector
        self.vime = main_collector.vime_archive.vime
        self.status = 'Starting'
        self.status_update = 'Starting'

        self.main_collector.vime_archive.run_async_thread(self.check_leaderboards())
        self.main_collector.vime_archive.run_async_thread(self.update_user_lb_cycle())

    async def check_leaderboards(self):
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
        self.users_lb_db = DataBase('', file_name='user_lb.db')
        await self.load_user_lb_data(self.user_lb_data, self.users_lb_db)
        date = datetime.now()

        while True:
            try:
                self.status_update = 'Updating Leaderboards'
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
                self.save_user_lb_data(self.users_lb_db, lb_data_copy, xp_top, online_top, wins_top, games_top)

                await self.calc_users_rank()
            except Exception as e:
                self.main_collector.exceptions.append(traceback.format_exc())
                self.status_update = 'Waiting'
                time.sleep(10)
            self.status_update = 'Waiting'
            time.sleep(1800)

    async def calc_users_rank(self):
        self.status_update = 'Calculating ranks'
        users_points = await self.main_collector.vime_archive.users_db.get_async('points', 'id, points', type='all')
        data = {}
        for user in users_points:
            user_id = user[0]
            points = ast.literal_eval(user[1])
            for game in points:
                if game not in data: data[game] = {}
                data[game][user_id] = points[game]

        data_players_list = {}
        for game in data:
            data[game] = dict(sorted(data[game].items(), key=lambda item: item[1], reverse=True))
            data_players_list[game] = list(data[game].keys())

        set_data_pattern = 'rank= CASE {0} END'
        case_pattern = 'WHEN id={0} THEN "{1}" '
        condition_pattern = 'id IN ({0})'
        condition_el_pattern = '{0},'

        i = 0
        self.status_update = f'Saving player #{i}'
        set_data = ''
        condition_data = '' 
        for user in users_points:
            try:
                user_id = user[0]
                ranks = {}
                for game in data:
                    index = data_players_list[game].index(user_id)
                    rank = rank_calc.get_rank_by_index(index)
                    ranks[game] = rank
                set_data += case_pattern.format(user_id, ranks)
                condition_data += condition_el_pattern.format(user_id)
                self.status_update = f'Saving player #{i}'
                i += 1
            except ValueError:
                pass
        
        self.main_collector.vime_archive.users_db.update_async('points', set_data_pattern.format(set_data),
         condition_pattern.format(condition_data[:-2]))

        for game in data:
            self.status_update = f'Saving {game}_top'
            if len(await self.users_lb_db.request_command(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{game}_top';")) == 0:
                self.users_lb_db.execute_command(f'CREATE TABLE {game}_top (user_id INTEGER, stat INTEGER);')
            
            table = data_players_list[game]
            table = table[:500]

            self.users_lb_db.delete_async(f'{game}_top')
            for user_id in table:
                self.users_lb_db.insert_async(f'{game}_top', f'{user_id}, {data[game][user_id]}')


    async def load_user_lb_data(self, user_lb_data, db):
        data = await db.get_async('daily_activity', '*', type='all')
        if data is None: return
        for d in data:
            user_lb_data[d[0]] = ast.literal_eval(d[1])

    def save_user_lb_data(self, db, user_lb_data, xp_top, online_top, wins_top, games_top):
        self.status_update = 'Saving Leaderboards'
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
        return f'{self.status} | {self.status_update}'