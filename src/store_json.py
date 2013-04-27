# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime, date
import os
from uuid import uuid4, UUID

import config
import config_keys as ck
import helpers
import parser
import smartcontent
import unicodedata
import json
import itemlist

from dateutil.parser import parse

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj)
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, date):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class JsonStore:

    def __init__(self, store):
        self.store = store

    def get_features(self):
        return []

    def get_todo_list(self):
        todos = []
        if(os.path.exists(self.store)):
            f = open(self.store)
            todos = json.load(f)

            for t in todos:
                # custom decoding
                t['created'] = parse(t['created'])
                if 'due' in t and t['due'] is not None:
                    t['due'] = parse(t['due']).date()

            if todos is None:
                todos = []
        return todos

    def save_todo_list(self, todos):
        if len(todos) > 0:
            with open(config.get(ck.KEY_TODO), 'w') as f:
                json.dump(todos, f, indent=True, cls=CustomEncoder)
        else:
            self.clear_all_todos()

    def clear_all_todos(self):
        with open(self.store, 'w') as f:
            json.dump([],f)

    def append_todo_list(self, todos):
        current_todos = self.get_todo_list()
        current_todos = current_todos + todos
        self.save_todo_list(current_todos)

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
