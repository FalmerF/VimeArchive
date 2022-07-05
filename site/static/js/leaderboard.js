var isLoading = false;
var current_top_button = null;
var top_stat_locale = new Map();
var locale = null;
top_stat_locale.set('xp', 'Опыт');
top_stat_locale.set('online', 'Наиграно');
top_stat_locale.set('wins', 'Побед');
top_stat_locale.set('games', 'Игр');

var players = null;
var players_data = null;
var table_body = null;

var filter = '';

var sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay));

window.addEventListener('scroll',(event) => {
	scroll_bottom = document.documentElement.scrollHeight-document.documentElement.scrollTop;
    if(scroll_bottom <= 2000)
    	load_100_users();
});
init();
async function init() {
	response = await fetch("https://api.vimeworld.ru/leaderboard/list");
	var lb_list = json_to_map(await response.json());
	response = await fetch('/api/locale/game_stats,lb_name,games,lb_list');
    locale = json_to_map(await response.json());

	category_place = document.getElementById('category-place');

	var i = 0;
	locale.get('lb_list').forEach(async (value, name) => {
		category = document.createElement('div');
		category.className = 'lb-select-button';
		category.style.cssText = '--i: '+i;
		i++;
		if(name == 'user')
			category.innerHTML = 'Игроки';
		else if(name == 'guild')
			category.innerHTML = 'Гильдии';
		else
			category.innerHTML = locale.get('games').get(name).get('name');

		hover_panel = document.createElement('div');
		hover_panel.className = 'hover-panel';

		type_title = document.createElement('h3');
		type_title.innerHTML = 'За все время';
		hover_panel.append(type_title);

		value.get('main').forEach(async (stat_name, num) => {
			sort_div = document.createElement('div');
			sort_div.className = 'hover-select-button';
			sort_div.innerHTML = locale.get('game_stats').get(name).get(stat_name);
			sort_div.setAttribute('data-tag', name+"/"+stat_name);
			sort_div.setAttribute('data-game', name);
			sort_div.addEventListener('click', on_select_top, false);
			hover_panel.append(sort_div);
		});

		if(value.get('season') != null) {
			type_title = document.createElement('h3');
			type_title.innerHTML = 'За сезон';
			hover_panel.append(type_title);
			value.get('season').forEach(async (stat_name, num) => {
				sort_div = document.createElement('div');
				sort_div.className = 'hover-select-button';
				sort_div.innerHTML = locale.get('game_stats').get(name).get(stat_name);
				if(name == 'prison')
					sort_div.setAttribute('data-tag', name+"_season/"+stat_name);
				else
					sort_div.setAttribute('data-tag', name+"_monthly/"+stat_name);
				sort_div.setAttribute('data-game', name);
				sort_div.addEventListener('click', on_select_top, false);
				hover_panel.append(sort_div);
			});
		}
		if(value.get('daily') != null) {
			type_title = document.createElement('h3');
			type_title.innerHTML = 'За день';
			hover_panel.append(type_title);
			value.get('daily').forEach(async (stat_name, num) => {
				sort_div = document.createElement('div');
				sort_div.className = 'hover-select-button';
				sort_div.innerHTML = locale.get('game_stats').get(name).get(stat_name);
				sort_div.setAttribute('data-tag', name+"_daily/"+stat_name);
				sort_div.setAttribute('data-game', name);
				sort_div.addEventListener('click', on_select_top, false);
				hover_panel.append(sort_div);
			});
		}

		category.append(hover_panel);
		category_place.append(category);
	});
}

function formate_time(time) {
	formated_time = '';
	days = (time-(time%86400))/86400;
	hours = ((time%86400)-(time%3600))/3600;
	minutes = ((time%3600)-(time%60))/60;
	seconds = time%60;

	if(days > 0)
		formated_time += days+'д '
	if(hours > 0)
		formated_time += hours+'ч '
	if(minutes > 0)
		formated_time += minutes+'м '
	if(seconds > 0)
		formated_time += seconds+'с'
	return formated_time
}

function select_top() {
	if(isLoading == true)
		return;
	isLoading = true;
	if(current_top_button != null)
		current_top_button.style.background = '';
	current_top_button = this;
	this.style.background = 'var(--primary-color)';
	top_name = this.getAttribute('data-top');
	load_top(top_name)
}

