function get_cookie() {
	cookies = new Map();
	params = document.cookie.split('; ');
	params.forEach((value) => {
		d = value.split('=');
		cookies.set(d[0], d[1]);
	});
	return cookies;
}
function set_cookie(name, value) {
	let date = new Date(Date.now() + 86400e3*365);
	date = date.toUTCString();
	document.cookie = name+'='+value+'; expires=' + date+'; path=/';
}
function get_error_place() {
	error_place = document.getElementById('error_place');
	if(error_place != null)
		return error_place;

	error_place = document.createElement('div');
	error_place.className = 'error_place';
	error_place.id = 'error_place';
	document.body.append(error_place);
	return error_place;
}
function make_error_div(message) {
	error = document.createElement('div');
	error.className = 'error_notify';

	span = document.createElement('span');
	span.innerHTML = message;

	error_bottom = document.createElement('div');
	error_bottom.className = 'error_bottom';

	error.append(span);
	error.append(error_bottom);

	return error;
}
function send_error_notify(message) {
	error_place = get_error_place();
	error = make_error_div(message);
	error_place.append(error);

	setTimeout((error_div) => {
		error_div.remove();
	}, 8000, error);
}
function send_notify(message) {
	error_place = get_error_place();
	notify = make_error_div(message);
	notify.style.backgroundColor = 'var(--mc-color-a)';
	error_place.append(notify);

	setTimeout((notify_div) => {
		notify_div.remove();
	}, 8000, notify);
}
function json_to_map(json) {
	var map = new Map();
	var json_map = new Map(Object.entries(json));
	json_map.forEach((value, key) => {
		if(value != null && Object.entries(value).length > 0 && typeof value != 'string')
			map.set(key, json_to_map(value));
		else
			map.set(key, value);
	});
	return map;
}

var statusUserRegex = new RegExp("(@[A-Za-z0-9_]{3,16})", "g");
async function parse_status(status) {
	status = status.replaceAll('&lt;br /&gt;', '<br />');
	var players = status.match(statusUserRegex);
	if(players != null) {
		var string_players = '';
		players.forEach((p) => {
			string_players += p.replace('@', '')+',';
		});
		response = await fetch("https://api.vimeworld.ru/user/name/"+string_players);
		var players_data = json_to_map(await response.json());
		players_data.forEach((value, num) => {
			var username = value.get('username');
			status = status.replaceAll('@'+value.get('username'), '<a href="/player/'+username+'"><span class="status-player-mention" style="color: var(--'+value.get('rank').toLowerCase()+'-rank-color);"><img src="https://skin.vimeworld.ru/helm/3d/'+username+'.png">'+username+'</span></a>');
		});
	}
	return status;
}

function copy_text(text) {
	fallbackCopyTextToClipboard(text);
	send_notify('Скопировано: '+text);
}

function fallbackCopyTextToClipboard(text) {
  var textArea = document.createElement("textarea");
  textArea.value = text;
  
  // Avoid scrolling to bottom
  textArea.style.top = "0";
  textArea.style.left = "0";
  textArea.style.position = "fixed";

  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  try {
    var successful = document.execCommand('copy');
    var msg = successful ? 'successful' : 'unsuccessful';
    console.log('Fallback: Copying text command was ' + msg);
  } catch (err) {
    console.error('Fallback: Oops, unable to copy', err);
  }

  document.body.removeChild(textArea);
}