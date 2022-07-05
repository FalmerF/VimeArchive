def get_rank_by_index(index) -> str:
    if index >= 0 and index <= 9: return 'pearl'
    elif index >= 10 and index <= 34: return 'emerald'
    elif index >= 35 and index <= 99: return 'diamond'
    elif index >= 100 and index <= 299: return 'gold'
    elif index >= 300 and index <= 499: return 'iron'
    return 'none'

def calc_points(stats) -> dict:
    ranks = {}
    for stat in stats:
        points = 0
        stat_data = stats[stat]['global']
        try:
            points = globals()[f'calc_{stat.lower()}'](stat_data)
        except:
            pass

        ranks[stat] = (int)(points)
    return ranks

def calc_ann(stat_data) -> int:
    kills_p = stat_data['kills']
    bowkills_p = stat_data['bowkills']*2
    nexsus_p = stat_data['nexus']*2
    points = kills_p+bowkills_p+nexsus_p
    return (int)(points)

def calc_bb(stat_data) -> int:
    games = stat_data['games']
    wins = stat_data['wins']
    wins_p = wins
    points = wins_p*(wins/games)
    return (int)(points)

def calc_bp(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    wins_p = wins
    points = wins_p*(wins/games)
    return (int)(points)

def calc_bridge(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    deaths = stat_data['deaths']
    wins_p = wins*2
    kills_p = kills
    points_p = stat_data['points']
    points = (wins_p+points_p)*(wins/games)+kills_p*(kills/deaths)
    return (int)(points)

def calc_luckywars(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    deaths = stat_data['deaths']
    wins_p = wins*2
    kills_p = kills
    points = wins_p*(wins/games)+kills_p*(kills/deaths)
    return (int)(points)

def calc_bw(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    deaths = stat_data['deaths']
    bedBreaked_p = stat_data['bedBreaked']*2
    wins_p = wins*2
    kills_p = kills
    points = (wins_p+bedBreaked_p)*(wins/games)+kills_p*(kills/deaths)
    return (int)(points)

def calc_bwt(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    deaths = stat_data['deaths']
    bedBreaked_p = stat_data['bedBreaked']*2
    wins_p = wins*2
    kills_p = kills
    points = (wins_p+bedBreaked_p)*(wins/games)+kills_p*(kills/deaths)
    return (int)(points)

def calc_cp(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    deaths = stat_data['deaths']
    resourcePointsBreaked_p = stat_data['resourcePointsBreaked']*2
    wins_p = wins*2
    kills_p = kills
    points = (wins_p+resourcePointsBreaked_p)*(wins/games)+kills_p*(kills/deaths)
    return (int)(points)

def calc_dr(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    wins_p = wins
    points = wins_p*(wins/games)
    return (int)(points)

def calc_duels(stat_data) -> int:
    solo_wins = stat_data['solo_wins']
    solo_games = max(stat_data['solo_games'], 1)
    team_wins = stat_data['team_wins']
    team_games = max(stat_data['team_games'], 1)
    ranked_wins = stat_data['ranked_wins']
    ranked_games = max(stat_data['ranked_games'], 1)
    points = solo_wins*(solo_wins/solo_games)+team_wins*(team_wins/team_games)+ranked_wins*(ranked_wins/ranked_games)
    return (int)(points)

def calc_gg(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    wins_p = wins*3
    points = (wins_p+kills)*(wins/games)
    return (int)(points)

def calc_hg(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    wins_p = wins*3
    points = (wins_p+kills)*(wins/games)
    return (int)(points)

def calc_kpvp(stat_data) -> int:
    kills = stat_data['kills']
    deaths = stat_data['deaths']
    game_points = stat_data['points']
    points = (game_points+kills)*(kills/deaths)
    return (int)(points)

def calc_mw(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    wins_p = wins
    points = wins_p*(wins/games)
    return (int)(points)

def calc_prison(stat_data) -> int:
    total_blocks = stat_data['total_blocks']
    kills = stat_data['kills']
    deaths = stat_data['deaths']
    mobs = stat_data['mobs']
    points = kills*(kills/deaths)+(total_blocks/10)+(mobs/2)
    return (int)(points)

def calc_sw(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    deaths = stat_data['deaths']
    wins_p = wins*2
    kills_p = kills
    points = wins_p*(wins/games)+kills_p*(kills/deaths)
    return (int)(points)

def calc_arc(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    deaths = stat_data['deaths']
    wins_p = wins*2
    kills_p = kills
    points = wins_p*(wins/games)+kills_p*(kills/deaths)
    return (int)(points)

def calc_jumpleague(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    deaths = stat_data['deaths']
    checkpoints = stat_data['checkpoints']
    wins_p = wins*2
    kills_p = kills
    points = (wins_p+checkpoints)*(wins/games)+kills_p*(kills/deaths)
    return (int)(points)

def calc_murder(stat_data) -> int:
    games = stat_data['games']
    total_wins = stat_data['total_wins']
    wins_as_innocent_p = stat_data['wins_as_innocent']
    wins_as_maniac_p = stat_data['wins_as_maniac']*2
    wins_as_detective_p = stat_data['wins_as_detective']*2
    kills = stat_data['kills']
    points = (wins_as_innocent_p+wins_as_maniac_p+wins_as_detective_p)/(total_wins/games)+kills
    return (int)(points)

def calc_sheep(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    deaths = stat_data['deaths']
    wins_p = wins*2
    kills_p = kills
    points = wins_p*(wins/games)+kills_p*(kills/deaths)
    return (int)(points)

def calc_turfwars(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    deaths = stat_data['deaths']
    wins_p = wins*2
    kills_p = kills
    points = wins_p*(wins/games)+kills_p*(kills/deaths)
    return (int)(points)

def calc_tnttag(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    wins_p = wins*2
    points = (wins_p+kills)*(wins/games)
    return (int)(points)

def calc_tntrun(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    wins_p = wins
    points = wins_p*(wins/games)
    return (int)(points)

def calc_zombieclaus(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    wins_p = wins*2
    points = (wins_p+kills)*(wins/games)
    return (int)(points)

def calc_hide(stat_data) -> int:
    wins = stat_data['total_wins']
    games = stat_data['games']
    kills = stat_data['kills']
    wins_p = wins*2
    points = (wins_p+kills)*(wins/games)
    return (int)(points)

def calc_speedbuilders(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    wins_p = wins
    points = wins_p*(wins/games)
    return (int)(points)

def calc_fallguys(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    wins_p = wins
    points = wins_p*(wins/games)
    return (int)(points)

def calc_teamfortress(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    deaths = stat_data['deaths']
    wins_p = wins*2
    kills_p = kills
    points = wins_p*(wins/games)+kills_p*(kills/deaths)
    return (int)(points)

def calc_eggwars(stat_data) -> int:
    wins = stat_data['wins']
    games = stat_data['games']
    kills = stat_data['kills']
    deaths = stat_data['deaths']
    wins_p = wins*2
    kills_p = kills
    points = wins_p*(wins/games)+kills_p*(kills/deaths)
    return (int)(points)