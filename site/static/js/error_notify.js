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