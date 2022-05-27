import re
import sqlite3
import os
from datetime import datetime

class DataBase:
    def __init__(self, date: str, make_db=True, file_name=None):
        self.con = None
        self.last_update = datetime.now()

        if file_name is None:
            file_name = f'{os.path.dirname(__file__)}/data/{date}.db'
        self.file_name = file_name
        try:
            f = open(file_name, "r", encoding="utf-8")
            f.close()
            self.valid = True
        except FileNotFoundError:
            if make_db:
                open(file_name, "a", encoding="utf-8")
                self.create_data_base()
                self.valid = True
            else:
                self.valid = False

    def update_con(self):
        delta = datetime.now() - self.last_update
        if self.con is None:
            self.last_update = datetime.now()
            self.con = sqlite3.connect(self.file_name)
        elif delta.total_seconds() >= 5:
            self.last_update = datetime.now()
            self.con.commit()
            self.con.close()
            self.con = sqlite3.connect(self.file_name)

    def close_con(self):
        self.con.commit()
        self.con.close()

    def create_data_base(self):
        self.update_con()
        self.con.cursor().execute('CREATE TABLE actions (user_id INTEGER, time DATETIME, actions TEXT);')

    def get(self, table: str, selectData: str, condition = '', type = ''):
        self.update_con()
        cursor = self.con.cursor()
        if condition == '':
            cursor.execute(f'SELECT {selectData} FROM {table}')
        else:
            cursor.execute(f'SELECT {selectData} FROM {table} WHERE {condition}')
        return ((cursor.fetchall()) if type == "all" else (cursor.fetchone()))

    def update(self, table: str, updateData: str, condition: str):
        self.update_con()
        self.con.cursor().execute(f'UPDATE {table} SET {updateData} WHERE {condition}')

    def delete(self, table: str, condition=''):
        self.update_con()
        if condition == '':
            self.con.cursor().execute(f'DELETE FROM {table}')
        else:
            self.con.cursor().execute(f'DELETE FROM {table} WHERE {condition}')

    def insert(self, table: str, values: str):
        self.update_con()
        self.con.cursor().execute(f'INSERT INTO {table} VALUES ({values})')
        self.con.commit()

    def getTablesList(self):
        self.update_con()
        cursor = self.con.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return cursor.fetchall()