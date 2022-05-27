import discord
import time
import requests
import DataBase
import os
import sys
import threading
import ast
import traceback
import pathlib
import utils
from datetime import datetime, date, timedelta
from discord.ext import commands
from discord_components import DiscordComponents, Button, Select, SelectOption, ButtonStyle, Component
from utils import cls, get_player_stats, get_player_actions, format_date, get_xp_for_lvl

diff = 45023
date = datetime.now()
seconds_in_day = date.hour*3600+date.minute*60+date.second

if diff > seconds_in_day:
	diff_p_day = diff-seconds_in_day
	diff = seconds_in_day
	date = date - timedelta(days=1)
	date = date.replace(hour=23, minute=59, second=59)
print(diff_p_day)
print(diff)