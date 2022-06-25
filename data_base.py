import re
import sqlite3
import os
import asyncio
import threading
from datetime import datetime
from random import randrange

class DataBase:
    def __init__(self, date: str, make_db=True, file_name=None):
        self.con = None
        self.last_update = datetime.now()
        self.update_list = []
        self.insert_list = []
        self.delete_list = []
        self.get_dict = {}

        if file_name is None:
            file_name = f'{os.path.dirname(__file__)}/data/{date}.db'
        self.file_name = file_name
        try:
            f = open(file_name, "r", encoding="utf-8")
            f.close()
            self.valid = True
            self.con = sqlite3.connect(self.file_name)
        except FileNotFoundError:
            if make_db:
                open(file_name, "a", encoding="utf-8")
                self.con = sqlite3.connect(self.file_name)
                self.create_data_base()
                self.valid = True
            else:
                self.valid = False
        threading.Thread(target=self.run_async_task).start()

    def run_async_task(self):
        asyncio.run(self.update_cycle())

    async def update_cycle(self):
        self.con = sqlite3.connect(self.file_name)
        while True:
            while len(self.update_list) > 0:
                args = self.update_list.pop(0)
                self.update(*args)

            while len(self.insert_list) > 0:
                args = self.insert_list.pop(0)
                self.insert(*args)

            while len(self.delete_list) > 0:
                args = self.delete_list.pop(0)
                self.delete(*args)

            for key in self.get_dict:
                if self.get_dict[key]['completed'] != True:
                    self.get_dict[key]['result'] = self.get(*self.get_dict[key]['args'])
                    self.get_dict[key]['completed'] = True
            await asyncio.sleep(0.01)

    def close_con(self):
        self.con.commit()
        self.con.close()

    def create_data_base(self):
        self.con.cursor().execute('CREATE TABLE actions (user_id INTEGER, time INTEGER, actions TEXT);')

    def get(self, table: str, selectData: str, condition = '', type = ''):
        cursor = self.con.cursor()
        if condition == '':
            cursor.execute(f'SELECT {selectData} FROM {table}')
        else:
            cursor.execute(f'SELECT {selectData} FROM {table} WHERE {condition}')
        return ((cursor.fetchall()) if type == "all" else (cursor.fetchone()))

    async def get_async(self, table: str, selectData: str, condition = '', type = ''):
        key = str(randrange(10000000))
        self.get_dict[key] = {'completed': False, 'args': [table, selectData, condition, type]}
        while True:
            if self.get_dict[key]['completed'] == True:
                return self.get_dict.pop(key)['result']
            await asyncio.sleep(0.01)

    def update(self, table: str, updateData: str, condition: str):
        self.con.cursor().execute(f'UPDATE {table} SET {updateData} WHERE {condition}')
        self.con.commit()

    def update_async(self, table: str, updateData: str, condition: str):
        self.update_list.append([table, updateData, condition])

    def delete(self, table: str, condition=''):
        if condition == '':
            self.con.cursor().execute(f'DELETE FROM {table}')
        else:
            self.con.cursor().execute(f'DELETE FROM {table} WHERE {condition}')
        self.con.commit()

    def delete_async(self, table: str, condition=''):
        self.delete_list.append([table, condition])

    def insert(self, table: str, values: str):
        self.con.cursor().execute(f'INSERT INTO {table} VALUES ({values})')
        self.con.commit()

    def insert_async(self, table: str, values: str):
        self.insert_list.append([table, values])

    def getTablesList(self):
        cursor = self.con.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return cursor.fetchall()