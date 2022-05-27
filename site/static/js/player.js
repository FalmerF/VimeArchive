var user_id = 0;
var locale = null;
var filter_list = new Map();
var can_change_filter = true;
var stat_elements_count = 0;
var leaderboard_list = new Map();
var lb_sort_locale = new Map();
var load_delay = 10;
var header_selected_button = null;
var blocks_locale = new Map();
var actions = null;
async function init() {
	response = await fetch("https://api.vimeworld.ru/user/name/"+username);
	var player_data = json_to_map(await response.json());
	response = await fetch('/api/locale');
    locale = json_to_map(await response.json());
    response = await fetch("https://api.vimeworld.ru/leaderboard/list");
	lb_list = json_to_map(await response.json());
	lb_list.forEach(async (value) => {
		value.set('description', value.get('description').replace('(в этом месяце)', '(за сезон)'));
		leaderboard_list.set(value.get('type'), value);
	});
	make_lb_sort_locale();
	make_blocks_locale();
	response = await fetch("/api/black_list");
	black_list = json_to_map(await response.json()).get('ids');

    var player = null;
    if (player_data.get('error') != null || player_data.size == 0) {
    	document.getElementById("not-found").style.visibility = "unset";
    	document.getElementById("select-hint").style.visibility = 'hidden';
    	document.getElementById('stats-div').style.visibility = 'hidden';
    	return;
    }
    else
    	player = player_data.get('0');

    if(Array.from(black_list.values()).includes(player.get('id'))) {
    	document.getElementById("black-list").style.visibility = "unset";
    	document.getElementById("select-hint").style.visibility = 'hidden';
    	document.getElementById('stats-div').style.visibility = 'hidden';
    	return;
    }

    response = await fetch("https://api.vimeworld.ru/user/"+player.get('id')+"/session");
	var session = json_to_map(await response.json()).get('online');

	username = player.get('username');
	user_id = player.get('id');
	var rank = player.get('rank').toLowerCase();
	var rank_name = locale.get('ranks').get(rank).get('name');

	player_status = document.getElementById("player-status");
	player_status.innerHTML = session.get('message');
	if(session.get('value') == true)
		player_status.style.color = 'var(--green-color-s)';
	else {
		player_status.style.color = 'var(--red-color-s)';
		offline_time = Math.floor(new Date().getTime()/1000)-player.get('lastSeen');
		player_status.innerHTML = 'Оффлайн '+formate_time(offline_time);
		tooltip = document.createElement('span');
		tooltip.className = 'status-tooltip';
		tooltip.innerHTML = new Date(player.get('lastSeen') * 1000).toLocaleDateString("ru-RU", {year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric'});
		player_status.append(tooltip);
	}

	formated_percent = Math.round(player.get('levelPercentage')*100);
	xp_to_level = 8000+(player.get('level')*2000);

	document.getElementById("user-head-first").src = "https://skin.vimeworld.ru/head/"+username+".png";
	document.getElementById("user-head-second").style.backgroundImage = "url('https://skin.vimeworld.ru/raw/skin/"+username+".png')";
	document.getElementById("card-title-top").innerHTML = username + ' [<span id="rank-text" style="color: var(--'+rank+'-rank-color);">'+rank_name+'</span>]';
	document.getElementById("card-title-id").innerHTML = "ID: "+user_id;
	document.getElementById("xp-level").innerHTML = player.get('level')+' ур. <span class="xp-percent">('+formated_percent+'%)</span>';
	document.getElementById("xp-progress").style.width = (player.get('levelPercentage')*100)+'%';
	document.getElementById("xp-tooltip").innerHTML = (Math.round(xp_to_level*player.get('levelPercentage')))+"/"+xp_to_level;
	if(player.get('guild') != null) {
		document.getElementById("player-guild-name").innerHTML = player.get('guild').get('name');
		document.getElementById("player-guild-avatar").src = player.get('guild').get('avatar_url');
		document.getElementById("card-title-guild").style.color = "var(--mc-color-"+player.get('guild').get('color').replace('&', '')+")";
		document.getElementById("card-title-guild").href = '/guild/'+player.get('guild').get('id');
		document.getElementById("card-title-guild").style.visibility = 'unset';
	}

	document.getElementById("top").style.visibility = "unset";
	document.getElementById("player-card").style.animation = "fadein-player-card 1s";

	document.getElementById("header-main-button").addEventListener('click', header_button_click, false);
	document.getElementById("header-season-button").addEventListener('click', header_button_click, false);
	select_header_button(document.getElementById("header-main-button"));

	response = await fetch("https://api.vimeworld.ru/user/"+player.get('id')+"/friends");
	var friends = json_to_map(await response.json()).get('friends');
	friends.forEach(async (friend) => {
		make_friend(friend);
	});
	document.getElementById('friends-title').innerHTML = 'Друзей '+friends.size;

	load_player_stats();
}
init();
var sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay));

