var sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay))
var logo = document.getElementById('clickable-logo');
var BreakException = {};

logo.addEventListener('click', event => {
	// logo.style.webkitAnimationPlayState = "running";
	logo.style.animation = "logo-tap 0.15s ease-in-out";
	off_anim()
	async function off_anim() {
	    await sleep(150);
	    logo.style.animation = "none";
	};
});

const clamp = (num, min, max) => Math.min(Math.max(num, min), max);
var canvas = document.getElementById("canvas");
var ctx = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

chars = ['V', 'i', 'm', 'e', 'A', 'r', 'c', 'h', 'i', 'v', 'e']
posY = 200;
x = window.innerWidth/2-60;
char_pos = [[x-120, posY], [x-85, posY], [x-73, posY], [x-32, posY], [x-4, posY],
[x+32, posY],[x+53, posY],[x+79, posY],[x+106, posY],[x+117, posY],[x+145, posY]]
char_vel = []
for(i = 0; i < chars.length; i++) {
    velX = 0;
	velY = getRandomInt(-75, -25)/100.0;
	char_vel.push([velX, velY])
}

setInterval(function() {
	var width = window.innerWidth;
	var height = window.innerHeight;
	ctx.clearRect(0, 0, width, height);
	draw_effect(ctx);
	ctx.fillStyle = "white";
	ctx.globalAlpha = 1;
	ctx.font = "48px 'Fredoka', sans-serif";
	for(i = 0; i < chars.length; i++) {
		pos = char_pos[i];
		vel = char_vel[i];
		pos[0] += vel[0];
		pos[1] += vel[1];
		vel[0] = lerp(vel[0], 0, 0.01);
		vel[1] = lerp(vel[1], 0, 0.01);
		ctx.fillText(chars[i], pos[0], pos[1]);
	}
}, 30);

async function init() {
	response = await fetch("https://api.vimeworld.ru/online");
	var online_data = json_to_map(await response.json());

	response = await fetch("https://api.vimeworld.ru/locale/ru");
	var locale_data = json_to_map(await response.json());

	online_div = document.getElementById('online-div');

	online_el = document.createElement('div');
	online_el.innerHTML = 'Онлайн: <span>'+online_data.get('total')+'</span>';
	online_el.className = 'online-title online-element'
	online_el.style.cssText = "--i: 0";
	online_div.append(online_el);

	index = 0;

	online_data.get('separated').forEach(async (value, key) => {
		index++;
		game_name = '';
		if(key == 'lobby') game_name = 'Лобби';
		else {
			game = locale_data.get('games').get(key);
			if(game != null)
				game_name = game.get('name');
			else
				game_name = key;
		}
		
		online_el = document.createElement('div');
		online_el.innerHTML = ''+game_name+': <span>'+value+'</span>';
		online_el.className = 'online-element'
		online_el.style.cssText = "--i: "+index;
		online_div.append(online_el);
	});
}
init();
load_statuses();

async function load_statuses() {
	response = await fetch("/api/player/status/last");
	var statuses_data = json_to_map(await response.json());
	var statuses = new Map();
	statuses_data.forEach((value, num) => {
		statuses.set(value.get('id'), value.get('status'));
	});

	last_id = 0;
	status_place = document.getElementById('status-place');
	if(status_place.childNodes.length > 0) {
		last_id = status_place.childNodes[status_place.childNodes.length-1].getAttribute('data-id');
	}
	players_string = '';
	try {
		statuses.forEach((status, id) => {
			if(id+'' == last_id) throw BreakException;
			players_string += id+',';
		});
	} catch (e) {
	  	if (e !== BreakException) throw e;
	}

	if(players_string != '') {
		response = await fetch("https://api.vimeworld.ru/user/"+players_string);
		var players_data = json_to_map(await response.json());

		i = -1;
		players_data.forEach(async (player, num) => {
			i += 1
			await sleep(50*i);
			var username = player.get('username');
			var status_el = document.createElement('div');
			status_el.className = 'status-el';
			status_el.innerHTML = '<a href="/player/'+username+'"><span class="status-el-header" style="color: var(--'+player.get('rank').toLowerCase()+'-rank-color);"><img src="https://skin.vimeworld.ru/helm/3d/'+username+'.png">'+username+'</span></a>'
			var content_span = document.createElement('span');
			content_span.className = 'status-el-content';
			content_span.textContent = statuses.get(player.get('id')).replaceAll('\n', '<br />');
			content_span.innerHTML = await parse_status(content_span.innerHTML);
			status_el.append(content_span);
			status_el.setAttribute('data-id', player.get('id'));
			if(status_place.childNodes.length == 0)
				status_place.append(status_el);
			else
				status_place.insertBefore(status_el, status_place.childNodes[0]);
		});
	}
}