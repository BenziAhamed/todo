from collections import defaultdict
from datetime import datetime
import os
from uuid import uuid4

import config as cfg
import config_keys as ck
from topy import *
import parser
from datetime import datetime
from pprint import pprint
import itemlist
import codecs
import re

class TaskpaperStore:

    def __init__(self, store):
        self.store = store
        self.tp_todos = None
        self.refresh()

    def get_features(self):
        return []

    def refresh(self):
        if(os.path.exists(self.store)):
            TodoList.reset_id()
            self.tp_todos = Parser.list_from_file(self.store)

    def get_todo_list(self):
        todos = []
        if self.tp_todos:
            for todo_item in self.tp_todos.items:
                if todo_item.type == 'task':
                    todos.append(self.get_todo_from_item('default', todo_item))
                if todo_item.type == 'project' and todo_item.sub_tasks:
                    for sub_task in todo_item.sub_tasks.items:
                        if sub_task.type == 'task':
                            todos.append(self.get_todo_from_item(todo_item.title.content, sub_task))
        return todos[::-1]

    def get_todo_from_item(self, group, task):
        todo = {}
        todo['title'] = task.title.content.decode('utf-8')
        todo['done'] = task.title.is_done()
        todo['pinned'] = task.title.has_tag('@pinned')
        todo['due'] = None
        todo['group'] = group.replace(' ', '-').decode('utf-8')
        todo['id'] = task.title._id
        todo['created'] = datetime.now()

        self.get_tag_content(todo, 'due', task, '@due')

        smartcontent_tags = ['@web', '@file', '@app', '@folder']
        tag_actions = {
            '@web': lambda todo, task: self.set_smartcontent(todo, 'Web', task.title.get_tag_param('@web')),
            '@file': lambda todo, task: self.set_smartcontent(todo, 'File', task.title.get_tag_param('@file')),
            '@folder': lambda todo, task: self.set_smartcontent(todo, 'Folder', task.title.get_tag_param('@folder')),
            '@app': lambda todo, task: self.set_smartcontent(todo, 'Application', task.title.get_tag_param('@app'))
        }
        for tag in smartcontent_tags:
            if task.title.has_tag(tag):
                tag_actions[tag](todo, task)

        if todo['due'] and len(todo['due']) > 0:
            due, task = parser.get_due_and_task('@'+todo['due'])
            todo['due'] = due

        return todo

    def set_smartcontent(self, todo, _type, _info):
        todo['smartcontent_type'] = _type.decode('utf-8')
        todo['smartcontent_info'] = _info.decode('utf-8')


    def get_tag_content(self, todo, todo_tag, task, task_tag):
        if task.title.has_tag(task_tag):
            todo[todo_tag] = task.title.get_tag_param(task_tag)

    def save_todo_list(self, todos):
        tags = defaultdict(list)
        export_content = []
        for i in todos:
            tags[i['group']].append(
                {'title': i['title'],
                 'created': i['created'],
                 'due': itemlist.feature(i, 'due'),
                 'done': itemlist.feature(i, 'done'),
                 'smartcontent_type': itemlist.feature(i, 'smartcontent_type'),
                 'smartcontent_info': itemlist.feature(i, 'smartcontent_info'),
                 'pinned': itemlist.feature(i, 'pinned')
                 }
            )
        for tag in tags:
            # Project
            export_content.append(tag + ':')
            for todo in tags[tag]:
                todo_text = self.get_item_from_todo(todo)
                # print todo
                export_content.append('\t'+todo_text)
        with codecs.open(self.store, "w", "utf-8") as f:
            for item in export_content:
                f.write(item + u'\n')

        self.refresh()

    def get_item_from_todo(self, todo):
        todo_text = '- ' + todo['title']
        if itemlist.feature(todo,'due') is not None:
            todo_text = todo_text + " @due(" + str(todo['due']) + ")"

        smartcontent_type = itemlist.feature(todo,'smartcontent_type')
        if smartcontent_type and len(smartcontent_type) > 0:
            smartcontent_info = itemlist.feature(todo,'smartcontent_info')
            smartcontent_type_actions = {
            'Web': lambda x: x + " @web(" + smartcontent_info + ")",
            'File': lambda x: x + " @file(" + smartcontent_info + ")",
            'Folder': lambda x: x + " @folder(" + smartcontent_info + ")",
            'Application': lambda x: x + " @app(" + smartcontent_info + ")"
            }
            todo_text = smartcontent_type_actions[smartcontent_type](todo_text)

        if itemlist.feature(todo,'pinned') == True:
            todo_text = todo_text + " @pinned"
        if itemlist.feature(todo,'done') == True:
            todo_text = todo_text + " @done"
        return todo_text

    def clear_all_todos(self):
        open(self.store, 'w').close()
        self.refresh()

    def append_todo_list(self, todos):
        # existing_todos = self.get_todo_list()
        # existing_todos = existing_todos + todos
        # self.save_todo_list(existing_todos)
        if not os.path.exists(self.store):
            open(self.store, 'w').close()

        with codecs.open(self.store, "r", "utf-8") as f:
            lines = f.readlines()

        for todo in todos:
            lines = self.add_in_memory(lines, todo)

        with codecs.open(self.store, "w", "utf-8") as f:
            f.write("".join(lines))

        self.refresh()


    def save_todo(self, todo):
        # existing_todos = self.get_todo_list()
        # existing_todos.append(todo)
        # self.save_todo_list(existing_todos)
        # option 2
        if not os.path.exists(self.store):
            open(self.store, 'w').close()

        with codecs.open(self.store, "r", "utf-8") as f:
            lines = f.readlines()

        lines = self.add_in_memory(lines, todo)

        with codecs.open(self.store, "w", "utf-8") as f:
            f.write("".join(lines))

        self.refresh()

    def add_in_memory(self, lines, todo):
        existing = False
        task = self.get_item_from_todo(todo)
        tag = todo['group']
        for idx, line in enumerate(lines):
            if re.match('\s*' + tag + ':', line):
                tabs_no = line.find(tag[0])
                lines.insert(idx + 1, '\t' * tabs_no + '\t' + task + '\n')
                existing = True
                break
        if not existing:
            lines.append(tag+':\n')
            lines.append('\t'+task+'\n')
        return lines


    def get_todo(self, _id):
        all_items = self.get_todo_list()
        match = [t for t in all_items if t['id']==int(_id)]
        return match[0]

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
        with codecs.open(self.store, "r", "utf-8") as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            if re.match('\s*' + old_tag + ':', line):
                lines[idx] = new_tag+':\n'
                break
        with codecs.open(self.store, "w", "utf-8") as f:
            f.write("".join(lines))

def main():
    import sys
    from pprint import pprint
    store_file = sys.argv[1]
    datastore = TaskpaperStore()
    datastore.store = store_file
    datastore.get_todo('46')
    datastore.get_todo('46')
    datastore.get_todo('46')

if __name__ == '__main__':
    main()