function create_user_row(num, data) {
	row = document.createElement('tr');
	index = document.createElement('td');
	name_td = document.createElement('td');

	index.innerHTML = num;

	if(data.get('guild') != null) {
		guild = data.get('guild');
		name = guild.get('name');
		color = guild.get('color').replace('&', '');

		user_head = document.createElement('img');
		user_head.className = 'user-head-first';
		user_head.src = guild.get('avatar_url');

		name_span = document.createElement('span');
		name_span.className = 'username';
		name_span.style.color = 'var(--mc-color-'+color+')'
		name_span.innerHTML = name;

		name_href = document.createElement('a');
		name_href.href = '/guild/'+guild.get('id');
		name_href.append(user_head);
		name_href.append(name_span);

		name_td.append(name_href);

		row.append(index);
		row.append(name_td);
	}
	else {
		user = data.get('user');
		username = user.get('username');
		rank = user.get('rank').toLowerCase();

		user_head = document.createElement('img');
		user_head.className = 'user-head-first';
		user_head.src = '//skin.vimeworld.ru/helm/3d/'+username+'.png';

		name_span = document.createElement('span');
		name_span.className = 'username';
		name_span.style.color = 'var(--'+rank+'-rank-color)'
		name_span.innerHTML = username;

		name_href = document.createElement('a');
		name_href.href = 'player/'+username;
		name_href.append(user_head);
		name_href.append(name_span);

		name_td.append(name_href);

		row.append(index);
		row.append(name_td);
	}

	data.forEach(async (value, name) => {
		if(name != 'user' && name != 'guild') {
			td = document.createElement('td')
			td.className = 't-align';
			if(name == 'online')
				td.innerHTML = formate_time(value);
			else
				td.innerHTML = value.toLocaleString(undefined, {});
			row.append(td)
		}
	});

	return row;
}

function on_select_top() {
	tag = this.getAttribute('data-tag');
	game = this.getAttribute('data-game');
	load_top(tag, game);
}

