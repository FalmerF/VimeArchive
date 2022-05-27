var update = null;

function close_window() {
	this.style.animation = 'update-out 1s';
	this.style.visibility = 'hidden';
	document.getElementById('update-window').style.animation = 'update-window-out 1s';
	set_cookie('last_upd', update.get('version'))
}

async function check_update() {
	response = await fetch('/api/update');
	update = json_to_map(await response.json());
	cookies = get_cookie();
	last_upd_version = cookies.get('last_upd');
	if(last_upd_version == null || last_upd_version != update.get('version')) {
		upd_div = document.createElement('div');
		upd_div.className = 'update';

		upd_window = document.createElement('div');
		upd_window.className = 'update-window';
		upd_window.id = 'update-window';

		title = document.createElement('h3');
		title.innerHTML = update.get('title');

		message_div = document.createElement('div');
		message_div.className = 'message';

		message = document.createElement('span');
		message.innerHTML = update.get('message');

		discord_link = document.createElement('a');
		discord_link.href = "https://discord.gg/qEJdZuHydq";
		discord_link.target = "_blank";
		discord_link.innerHTML = '<img src="/static/svg/discord-logo.svg" class="discord-logo-update">';

		message_div.append(message);
		upd_window.append(title);
		upd_window.append(discord_link);
		upd_window.append(message_div);

		upd_div.append(upd_window);
		upd_div.addEventListener('click', close_window, false);

		document.body.append(upd_div);

		$('.update-window').on('click', function(e){
			e.stopPropagation();
		});
	}
}

check_update();