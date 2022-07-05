import time
import traceback
from datetime import datetime
from collector.leaderboards_collector import LeaderboardsCollector
from collector.matches_collector import MatchesCollector
from collector.players_collector import PlayersCollector
from collector.rank_collector import RankCollector

class MainCollector:
    def __init__(self, vime_archive, db, db_p) -> None:
        self.db = db
        self.db_p = db_p
        self.vime_archive = vime_archive
        self.date = datetime.now()
        self.status = 'Starting...'
        self.waiting_time = 0

        self.exceptions = []

        self.lb_collector = LeaderboardsCollector(self)
        self.matches_collector = MatchesCollector(self)
        self.players_collector = PlayersCollector(self)

        self.rank_collector = RankCollector(self)

        self.vime_archive.run_async_thread(self.collect_cycle())

    async def collect_cycle(self) -> None:
        while True:
            try:
                self.pre_cycle()
                self.status = 'Processing Matches Collector'
                self.matches_collector.check_matches()
                self.status = 'Processing Players Collector'
                self.players_collector.get_active_players()
                self.players_collector.check_active_players()
                self.status = 'Saving Config'
                self.vime_archive.save_config()
            except Exception as e:
                self.exceptions.append(traceback.format_exc())

            dif = (datetime.now()-self.cycle_start_time).total_seconds()
            self.waiting_time = 60 - dif
            while self.waiting_time > 0:
                self.status = f'Waiting {(int)(self.waiting_time)}s'
                time.sleep(1)
                self.waiting_time -= 1

    def pre_cycle(self) -> None:
        self.status = 'Pre Cycle'
        self.cycle_start_time = datetime.now()
        self.users_list = []
        if self.date.day != datetime.now().day:
            self.date = datetime.now()

    def get_status(self) -> str:
        return self.status