async function load_top(top_name, game_name) {
	document.getElementById('table-title').innerHTML = locale.get('lb_name').get(top_name.split('/')[0]);
	if(top_name.startsWith('user_daily/') || top_name.endsWith('/rank_points')) {
		api_top_name = '';
		if(top_name.endsWith('/rank_points')) {
			api_top_name = game_name.toUpperCase();
			top_name = 'rank_points';
		}
		else {
			api_top_name = top_name.replace('user_daily/', '');
			top_name = api_top_name;
		}

		table_body = document.getElementById('table-body');
		table_body.innerHTML = '';
		players = null;
		try {
			response = await fetch('/api/leaderboard/'+api_top_name);
			players = json_to_map(await response.json());
		} catch(err) {
			isLoading = false;
			send_error_notify('Ошибка сервера! Попробуйте повторить позже или сообщите куда-нибудь.');
		}

		players_list = []
		players.forEach(async (data, num) => {
			players_list.push(data.get('id'));
		});

		response = await fetch("https://api.vimeworld.ru/user/session", {
			method: "POST",
			headers: {'Content-Type': 'application/json'}, 
			body: JSON.stringify(players_list)
		})
		players_data = json_to_map(await response.json());

		if(players_data.get('error') != null) {
			isLoading = false;

			send_error_notify('Воу! Полегче! Не стоит так часто использовать таблицу.');
			return;
		}

		players_tmp = new Map();
		players.forEach(async (value, num) => {
			data = new Map();
			data.set('user', players_data.get(num))
			data.set(top_name, value.get('stat'))
			players_tmp.set(num, data);
		});
		players = players_tmp;

		table_header = document.getElementById('table-header');
		table_header.innerHTML = '<th scope="col">#</th><th scope="col">Имя</th>'
		
		players.get('1').forEach(async (value, name) => {
			if(name != 'user' && name != 'guild') {
				th = document.createElement('th')
				th.className = 't-align';
				th.innerHTML = locale.get('game_stats').get(game_name).get(name);
				table_header.append(th)
			}
		});
		load_100_users();

		isLoading = false;
	}
	else {
		table_body = document.getElementById('table-body');
		table_body.innerHTML = '';
		players = null;

		try {
			response = await fetch('https://api.vimeworld.ru/leaderboard/get/'+top_name+'?size=1000');
			players = json_to_map(await response.json()).get('records');
		} catch(err) {
			isLoading = false;
			send_error_notify('Ошибка сервера! Попробуйте повторить позже или сообщите куда-нибудь.');
		}

		table_header = document.getElementById('table-header');
		table_header.innerHTML = '<th scope="col">#</th><th scope="col">Имя</th>'

		if(top_name == 'user/level') {
			tmp_players = new Map();
			players.forEach(async (value, id) => {
				data = new Map();
				data.set('user', value);
				data.set('level', value.get('level'));
				data.set('online', value.get('playedSeconds'));
				tmp_players.set(id, data);
			});
			players = tmp_players;
		}
		else if(top_name == 'user/online') {
			tmp_players = new Map();
			players.forEach(async (value, id) => {
				data = new Map();
				data.set('user', value);
				data.set('online', value.get('playedSeconds'));
				data.set('level', value.get('level'));
				tmp_players.set(id, data);
			});
			players = tmp_players;
		}
		else if(top_name == 'guild/level') {
			tmp_players = new Map();
			players.forEach(async (value, id) => {
				data = new Map();
				data.set('guild', value);
				data.set('level', value.get('level'));
				data.set('totalCoins', value.get('totalCoins'));
				tmp_players.set(id, data);
			});
			players = tmp_players;
		}
		else if(top_name == 'guild/total_coins') {
			tmp_players = new Map();
			players.forEach(async (value, id) => {
				data = new Map();
				data.set('guild', value);
				data.set('totalCoins', value.get('totalCoins'));
				data.set('level', value.get('level'));
				tmp_players.set(id, data);
			});
			players = tmp_players;
		}
		else if(top_name == 'duels/total_wins') {
			tmp_players = new Map();
			players.forEach(async (value, id) => {
				data = new Map();
				data.set('user', value.get('user'));
				data.set('total_wins', value.get('total_wins'));
				data.set('total_games', value.get('total_games'));
				data.set('maxstrike', value.get('maxstrike'));
				tmp_players.set(id, data);
			});
			players = tmp_players;
		}
		else if(top_name == 'duels/total_games') {
			tmp_players = new Map();
			players.forEach(async (value, id) => {
				data = new Map();
				data.set('user', value.get('user'));
				data.set('total_games', value.get('total_games'));
				data.set('total_wins', value.get('total_wins'));
				data.set('maxstrike', value.get('maxstrike'));
				tmp_players.set(id, data);
			});
			players = tmp_players;
		}
		else if(top_name == 'duels_monthly/rate') {
			tmp_players = new Map();
			players.forEach(async (value, id) => {
				data = new Map();
				data.set('user', value.get('user'));
				data.set('ranked_wins', value.get('ranked_wins'));
				data.set('ranked_games', value.get('ranked_games'));
				data.set('max_rate', value.get('max_rate'));
				tmp_players.set(id, data);
			});
			players = tmp_players;
		}
		else if(top_name == 'duels_monthly/total_wins') {
			tmp_players = new Map();
			players.forEach(async (value, id) => {
				data = new Map();
				data.set('user', value.get('user'));
				data.set('total_wins', value.get('total_wins'));
				data.set('total_games', value.get('total_games'));
				tmp_players.set(id, data);
			});
			players = tmp_players;
		}

		players.get('0').forEach(async (value, name) => {
			if(name != 'user' && name != 'guild') {
				th = document.createElement('th')
				th.className = 't-align';
				th.innerHTML = locale.get('game_stats').get(game_name).get(name);
				table_header.append(th)
			}
		});
		load_100_users();
	}
}

function load_100_users() {
	if(players == null || table_body == null)
		return;
    players_tmp = get_sliced_map();
    var t = 0;
	players_tmp.forEach(async (data, num) => {
		i = parseInt(num, 10)+1;
		row = create_user_row(i, data);
		row.style.cssText = "--i: "+t;
		t++;
		table_body.append(row);
	});
}

function set_filter(input) {
	filter = input.value.replaceAll(' ', '').toLowerCase();
	document.getElementById('table-body').innerHTML = '';
	load_100_users();
}

function get_sliced_map() {
	players_tmp = new Map();
	if(filter != '') {
		players.forEach(async (data, num) => {
			if(data.get('guild') != null && data.get('guild').get('name').toLowerCase().includes(filter)) {
				players_tmp.set(num, data);
			}
			else if(data.get('user') != null && data.get('user').get('username').toLowerCase().includes(filter)) {
				players_tmp.set(num, data);
			}
		});
	}
	else {
		players_tmp = players;
	}

	count = table_body.childNodes.length;
	if(count >= players_tmp.length)
		return new Map();
	arrayTmp = Array.from(players_tmp).slice(count, count+100);
    players_tmp = new Map(arrayTmp);
    return players_tmp;
}