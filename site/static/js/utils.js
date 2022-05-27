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