function close_notify() {
	set_cookie('test_notify_checked', 'true');
	notify = document.getElementById('test_notify');
	notify.parentNode.removeChild(notify);
}

cookies = get_cookie();
test_notify_checked = cookies.get('test_notify_checked');
if (test_notify_checked == null || test_notify_checked == '') {
	notify_div = document.createElement("div");
	notify_div.className = 'bottom_notify';
	notify_div.id = 'test_notify';

	content_span = document.createElement("span");
	content_span.innerHTML = 'Сайт находится в тестовом режиме, возможно большое количество ошибок и пропусков!';
	notify_div.append(content_span);

	close_div = document.createElement("div");
	close_div.className = 'close-img';
	close_div.addEventListener('click', close_notify, false);
	close_img = document.createElement("img");
	close_img.src = "/static/png/close.png";
	close_div.append(close_img);
	notify_div.append(close_div);

	document.body.append(notify_div);
}