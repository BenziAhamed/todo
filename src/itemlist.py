# -*- coding: utf-8 -*-
import Queue
from collections import defaultdict
from datetime import datetime
import os
import threading
from uuid import uuid4

import config
import config_keys as ck
import helpers
import parser
import smartcontent
import unicodedata
from store import datastore


# ---------------------------------------------------------
# overall list management

# clears out eveything - practically deletes
# the todo list file


def clear_all_todos():
    datastore.instance.clear_all_todos()
    config.update_state(command='clear_todos')


# clear items based on 'done' status
def clear_todos(done=False):
    todos = datastore.instance.get_todo_list()
    todos = [t for t in todos if feature(t, 'done') != done]
    datastore.instance.save_todo_list(todos)
    config.update_state(command='clear_todos')

# gets the list of todo items


def get_todo_list():
    return datastore.instance.get_todo_list()

# saves the todo list to file
# if an empty list if passed, it will
# delete the existing todo db file


def save_todo_list(todos):
    datastore.instance.save_todo_list(todos)

# appends a list of todo items to the todo
# db file


def append_todo_list(todos):
    datastore.instance.append_todo_list(todos)

# ---------------------------------------------------------
# todo management


def save_todo(raw_task, silent=False):
    newtodo = parse_todo_text(raw_task)
    task = newtodo['title']
    tag = newtodo['group']
    if len(task) == 0:
        return

    smartcontent.process_todo(newtodo)
    datastore.instance.save_todo(newtodo)

    if not silent:
        if tag != 'default':
            print ("Added '" + task + "' tagged #" + tag).encode('utf-8')
        else:
            print ("Added '" + task + "'").encode('utf-8')

    config.put(ck.KEY_USER_QUERY_NOITEMPREFIX, '')
    config.update_state(command='add_todo', tag='#'+tag)


def import_todo_items(contents):
    new_todos = []
    for t in contents:
        new_todos.append(parse_todo_text(t))
    for t in new_todos:
        smartcontent.process_todo(t)
    datastore.instance.append_todo_list(new_todos)
    return {'imported': len(new_todos)}


def import_worker(work_q, done_q):
    while True:
        content = work_q.get()
        try:
            todo = parse_todo_text(content)
            smartcontent.process_todo(todo)
            done_q.put(todo)
        except:
            pass
        work_q.task_done()


def import_todo_items_threaded2(contents):
    work_q = Queue.Queue()
    done_q = Queue.Queue()

    # create a fixed numbner of threads
    for i in range(10):
        t = threading.Thread(target=import_worker, args=(work_q, done_q))
        t.daemon = True
        t.start()

    for c in contents:
        work_q.put(c)

    work_q.join()
    new_todos = []
    while not done_q.empty():
        new_todos.append(done_q.get())
    datastore.instance.append_todo_list(new_todos)
    return {'imported': len(new_todos)}


def parse_todo_text(text):
    info = parser.parse(text)
    tag = info['tag']
    task = info['task']
    pinned = info['pinned']
    due = info['due']
    if tag is None:
        tag = 'default'
    newtodo = {
        'title': task if len(task) != 2 else task + '  ',
        'created': datetime.now(),
        'id': uuid4(),
        'group': tag,
        'pinned': pinned,
        'due': due
    }
    return newtodo


def get_todo(_id):
    return datastore.instance.get_todo(_id)


def remove_todo(_id):
    removed = datastore.instance.remove_todo(_id)
    config.update_state(command='remove_todo', tag='#'+removed['group'])
    print ("Removed '" + removed['title'] + "'").encode('utf-8')


def update_todo(_id, values):
    todos = get_todo_list()
    if len(todos) > 0 and len(_id) > 0:
        for t in todos:
            if str(t['id']) == _id:
                for key in values:
                    t[key] = values[key]
                    if key == 'title':
                        smartcontent.process_todo(t)
                todo = t
                break
    if 'update_todo' in datastore.instance.get_features():
        datastore.instance.update_todo(todo)
    else:
        datastore.instance.save_todo_list(todos)

def update_tag(old_tag, new_tag):
    datastore.instance.update_tag(old_tag, new_tag)

def toggle_pinned(_id):
    todo = get_todo(_id)
    toggle = False if feature(todo, 'pinned') else True
    update_todo(_id, {'pinned': toggle})
    config.update_state(command='toggle_pinned', tag='#'+todo['group'])


def toggle_done(_id):
    todo = get_todo(_id)
    toggle = False if feature(todo, 'done') else True
    update_todo(_id, {'done': toggle, 'done_when': datetime.now()})
    config.update_state(command='toggle_done', tag='#'+todo['group'])

# ---------------------------------------------------------
# tag management


def get_tags():
    return datastore.instance.get_tags()


def remove_tag(tag):
    datastore.instance.remove_tag(tag)
    config.update_state(command='remove_tag', tag='#'+tag)
    print ("Removed all items tagged #" + tag).encode('utf-8')

# ---------------------------------------------------------
# generic functions


def remove_item(item):
    if helpers.is_todo(item):
        remove_todo(helpers.extract_todo_id(item))
    elif helpers.is_tag(item):
        remove_tag(helpers.extract_tag(item))

def copy_todo_to_clipboard(_id):
    todo = datastore.instance.get_todo(_id)
    title = todo['title']
    tag = todo['group']
    helpers.macSetClipboard(title)
    config.update_state(command='copy_to_clipboard', tag='#'+tag)
    print ("Copied '" + title + "' to the clipboard").encode('utf-8')


def copy_text_to_clipboard(text):
    helpers.macSetClipboard(text)
    config.update_state(command='copy_to_clipboard')
    print ("Copied '" + title + "' to the clipboard").encode('utf-8')

# Since these feature have been added after v0.2
# and the YAML file will not have these by default
# features should be extracted safely


def feature(todo, feature):
    if feature == 'pinned':
        return get_item_key(todo, feature, False)
    elif feature == 'due':
        return get_item_key(todo, feature, None)
    elif feature == 'done':
        done = get_item_key(todo, feature, False)
    elif feature == 'done_when':
        return get_item_key(todo, feature, datetime.now())
    elif feature == 'smartcontent_info':
        return get_item_key(todo, feature, '')
    elif feature == 'smartcontent_type':
        return get_item_key(todo, feature, '')
    return todo[feature]


def get_item_key(todo, key, default):
    if key not in todo:
        todo[key] = default
    return todo[key]


def main():
    pass

if __name__ == '__main__':
    main()
