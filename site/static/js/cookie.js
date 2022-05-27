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