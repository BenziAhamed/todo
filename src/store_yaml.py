# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime
import os
from uuid import uuid4

import config
import config_keys as ck
import helpers
import parser
import smartcontent
import unicodedata
import yaml
import itemlist


class YamlStore:

    def __init__(self, store):
        self.store = store

    def get_features(self):
        return []

    def get_todo_list(self):
        todos = []
        if(os.path.exists(self.store)):
            f = open(self.store)
            todos = yaml.load(f)
            if todos is None:
                todos = []
        return todos

    def save_todo_list(self, todos):
        if len(todos) > 0:
            with open(config.get(ck.KEY_TODO), 'w') as f:
                yaml.dump(todos, f)
        else:
            self.clear_all_todos()

    def clear_all_todos(self):
        open(self.store, 'w').close()

    def append_todo_list(self, todos):
        with open(self.store, 'a') as f:
            yaml.dump(todos, f)

    def save_todo(self, todo):
        self.append_todo_list([todo])

    def get_todo(self, _id):
        todos = self.get_todo_list()
        for todo in todos:
            if str(todo['id']) == _id:
                return todo

    def remove_todo(self, _id):
        todos = self.get_todo_list()
        if len(todos) > 0 and len(_id) > 0:
            toremove = [t for t in todos if str(t['id']) == _id]
            todos = [t for t in todos if str(t['id']) != _id]
            self.save_todo_list(todos)
            return toremove[0]

    def get_tags(self):
        todos = self.get_todo_list()
        tags = defaultdict(int)
        for i in todos:
            if not itemlist.feature(i, 'done'):
                tags[i['group']] = tags[i['group']] + 1
        return tags

    def remove_tag(self, tag):
        todos = self.get_todo_list()
        if len(todos) > 0 and len(tag) > 0:
            toremove = [t for t in todos if t['group'] == tag]
            todos = [t for t in todos if t['group'] != tag]
            self.save_todo_list(todos)


    def update_tag(self, old_tag, new_tag):
        todos = self.get_todo_list()
        for t in todos:
            if t['group'] == old_tag:
                t['group'] = new_tag
        self.save_todo_list(todos)

