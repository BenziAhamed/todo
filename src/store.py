# -*- coding: utf-8 -*-
import config
import config_keys as ck
from store_yaml import YamlStore
from store_taskpaper import TaskpaperStore
from store_json import JsonStore
from store_rtm import RtmStore


class Store:
    def __init__(self):
        todo_db = config.get(ck.KEY_TODO)
        self.instance = self.get_store(todo_db)

    def get_store(self, todo_db):
        if todo_db.endswith('.yaml'):
            return YamlStore(todo_db)
        elif todo_db.endswith('.taskpaper'):
            return TaskpaperStore(todo_db)
        elif todo_db.endswith('.json'):
            return JsonStore(todo_db)
        elif todo_db.endswith('.rtm-todolist'):
            return RtmStore(todo_db)
        return None




datastore = Store()