function make_friend(friend) {
	friend_div = document.createElement('a');
	friend_div.className = 'friend';
	friend_div.href = '/player/'+friend.get('username');
	head = document.createElement('img');
	head.src = '//skin.vimeworld.ru/helm/3d/'+friend.get('username')+'.png';
	name_span = document.createElement('span');
	name_span.innerHTML = friend.get('username');
	name_span.style.color = 'var(--'+friend.get('rank').toLowerCase()+'-rank-color)';
	friend_div.append(head);
	friend_div.append(name_span);
	document.getElementById('friends-hover').append(friend_div);
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

function make_lb_sort_locale() {
	lb_sort_locale.set('level', 'Уровень')
	lb_sort_locale.set('online', 'Онлайн')
	lb_sort_locale.set('kills', 'Убийств')
	lb_sort_locale.set('wins', 'Побед')
	lb_sort_locale.set('bedBreaked', 'Кроватей сломано')
	lb_sort_locale.set('total_wins', 'Всего побед')
	lb_sort_locale.set('total_games', 'Всего игр')
	lb_sort_locale.set('rate', 'Рейтинг')
	lb_sort_locale.set('points', 'Очков')
	lb_sort_locale.set('total_blocks', 'Всего блоков')
	lb_sort_locale.set('earned_money', 'Заработано монет')
	lb_sort_locale.set('wins_as_maniac', 'Побед за Маньяка')
	lb_sort_locale.set('tamed_sheep', 'Перетащено овец')
}

function make_blocks_locale() {
	blocks_locale.set("1", "Камень");
	blocks_locale.set("3", "Земля");
	blocks_locale.set("12", "Песок");
	blocks_locale.set("13", "Гравий");
	blocks_locale.set("14", "Золотая руда");
	blocks_locale.set("15", "Железная руда");
	blocks_locale.set("16", "Угольная руда");
	blocks_locale.set("17", "Дуб");
	blocks_locale.set("22", "Блок Лазурита");
	blocks_locale.set("23", "Раздатчик");
	blocks_locale.set("24", "Песчаник");
	blocks_locale.set("29", "Липкий поршень");
	blocks_locale.set("30", "Паутина");
	blocks_locale.set("33", "Поршень");
	blocks_locale.set("35", "Белая шерсть");
	blocks_locale.set("41", "Золотой блок");
	blocks_locale.set("42", "Железный блок");
	blocks_locale.set("43", "Каменная плита");
	blocks_locale.set("45", "Кирпичи");
	blocks_locale.set("48", "Замшелый булыжник");
	blocks_locale.set("49", "Обсидиан");
	blocks_locale.set("56", "Алмазная руда");
	blocks_locale.set("57", "Алмазный блок");
	blocks_locale.set("73", "Редстоуновая руда");
	blocks_locale.set("79", "Лед");
	blocks_locale.set("80", "Блок снега");
	blocks_locale.set("86", "Тыква");
	blocks_locale.set("87", "Адский камень");
	blocks_locale.set("88", "Песок душ");
	blocks_locale.set("89", "Светокамень");
	blocks_locale.set("103", "Арбуз");
	blocks_locale.set("118", "Котел");
	blocks_locale.set("121", "Эндерняк");
	blocks_locale.set("129", "Изумрудная руда");
	blocks_locale.set("133", "Изумрудный блок");
	blocks_locale.set("152", "Блок редстоуна");
	blocks_locale.set("153", "Кварцевая руда");
	blocks_locale.set("155", "Блок кварца");
	blocks_locale.set("158", "Выбрасыватель");
	blocks_locale.set("162", "Акация");
	blocks_locale.set("168", "Призмарин");
	blocks_locale.set("170", "Стог сена");
	blocks_locale.set("172", "Обожженная глина");
	blocks_locale.set("173", "Блок Угля");
	blocks_locale.set("174", "Твердый лед");
	blocks_locale.set("179", "Красный песчаник");
	blocks_locale.set("198", "Эндер стержень");
	blocks_locale.set("201", "Пурпурный блок");
	blocks_locale.set("202", "Пурпурная колонна");
	blocks_locale.set("216", "Костный блок");
	blocks_locale.set("251", "Белый бетон");
	blocks_locale.set("252", "Белый сухой бетон");
	blocks_locale.set("159:14", "Красная обожженная глина");
	blocks_locale.set("17:3", "Тропическое дерево");
	blocks_locale.set("159:5", "Лаймовая обожженная глина");
	blocks_locale.set("17:1", "Ель");
	blocks_locale.set("159:1", "Оранжевая обожженная глина");
	blocks_locale.set("168:2", "Темный призмарин");
	blocks_locale.set("168:1", "Призмариновые кирпичи");
	blocks_locale.set("252:9", "Бирюзовый сухой бетон");
	blocks_locale.set("98:3", "Резные каменные кирпичи");
	blocks_locale.set("98:2", "Потресканные каменные кирпичи");
	blocks_locale.set("98:1", "Замшелые каменные кирпичи");
	blocks_locale.set("1:5", "Андезит");
	blocks_locale.set("1:1", "Гранит");
	blocks_locale.set("95:10", "Фиолетовое стекло");
	blocks_locale.set("179:1", "Резной красный песчаник");
	blocks_locale.set("12:1", "Красный песок");
	blocks_locale.set("95:2", "Пурпурное стекло");
	blocks_locale.set("251:8", "Бирюзовый бетон");
	blocks_locale.set("155:2", "Кварцевая колонна");
	blocks_locale.set("155:1", "Резной кварц");
	blocks_locale.set("24:2", "Гладкий песчаник");
	blocks_locale.set("24:1", "Резной песчаник");
	blocks_locale.set("162:3", "Искаженная ножка");
	blocks_locale.set("162:2", "Багровая ножка");
	blocks_locale.set("252:15", "Черный сухой бетон");
	blocks_locale.set("252:14", "Красный сухой бетон");
	blocks_locale.set("252:13", "Зеленый сухой бетон");
	blocks_locale.set("252:11", "Синий сухой бетон");
	blocks_locale.set("252:10", "Фиолетовый сухой бетон");
	blocks_locale.set("252:8", "Светло-серый сухой бетон");
	blocks_locale.set("252:7", "Серый сухой бетон");
	blocks_locale.set("252:6", "Розовый сухой бетон");
	blocks_locale.set("252:5", "Лаймовый сухой бетон");
	blocks_locale.set("252:4", "Желтый сухой бетон");
	blocks_locale.set("252:3", "Голубой сухой бетон");
	blocks_locale.set("252:2", "Пурпурный сухой бетон");
	blocks_locale.set("252:1", "Оранжевый сухой бетон");
	blocks_locale.set("1:3", "Диорит");
	blocks_locale.set("252:12", "Коричневый сухой бетон");
	blocks_locale.set("35:13", "Зеленая шерсть");
	blocks_locale.set("95", "Белое стекло");
	blocks_locale.set("98", "Каменные кирпичи");
	blocks_locale.set("18", "Дубовая листва");
	blocks_locale.set("11", "Лава");
}

function make_stat_row(name, value) {
	if(name == 'Сломанные блоки') {
		var stat_title = document.createElement("div");
		stat_title.className = 'stat-title';
		stat_title.innerHTML = 'Блоки';

		var stat_hover = document.createElement("div");
		stat_hover.className = 'stat-hover';

		stat_title.append(stat_hover);

		value = new Map([...value.entries()].sort((a, b) => b[1] - a[1]));

		value.forEach(async (count, id) => {
			if(count >= 1000000){
				count = Math.round(count/100000)/10.0;
				count_text = count+'м';
			}
			else if(count >= 100000){
				count = Math.round(count/1000);
				count_text = count+'к';
			}
			else if(count >= 10000){
				count = Math.round(count/100)/10.0;
				count_text = count+'к';
			}
			else
				count_text = count+'';
			stat_row = make_stat_row(blocks_locale.get(id), count_text);
			stat_hover.append(stat_row);
		});
		return stat_title;
	}
	else {
		var stat_row = document.createElement("div");
		stat_row.className = "stat-row"

		span_name = document.createElement("span");
		span_name.innerHTML = name;

		span_value = document.createElement("span");
		span_value.innerHTML = "<b>"+value.toLocaleString(undefined, {})+"</b>";

		stat_row.append(span_name);
		stat_row.append(span_value);
		return stat_row;
	}
}

function make_lb_row(name, place, diff) {
	var stat_row = document.createElement("div");
	stat_row.className = "lb-row"

	span_name = document.createElement("span");
	span_name.innerHTML = name;

	span_place = document.createElement("span");
	span_place.innerHTML = place;

	span_diff = document.createElement("div");
	if(diff >= 0) {
		span_diff.innerHTML = "+"+diff;
		span_diff.style.backgroundColor = 'var(--green-color-s)';
	}
	else {
		span_diff.innerHTML = diff;
		span_diff.style.backgroundColor = 'var(--red-color-s)';
	}

	stat_row.append(span_name);
	stat_row.append(span_place);
	span_place.append(span_diff);
	return stat_row;
}

function format_date(date) {
	day = String(date.getDate());
	if(date.getDate() < 10)
		day = "0"+day;
	month = String(date.getMonth()+1);
	if(date.getMonth()+1 < 10)
		month = "0"+month;
	year = date.getFullYear()-2000;
	hours = String(date.getHours());
	if(date.getHours() < 10)
		hours = "0"+hours;
	mins = String(date.getMinutes());
	if(date.getMinutes() < 10)
		mins = "0"+mins;
	formated = day+"."+month+"."+year+" "+hours+":"+mins;
	return formated;
}

function show_hide_action() {
	el = this.lastChild;
	if (el.style.visibility == 'hidden') {
		el.style.visibility = 'unset';
		el.style.height = 'auto';
	}
	else {
		el.style.visibility = 'hidden';
		el.style.height = '0';
	}
}

function show_hide_filter() {
	filter_window = document.getElementById('filter-window');
	if (filter_window.style.height == '0px') {
		filter_window.style.height = 'auto';
		filter_window.style.marginTop = '';
		this.style.background = '#57F287';
	}
	else {
		filter_window.style.height = '0';
		filter_window.style.marginTop = '0';
		this.style.background = '';
	}
}

function filter() {
	if(can_change_filter == false)
		return;
	tag = this.getAttribute('data-tag');
	if (this.style.background == 'var(--primary-color)') {
		this.style.background = '';
		filter_list.set(tag, false);
	}
	else{
		this.style.background = 'var(--primary-color)';
		filter_list.set(tag, true);
	}
    get_actions_div();
    make_100_actions();
}

function hide_show_elements_with_filter() {
	Object.entries($("#actions-place .actions")).forEach((value) => {
		action = value[1];
		tag = action.getAttribute('data-tag');
		if(filter_list.get(tag) == true) {
			action.style.visibility = 'unset';
			action.style.height = 'auto';
			action.style.margin = '';
			action.style.minHeight = '';
			return
		}
		action.style.visibility = 'hidden';
		action.style.height = '0';
		action.style.margin = '0';
		action.style.minHeight = '0';
	});
}

function make_filter_element(name, tag) {
	filter_element = document.createElement("div");
    filter_element.className = "filter-window-element";
    filter_element.innerHTML = "<b>"+name+"</b>";
 	filter_element.setAttribute('data-tag', tag);
 	filter_element.addEventListener('click', filter, false);
 	filter_element.style.background = 'var(--primary-color)';
 	filter_list.set(tag, true);
    return filter_element;
}

function make_simple_action_div(header, content) {
	var action_div = document.createElement("div");
	action_div.className = "actions";

	var actions_header = document.createElement("div");
	actions_header.className = "actions-header";
	actions_header.style.font_family = "'Fredoka', sans-serif";
	actions_header.innerHTML = header;
	action_div.append(actions_header);

	var span_content = document.createElement("span");
	span_content.innerHTML = content;
	span_content.style.margin = "0.5em";

	action_div.append(span_content);
	return action_div;
}

function get_top_stats_div() {
	var stats_top_div = document.getElementById("stats-place-top");
    if(stats_top_div == null) {
	  	stats_top_div = document.createElement("div");
	    stats_top_div.className = "stats-place-top";
	    stats_top_div.id = "stats-place-top";
	    document.body.insertBefore(stats_top_div, document.getElementById('data-place'));
    }
    else {
    	stats_top_div.innerHTML = "";
    }
    return stats_top_div;
}

function update_top_stats(xp, played_seconds) {
	stats_top_div = get_top_stats_div();
	if(xp > 0) {
		span_xp = document.createElement("span");
	    span_xp.innerHTML = xp;
	    xp_img = document.createElement("img");
	    xp_img.className = "stats-icon";
	    xp_img.style.width = "17px";
	    xp_img.src = "/static/gif/experience-orb.gif";
	    span_xp.append(xp_img);
	    stats_top_div.append(span_xp);
	}
	if(played_seconds > 0) {
	    span_time = document.createElement("span");
	    span_time.innerHTML = formate_time(played_seconds);
	    time_img = document.createElement("img");
	    time_img.className = "stats-icon";
	    time_img.src = "/static/png/clock.png";
	    span_time.append(time_img);
	    stats_top_div.append(span_time);
	}
}

function get_and_clear_stats_div() {
	var stats_div = document.getElementById("stats-div");
    document.getElementById("stats-place").innerHTML = "";
    return stats_div;
}

function get_actions_div() {
	var actions_div = document.getElementById("actions-div");
    if(actions_div == null) {
	  	actions_div = document.createElement("div");
	    actions_div.className = "actions-div";
	    actions_div.id = "actions-div";

	    actions_div_header = document.createElement("div");
	    actions_div_header.className = "actions-div-header";
	    actions_div.append(actions_div_header);

	    actions_div_header.innerHTML = '<span>Список матчей по времени</span>'

	    filter_div = document.createElement("div");
	    filter_div.className = "filter-div";
	    src = "/static/png/filter.png";
	    filter_div.innerHTML = "<img src='"+src+"'>";
	    filter_div.addEventListener('click', show_hide_filter, false);
	    actions_div_header.append(filter_div);

	    filter_window = document.createElement("div");
	    filter_window.className = "filter-window";
	    filter_window.id = 'filter-window';
	    filter_window.style.height = '0';
	    filter_window.style.marginTop = '0';
	    actions_div_header.append(filter_window);

	    filter_window.append(make_filter_element('Матчи', 'match'));
	    // filter_window.append(make_filter_element('Активность', 'game'));
	    filter_window.append(make_filter_element('Опыт', 'xp'));
	    // filter_window.append(make_filter_element('Онлайн', 'online'));
	    filter_window.append(make_filter_element('Наиграно', 'playedSeconds'));
	    filter_window.append(make_filter_element('Статус', 'rank'));

	    actions_div_place = document.createElement("div");
	    actions_div_place.className = "actions-place";
	    actions_div_place.id = "actions-place";
	    actions_div.append(actions_div_place);

	    actions_div_place.addEventListener('scroll', (event) => {
			scroll_bottom = event.target.scrollHeight-event.target.scrollTop;
		    if(scroll_bottom <= 2000)
		    	make_100_actions();
		});

	    document.getElementById('data-place').append(actions_div);
    }
    else {
    	document.getElementById("actions-place").innerHTML = "";
    }
    return actions_div;
}

function get_leaderboard_div() {
	var lb_div = document.getElementById("lb-div");
    if(lb_div == null) {
	  	lb_div = document.createElement("div");
	    lb_div.className = "lb-div";
	    lb_div.id = "lb-div";
	    document.body.append(lb_div);

	    lb_div_header = document.createElement("div");
	    lb_div_header.className = "lb-div-header";
	    lb_div_header.innerHTML = '<span>Изменение в топах</span>';
	    lb_div.append(lb_div_header);

	    lb_place = document.createElement("div");
	    lb_place.className = "lb-place";
	    lb_place.id = "lb-place";
	    lb_div.append(lb_place);
    }
    else {
    	document.getElementById("lb-place").innerHTML = "";
    }
    return lb_div;
}

function make_stats(games) {
	var stats_div = document.getElementById("stats-place");
	games.forEach(async (value, game) => {
    	stat_elements_count += 1;
    	await sleep(load_delay*stat_elements_count);
    	game_stats = value;

    	var stat_div = document.createElement("div");
    	stat_div.className = "stat";
    	var stat_header = document.createElement("div");
    	stat_header.className = "stat-header";
    	stat_header.style.font_family = "'Fredoka', sans-serif";

    	game_name = locale.get('games').get(game.toLowerCase()).get('name');

    	stat_header.innerHTML = game_name;
    	stat_div.append(stat_header);
    	stats_div.append(stat_div);

    	var stat_content = document.createElement("div");
		stat_content.className = "stat-content";
		var stat_row_place = document.createElement("div");
		stat_row_place.className = "stat-row-place";

		stat_row = make_stat_row('Игр', game_stats.get('games'))
		stat_row_place.append(stat_row);
		stat_row = make_stat_row('Побед', game_stats.get('wins'))
		stat_row_place.append(stat_row);

		game_stats.forEach((stat, stat_name) => {
			game_stat_name = locale.get('game_stats').get(game.toLowerCase()).get(stat_name);
			if(game_stat_name == null || game_stat_name == 'Игр' || game_stat_name == 'Побед')
				return
			stat_row = make_stat_row(game_stat_name, stat)
			stat_row_place.append(stat_row);
		});
		stat_content.append(stat_row_place);
		stat_div.append(stat_content);
	});
}

function get_filter_actions() {
	actions_tmp = new Array();
	actions.forEach(async (action) => {
		actions_data = json_to_map(JSON.parse(action.get('2').replaceAll("'", "\"").replaceAll("False", "false").replaceAll("True", "true")));
		actions_data.set('date', format_date(new Date(action.get('1'))))
		if (actions_data.get('match') != null && filter_list.get('match'))
			actions_tmp.push(actions_data);
		else if (actions_data.get('xp') != null && filter_list.get('xp'))
			actions_tmp.push(actions_data);
		else if (actions_data.get('playedSeconds') != null && filter_list.get('playedSeconds'))
			actions_tmp.push(actions_data);
		else if (actions_data.get('rank') != null && filter_list.get('rank'))
			actions_tmp.push(actions_data);
	});
	return actions_tmp;
}

function make_100_actions() {
	filtered_actions = get_filter_actions();
	var actions_div = document.getElementById("actions-place");
	count = actions_div.childNodes.length;
	if(count >= filtered_actions.length)
		return;
	arrayTmp = filtered_actions.slice(count, count+100);
    arrayTmp.forEach(async (action) => {
    	action_div = make_action(action);
    	actions_div.append(action_div);
    })
}

function make_action(action) {
	action_div = null;
	match = action.get('match');
	time = action.get('date');
	if (match != null && filter_list.get('match')) {
		is_win = match.get('wins') > 0;
		action_div = document.createElement("div");
		action_div.className = "actions";
		action_div.setAttribute('data-tag', 'match');

		var actions_header = document.createElement("div");
		actions_header.className = "actions-header";
		actions_header.style.font_family = "'Fredoka', sans-serif";
		if(is_win)
			actions_header.style.background = "linear-gradient(to right, var(--green-color) 30%, var(--primary-color))";
		else
			actions_header.style.background = "linear-gradient(to right, var(--red-color) 30%, var(--primary-color))";
		game = match.get('game').toLowerCase();
		game_name = locale.get('games').get(game).get('name');

		var stat_content = document.createElement("div");
		stat_content.className = "actions-content";
		stat_content.style.visibility = 'hidden';
		stat_content.style.height = '0';
		var stat_row_place = document.createElement("div");
		stat_row_place.className = "actions-row-place";

    	actions_header.innerHTML = game_name+"<span>["+time+"]</span>";
    	action_div.addEventListener('click', show_hide_action, false);
		action_div.append(actions_header);

		match.forEach((stat, stat_name) => {
			game_stat_name = locale.get('game_stats').get(game).get(stat_name);
			if(game_stat_name == null || stat_name == 'game' || game_stat_name == 'Игр' || stat_name == 'wins')
				return;
			stat_row = make_stat_row(game_stat_name, stat);
			stat_row_place.append(stat_row);
		});
		stat_content.append(stat_row_place);
		action_div.append(stat_content);
	}
	xp = action.get('xp');
	if (xp != null && filter_list.get('xp')) {
	    src = "/static/gif/experience-orb.gif"
	    content = xp+"<img class='stats-icon' src='"+src+"' style='width: 17px;'>"
		action_div = make_simple_action_div("Получено опыта<span>["+time+"]</span>", content)
		action_div.setAttribute('data-tag', 'xp');
	}

	playedSeconds = action.get('playedSeconds');
	if (playedSeconds != null && filter_list.get('playedSeconds')) {
	    src = "/static/png/clock.png"
	    content = Math.round(playedSeconds/60)+" мин.<img class='stats-icon' src='"+src+"'>"
		action_div = make_simple_action_div("Наиграно<span>["+time+"]</span>", content)
		action_div.setAttribute('data-tag', 'playedSeconds');
	}
	rank = action.get('rank');
	if (rank != null && filter_list.get('rank')) {
		rank = rank.toLowerCase();
		content = "<b class='rank-color-"+rank+"'>"+locale.get('ranks').get(rank).get('name')+"</b>";
		action_div = make_simple_action_div("Изменен статус<span>["+time+"]</span>", content);
		action_div.setAttribute('data-tag', 'rank');
	}
	return action_div;
}

function make_lb(lb) {
	var lb_place = document.getElementById("lb-place");
	lb.forEach(async (value, lb) => {
		stat_elements_count += 1;
		await sleep(load_delay*stat_elements_count);

		var lb_div = document.createElement("div");
    	lb_div.className = "lb";
    	var lb_header = document.createElement("div");
    	lb_header.className = "lb-header";
    	lb_header.style.font_family = "'Fredoka', sans-serif";
    	lb_header.innerHTML = leaderboard_list.get(lb).get('description');
    	lb_div.append(lb_header);
    	lb_place.append(lb_div);

    	var lb_content = document.createElement("div");
		lb_content.className = "stat-content";
		var lb_row_place = document.createElement("div");
		lb_row_place.className = "stat-row-place";

		value.forEach(async (data, sort) => {
			diff = data.get('diff')
			place = data.get('place')
			lb_row = make_lb_row(lb_sort_locale.get(sort), place, diff)
			lb_row_place.append(lb_row);
		});
		lb_content.append(lb_row_place);
		lb_div.append(lb_content);
	});
}

$(function() {
  $('input[name="daterange"]').daterangepicker({
    opens: 'left',
    locale:{separator:" - ",format:"DD.MM.YYYY",applyLabel:"Выбрать",cancelLabel:"Отмена",fromLabel:"От",toLabel:"До"}
  })});
  $('input[name="daterange"]').on('apply.daterangepicker', async function(ev, picker) {
  	if (!can_change_filter) {
  		return;
  	}
  	start = picker.startDate;
  	end = picker.endDate;
  	can_change_filter = false;

  	document.getElementById("loading").style.animation = 'loading-in 0.5s';
  	document.getElementById("loading").style.visibility = 'unset';
  	document.getElementById("select-hint").style.visibility = 'hidden';
  	select_header_button(null);

  	try {
	  	response = await fetch("/api/"+user_id+"/stats?start_date="+start.format('DD.MM.YYYY')+"&end_date="+end.format('DD.MM.YYYY'));
		var stats = json_to_map(await response.json());
		response = await fetch("/api/"+user_id+"/actions?start_date="+start.format('DD.MM.YYYY')+"&end_date="+end.format('DD.MM.YYYY'));
		actions = json_to_map(await response.json()).get('actions');
		var games = stats.get('games');
		response = await fetch("/api/"+user_id+"/leaderboard?start_date="+start.format('DD.MM.YYYY')+"&end_date="+end.format('DD.MM.YYYY'));
		var lb = json_to_map(await response.json());
	} catch(err) {
		can_change_filter = true;
		document.getElementById("loading").style.animation = 'loading-out 0.5s';
		document.getElementById("loading").style.visibility = 'hidden';
		send_error_notify('Ошибка сервера! Попробуйте повторить позже или сообщите куда-нибудь.');
	}
    
    var xp = stats.get("xp");
    var played_seconds = stats.get("played_seconds");

    if(stats.size == 0) {
    	xp = 0;
    	played_seconds = 0;
    }

    update_top_stats(xp, played_seconds);
    get_and_clear_stats_div();
    get_actions_div();
    get_leaderboard_div();

 	stat_elements_count = -1;
 	if(games != null && games.size > 0)
    	make_stats(games);
    make_100_actions();
    make_lb(lb);
	
	setTimeout(() => {
		can_change_filter = true;
		document.getElementById("loading").style.animation = 'loading-out 0.5s';
		document.getElementById("loading").style.visibility = 'hidden';
	}, stat_elements_count*load_delay);
});

function header_button_click() {
	select_header_button(this);
	tag = this.getAttribute('data-tag');
	load_player_stats(tag)
}

function select_header_button(button) {
	if(header_selected_button != null)
		header_selected_button.style.backgroundColor = '';
	header_selected_button = button;
	if(button != null)
		button.style.backgroundColor = 'var(--primary-color)';
}

async function load_player_stats(type='global') {
	response = await fetch("https://api.vimeworld.ru/user/"+user_id+"/stats");
	var player_data = json_to_map(await response.json());
	var player_stats = player_data.get('stats');
	var player = player_data.get('user');
	get_and_clear_stats_div();
	actions_div = document.getElementById('actions-div');
	if(actions_div != null) actions_div.remove();
	lb_div = document.getElementById('lb-div');
	if(lb_div != null) lb_div.remove();
	update_top_stats(0, player.get('playedSeconds'));

	var stats_div = document.getElementById("stats-place");
	player_stats.forEach(async (value, game) => {
		game_stats = value.get(type);
		if(type == 'season') {
			if(game_stats == null)
				return;
			if(game_stats.get('monthly') != null)
				game_stats = game_stats.get('monthly');
			else if(game_stats.get('manual') != null)
				game_stats = game_stats.get('manual');
		}

		var stat_div = document.createElement("div");
    	stat_div.className = "stat";
    	var stat_header = document.createElement("div");
    	stat_header.className = "stat-header";
    	stat_header.style.font_family = "'Fredoka', sans-serif";

    	game_name = locale.get('games').get(game.toLowerCase()).get('name');

    	stat_header.innerHTML = game_name;
    	stat_div.append(stat_header);
    	stats_div.append(stat_div);

    	var stat_content = document.createElement("div");
		stat_content.className = "stat-content";
		var stat_row_place = document.createElement("div");
		stat_row_place.className = "stat-row-place";

		game_stats.forEach((stat, stat_name) => {
			game_stat_name = locale.get('game_stats').get(game.toLowerCase()).get(stat_name);
			if(game_stat_name == null)
				return
			stat_row = make_stat_row(game_stat_name, stat)
			stat_row_place.append(stat_row);
		});
		stat_content.append(stat_row_place);
		stat_div.append(stat_content);
	});
}