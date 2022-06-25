import math
from datetime import datetime, timedelta
from utils import get_xp_for_lvl


class PlayersCollector:
    def __init__(self, main_collector) -> None:
        self.main_collector = main_collector
        self.vime = main_collector.vime_archive.vime
        self.status = 'Starting'

        self.check_players_index = 0
        self.users_list = []
        self.activeUsers = self.main_collector.vime_archive.activeUsers
        self.last_users = {}

    def get_active_players(self):
        users = []
        self.status = 'Getting Players'
        while self.vime.limit_remaining > 100:
            n = self.check_players_index + 50
            while self.check_players_index < n and self.check_players_index < len(self.activeUsers):
                users.append(self.activeUsers[self.check_players_index])
                self.check_players_index += 1
            if self.check_players_index >= len(self.activeUsers):
                self.check_players_index = 0
                break
            elif len(users) >= 1000 or math.ceil(len(users)/50.0) == self.vime.limit_remaining:
                data = self.vime.get_sessions(users)
                self.users_list.extend(data)
                users.clear()
            elif math.ceil(len(users)/50.0) > self.vime.limit_remaining:
                self.check_players_index -= len(users)
                return

        if len(users) > 0:
            data = self.vime.get_sessions(users)
            self.users_list.extend(data)

    def check_active_players(self):
        self.status = 'Processing Players'
        for user in self.users_list:
            lastUser = (self.last_users[user.id]) if user.id in self.last_users else (None)
            actions = {}
            level = user.level
            levelPercentage = user.levelPercentage
            rank = user.rank
            if lastUser is not None:
                if level != lastUser.level:
                    xpDif = 0
                    lvl = lastUser.level+1
                    xpDif = (1-lastUser.levelPercentage)*get_xp_for_lvl(lastUser.level)
                    while lvl < level:
                        xpDif += get_xp_for_lvl(lastUser.level)
                        lvl += 1
                    xpDif += levelPercentage*get_xp_for_lvl(lastUser.level)
                    actions['xp'] = int(xpDif)
                    actions['level'] = level - lastUser.level
                elif levelPercentage != lastUser.levelPercentage:
                    xpDif = (levelPercentage-lastUser.levelPercentage)*get_xp_for_lvl(user.level)
                    actions['xp'] = int(xpDif)
                    self.main_collector.lb_collector.add_user_lb_stat(user.id, 'xp', actions['xp'])
                if rank != lastUser.rank:
                    actions['rank'] = rank
                dif = user.playedSeconds - lastUser.playedSeconds
                if dif > 0:
                    date = datetime.now()
                    seconds_in_day = date.hour*3600+date.minute*60+date.second

                    if dif > seconds_in_day:
                        dif_p_day = dif-seconds_in_day
                        dif = seconds_in_day

                        date = date - timedelta(days=1)
                        date = date.replace(hour=23, minute=59, second=59)
                        p_adction = {'playedSeconds': dif_p_day}
                        self.main_collector.db_p.insert_async('actions', f'{user.id}, "{date}", "{p_adction}"')

                    actions['playedSeconds'] = dif
                    self.main_collector.lb_collector.add_user_lb_stat(user.id, 'online', actions['playedSeconds'])
            self.last_users[user.id] = user

            if len(actions.keys()) > 0:
                self.main_collector.db.insert_async('actions', f'{user.id}, {int(datetime.now().timestamp())}, "{actions}"')

            if datetime.now().timestamp() - user.lastSeen > 604800 and user.id in self.activeUsers:
                self.activeUsers.remove(user.id)
        self.status = 'Waiting'

    def get_status(self) -> str:
        return f'{self.status} | Users: {len(self.activeUsers)} | index: {self.check_players_index}'