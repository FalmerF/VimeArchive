import time
import traceback
import rank_calc


class RankCollector:
    def __init__(self, main_collector) -> None:
        self.main_collector = main_collector
        self.vime = main_collector.vime_archive.vime
        self.status = 'Working'
        self.activeUsers = self.main_collector.vime_archive.activeUsers
        self.users_db = self.main_collector.vime_archive.users_db

        self.check_players_index = 0
        self.players = []
        
        self.main_collector.vime_archive.run_async_thread(self.process_stats_cycle())

    async def process_stats_cycle(self):
        while True:
            try:
                if self.check_players_index >= len(self.activeUsers) or self.vime.limit_remaining <= 50:
                    if self.check_players_index >= len(self.activeUsers):
                        self.check_players_index = 0
                    time.sleep(60)

                user_id = self.activeUsers[self.check_players_index]
                self.check_players_index += 1
                stats = self.vime.get_stats(user_id)
                points = rank_calc.calc_points(stats)
                if await self.users_db.get_async('points', '*', f'id={user_id}') == None:
                    self.users_db.insert_async('points', f'{user_id}, "{points}", ""')
                else:
                    self.users_db.update_async('points', f'points="{points}"', f'id={user_id}')
            except Exception as e:
                self.main_collector.exceptions.append(traceback.format_exc())
                time.sleep(5)

    def get_status(self) -> str:
        return f'{self.status} | index: {self.check_players_index}'