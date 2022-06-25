var status_locale = new Map();
status_locale.set('MEMBER', 'Участник');
status_locale.set('OFFICER', 'Офицер');
status_locale.set('LEADER', 'Лидер');

init();
async function init() {
	response = await fetch("https://api.vimeworld.ru/guild/get?id="+guild_id+"&unsafe=0");
	var guild = json_to_map(await response.json());

	window.document.title = "VimeArchive - " + guild.get('name');

	max_members = 20+(5*guild.get('perks').get('MEMBERS').get('level'));
	need_xp = 40000+(10000*guild.get('level'));
	current_xp = Math.round(need_xp*guild.get('levelPercentage'));
	web_info = guild.get('web_info');
	if(web_info != null)
		web_info = web_info.replaceAll('<img src="', '<img src="http://lnk.su/api/image.get?url=');

	document.getElementById('guild-avatar').src = guild.get('avatar_url');
	document.getElementById('guild-name').innerHTML = guild.get('name');
	document.getElementById('guild-tag').innerHTML = guild.get('tag');
	document.getElementById('guild-name').style.color = "var(--mc-color-"+guild.get('color').replace('&', '')+")";
	document.getElementById('guild-tag').style.color = "var(--mc-color-"+guild.get('color').replace('&', '')+")";
	document.getElementById('guild-web-info').innerHTML = web_info;
	document.getElementById('members-title').innerHTML = "Участников - "+guild.get('members').size+"/"+max_members;
	document.getElementById('guild-level-title').innerHTML = "Уровень "+guild.get('level');
	document.getElementById('xp-tooltip').innerHTML = current_xp+"/"+need_xp;
	document.getElementById('guild-level-progress').style.width = (guild.get('levelPercentage')*100)+"%";
	document.getElementById('create-date').innerHTML = new Date(guild.get('created') * 1000).toLocaleDateString("ru-RU", {year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric'})
	document.getElementById('total-coins').innerHTML = guild.get('totalCoins').toLocaleString(undefined, {});
	document.getElementById('total-xp').innerHTML = guild.get('totalExp').toLocaleString(undefined, {});

	table_body = document.getElementById('table-body');

	guild.get('members').forEach(async (member, num) => {if(member.get('status') == 'LEADER') {table_body.append(make_member_row(member))}})
	guild.get('members').forEach(async (member, num) => {if(member.get('status') == 'OFFICER') {table_body.append(make_member_row(member))}})
	guild.get('members').forEach(async (member, num) => {if(member.get('status') == 'MEMBER') {table_body.append(make_member_row(member))}})

	perks_body = document.getElementById('perks-body');
	guild.get('perks').forEach(async (perk, num) => {perks_body.append(make_perk_row(perk))})
}

function make_member_row(member) {
	row = document.createElement('tr');
	index = document.createElement('td');
	name_td = document.createElement('td');

	index.innerHTML = document.getElementById('table-body').childNodes.length+1;

	user = member.get('user');
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
	name_href.href = '/player/'+username;
	name_href.append(name_span);

	name_td.append(user_head);
	name_td.append(name_href);

	row.append(index);
	row.append(name_td);

	td = document.createElement('td');
	td.innerHTML = status_locale.get(member.get('status'));
	row.append(td);

	td = document.createElement('td');
	td.innerHTML = member.get('guildExp').toLocaleString(undefined, {});
	row.append(td);

	td = document.createElement('td');
	td.innerHTML = member.get('guildCoins').toLocaleString(undefined, {});
	row.append(td);

	return row;
}

function make_perk_row(perk) {
	name_span = document.createElement('span');
	name_span.className = 'info-name';
	name_span.innerHTML = perk.get('name')+": ";

	info_span = document.createElement('span');
	info_span.className = 'info-content';
	info_span.innerHTML = perk.get('level') + ' lvl';

	name_span.append(info_span);
	return name_span;
}