
class MatchesCollector:
    def __init__(self, main_collector) -> None:
        self.checked_matches = []
        self.main_collector = main_collector
        self.last_match_id = main_collector.vime_archive.last_match_id
        self.vime = main_collector.vime_archive.vime
        self.status = 'Starting'
        self.last_matches_count = 0

    def check_matches(self) -> None:
        self.last_matches_count = 0
        if self.vime.limit_remaining <= 0: return
        matches = []
        self.status = 'Getting Matches'
        if self.last_match_id is None or self.last_match_id == 0:
            matches = self.vime.get_latest_match(count=100)
        else:
            try:
                matches = self.vime.get_match_list(after=self.last_match_id, count=100)
            except:
                self.last_match_id = None
        self.status = 'Processing Matches'
        for m in matches:
            if self.vime.limit_remaining <= 0: return
            if m.id in self.checked_matches:	continue
            match = m.get_fullmatch(self.vime)
            self.checked_matches.append(m.id)
            if len(self.checked_matches) > 200:	self.checked_matches.pop(0)

            if match.game == 'SWT': match.game = 'SW'
            if match.game == 'BWH': match.game = 'BW'
            if match.game == 'HGL': match.game = 'HG'
            for p in match.players:
                player_id = p['id']
                match_action = self.make_match_stats_for_player(match, p)
                match_action['match']['id'] = m.id
                self.main_collector.db.insert_async('actions', f'{player_id}, {match.end}, "{match_action}"')

                self.main_collector.lb_collector.add_user_lb_stat(player_id, 'games', 1)
                wins = match_action['match']['wins']
                if wins > 0: self.main_collector.lb_collector.add_user_lb_stat(player_id, 'wins', wins)

                if not player_id in self.main_collector.players_collector.activeUsers:
                    self.main_collector.players_collector.activeUsers.append(player_id)

            self.last_match_id = m.id
            self.last_matches_count += 1
            if self.vime.limit_remaining <= 0: break

        self.status = 'Waiting'

    def make_match_stats_for_player(self, match, player_data) -> dict:
        player_id = player_data['id']
        match_action = {}
        match_action['match'] = {}
        match_action['match']['game'] = match.game
        match_action['match']['wins'] = (1) if player_id in match.win_players else (0)
        is_win = player_id in match.win_players

        if match.game == 'BW':
            match_action['match']['kills'] = player_data['kills']
            match_action['match']['bedBreaked'] = player_data['brokenBeds']
        elif match.game == 'CP':
            match_action['match']['kills'] = player_data['kills']
            match_action['match']['resourcePointsBreaked'] = player_data['rpBroken']
        elif match.game == 'DUELS':
            match_action['match']['winStreak'] = player_data['winStreak']
        elif match.game == 'HG':
            match_action['match']['kills'] = player_data['kills']
            if 'luckyBlocks' in player_data:
                match_action['match']['luckyBlocks'] = player_data['luckyBlocks']
        elif match.game == 'SW':
            match_action['match']['kills'] = (player_data['kills']) if 'kills' in player_data else (0)
        elif match.game == 'MURDER':
            match_action['match']['kills'] = (player_data['kills']) if 'kills' in player_data else (0)
            match_action['match']['wins_as_innocent'] = (1) if is_win and player_data['role'] == 'innocent' else (0)
            match_action['match']['wins_as_maniac'] = (1) if is_win and player_data['role'] == 'maniac' else (0)
            match_action['match']['wins_as_detective'] = (1) if is_win and player_data['role'] == 'detective' else (0)
        else:
            for key in player_data.keys():
                if key != 'id':
                    match_action['match'][key] = player_data[key]
        return match_action

    def get_status(self) -> str:
        return f'{self.status} | Checked Matches: {self.last_matches_count}'