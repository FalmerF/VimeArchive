from vime import Vime
import requests
import time

print('Start')
vime = Vime()

players = []
for i in range(800):
	players.append(4921298)
print('Players list maked')

resp = requests.get(url='https://api.vimeworld.ru/user/name/FalmerF')
reset_time = int(resp.headers['X-RateLimit-Reset-After'])+1
print(f'Waiting {reset_time} sec.')
time.sleep(reset_time)

for i in range(45):
	print(f'Send request {i}')
	vime.get_player(4921298)
print(f'Requests sended. Limit: {vime.limit_remaining}')

sessions = vime.get_sessions(players)
print(f'Players get {len(sessions)}')
print(f'Limit: {vime.limit_remaining}')