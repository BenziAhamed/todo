import codecs
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, date
import json
import os
from pprint import pprint
from subprocess import call
from time import mktime
from uuid import UUID
from dateutil.relativedelta import *

import config
import config_keys as ck
from dateutil.parser import parse
import rtm
from rtm.rtm import dottedDict


# import listmanager
apikey = "e115e2073922ee144cd0d2a370d78b89"
secret = "0a7d9ad7b86da955"


def is_enabled():
    return config.get(ck.KEY_FEATURE_RTM) == True


def is_authenticated():
    token = config.get(ck.KEY_RTM_TOKEN)
    if token != "todo.keyvalue.none" and len(token) > 0:
        # check if the token available is still valid
        # api = rtm.createRTM(apikey, secret, token)
        # try:
        #    api.get(method='rtm.auth.checkToken',auth_token=token)
            return True
        # except:
        #    pass
    return False


def auth_in_progress():
    return config.get(ck.KEY_RTM_AUTH_INPROGRESS) == True


def init_auth():
    api = rtm.createRTM(apikey, secret, token=None)
    config.put(ck.KEY_RTM_AUTH_INPROGRESS, True)
    config.put(ck.KEY_RTM_FROB, api.getFrob())
    config.put(ck.KEY_RTM_AUTH_STARTED, mktime(datetime.now().timetuple()))
    call(['open', api.getAuthURL()])


def auth_outdated():
    if not auth_in_progress():
        return False
    started = config.get(ck.KEY_RTM_AUTH_STARTED)
    now = mktime(datetime.now().timetuple())
    return (now-started) > 180  # 3 minutes


def end_auth():
    api = rtm.createRTM(apikey, secret, token=None)
    api.setFrob(config.get(ck.KEY_RTM_FROB))
    token = api.getToken()
    config.put(ck.KEY_RTM_TOKEN, token)
    config.put(ck.KEY_RTM_AUTH_INPROGRESS, False)


def create_rtm():
    token = config.get(ck.KEY_RTM_TOKEN)
    return rtm.createRTM(apikey, secret, token)


def refresh_lists():
    if not is_enabled() or not is_authenticated():
        return

    (path, db) = os.path.split(config.get(ck.KEY_TODO))

    if is_authenticated():
        api = create_rtm()
        s = api.settings.getList()
        lists = api.lists.getList()
        for l in lists.lists.list:
            if l.archived == '0' and l.smart == '0' and l.deleted == '0':
                if l.name == 'Sent':
                    return
                info = {'id': l.id,'name':l.name}
                # now that we have a list of todos, create local copies
                # of list files as reference, in JSON format
                # filename = 'name.rtm-todolist'
                list_file = os.path.join(path, l.name+'.rtm-todolist')
                if os.path.exists(list_file):
                    os.remove(list_file)
                with codecs.open(list_file, "w", "utf-8") as f:
                    json.dump(info, f)
                if s.settings.defaultlist == l.id:
                    config.put(ck.KEY_TODO, list_file)


def get_timeline():
    # check if we have a saved timeline
    tl = config.get(ck.KEY_RTM_TIMELINE, None)
    tl_age = config.get(ck.KEY_RTM_TIMELINE_AGE, 0)
    diff = mktime(datetime.now().timetuple()) - tl_age
    # check if we need to refresh
    if tl is None or diff > 86400:
        api = create_rtm()
        config.put(ck.KEY_RTM_TIMELINE, api.timelines.create().timeline)
        config.put(ck.KEY_RTM_TIMELINE_AGE, mktime(datetime.now().timetuple()))
    return config.get(ck.KEY_RTM_TIMELINE, None)


def reset():
    config.put(ck.KEY_RTM_TOKEN, '')
    config.put(ck.KEY_RTM_FROB, '')
    config.put(ck.KEY_RTM_AUTH_INPROGRESS, False)
    config.put(ck.KEY_RTM_AUTH_STARTED, 0)
    config.put(ck.KEY_RTM_TIMELINE, 0)
    config.put(ck.KEY_RTM_TIMELINE_AGE, 0)

    (path, db) = os.path.split(config.get(ck.KEY_TODO))

    # delete all saved lists
    lists = [f for f in os.listdir(path) if f.endswith('.rtm-todolist')]
    for l in lists:
        l = os.path.join(path, l)
        if os.path.exists(l):
            os.remove(l)

    # reset to the top active list
    # TODO:
    # lists, active = listmanager.get_todo_lists()
    # config.put(ck.KEY_TODO, os.path.join(path, lists[0]))


class CustomEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj)
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, date):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class RtmStore:

    def __init__(self, store):
        self.store = store
        self.api = create_rtm()
        self.load_info()

    def get_features(self):
        f = ['update_todo']
        return f

    def load_info(self):
        if not os.path.exists(self.store):
            return
        # load the list id
        with codecs.open(self.store, "r", "utf-8") as f:
            list_info = json.load(f)
            self.list_id = list_info['id']
            self.list_name = list_info['name']
            self.list_info = list_info
            if 'todo_list' in self.list_info:
                todos = self.list_info['todo_list']
                for t in todos:
                    # custom decoding of JSON dump
                    t['created'] = parse(t['created'])
                    if 'due' in t and t['due'] is not None:
                        t['due'] = parse(t['due']).date() + relativedelta(days=+1)
                self.list_info['todo_list'] = todos

    def get_todo_list(self):
        return self.cached_todo_list(aged=True)

    def cached_todo_list(self, aged=False):
        if aged:
            if 'todo_list' in self.list_info:
                # we have a cached value
                # check if its up to date
                diff = mktime(datetime.now().timetuple()) - self.list_info['cache_at']
                if diff > 300:
                    return self.invalidate()
            else:
                return self.invalidate()
        return deepcopy(self.list_info['todo_list'])

    def invalidate(self):
        todos = []
        rsp = self.api.tasks.getList(list_id=self.list_id)

        # check not empty list
        if hasattr(rsp.tasks.list, 'taskseries'):
            # many tasks
            if isinstance(rsp.tasks.list.taskseries, list):
                for t in rsp.tasks.list.taskseries:
                    todos.append(self.convert_todo(t))
            else:
                # just 1 task
                t = rsp.tasks.list.taskseries
                todos.append(self.convert_todo(t))
        self.list_info['todo_list'] = todos
        self.list_info['cache_at'] = mktime(datetime.now().timetuple())
        with codecs.open(self.store, "w", "utf-8") as f:
            json.dump(self.list_info, f, indent=True, cls=CustomEncoder)
        self.load_info()
        return deepcopy(self.list_info['todo_list'])

    def convert_todo(self, t):
        todo = {}
        todo['id'] = '.'.join([self.list_id, t.id, t.task.id])
        todo['title'] = t.name
        todo['created'] = t.task.added
        todo['done'] = (t.task.completed != '')
        if t.task.due != '':
            todo['due'] = parse(t.task.due).date()
        todo['pinned'] = (t.task.priority != 'N')
        if isinstance(t.tags, list):
            # no tags
            todo['group'] = 'default'
        else:
            tag = t.tags.__dict__().itervalues().next()
            if isinstance(tag, list):
                # multiple tags
                todo['group'] = tag[0]
            else:
                # only 1 tag
                todo['group'] = tag
        return todo

    def save_todo_list(self, todos):
        # pretty lame
        self.clear_all_todos(invalidate=False)
        for t in todos:
            self.save_todo(t, invalidate=False)
        self.invalidate()

    def clear_all_todos(self, invalidate=True):
        for t in self.get_todo_list():
            self.delete_todo(t)
        if invalidate:
            self.invalidate()

    def delete_todo(self, todo):
        list_id, taskseries_id, task_id = todo['id'].split('.')
        self.api.tasks.delete(timeline=get_timeline(), list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)

    def append_todo_list(self, todos):
        for t in todos:
            self.save_todo(t, invalidate=False)
        self.invalidate()

    def save_todo(self, todo, invalidate=True):
        # convert this to the smart info syntax for RTM
        # we will add the task title at the end - TODO for smartcontent
        task = todo['title']
        smart_task = task
        # due date
        if 'due' in todo and todo['due'] is not None:
            smart_task += ' ^'+str(todo['due'])
        # pinned = priority
        if 'pinned' in todo:
            if todo['pinned'] == True:
                smart_task += ' !1'
        # tags
        if todo['group'] != 'default':
            smart_task += ' #' + todo['group']

        # add the item
        self.api.tasks.add(timeline=get_timeline(), list_id=self.list_id, name=smart_task, parse='1')
        if invalidate:
            self.invalidate()

    def update_todo(self, todo):
        # check if this is a toggle of done
        # if so, we just set to completed the item
        # else, delete the item and add a new item again
        list_id, taskseries_id, task_id = todo['id'].split('.')

        def change_item(api_call, list_id, taskseries_id, taskseries, **params):
            api_call(timeline=get_timeline(), list_id=list_id, taskseries_id=taskseries_id,task_id=task_id,**params)
            self.invalidate()

        cached = [t for t in self.get_todo_list() if t['id'] == todo['id']][0]
        if cached['done'] != todo['done']:
            # we just need to update the completed status
            api_call = self.api.tasks.complete if todo['done'] else self.api.tasks.uncomplete
            change_item(api_call, list_id, taskseries_id, task_id)

        elif cached['pinned'] != todo['pinned']:
            priority = '1' if todo['pinned'] else ''
            change_item(self.api.tasks.setPriority, list_id, taskseries_id, task_id, priority=priority)

        else:
            # just delete and re-insert a new item
            # lame...
            self.api.tasks.delete(timeline=get_timeline(), list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)
            self.save_todo(todo)

    def get_todo(self, _id):
        todo = [t for t in self.get_todo_list() if t['id'] == _id]
        return todo[0]

    def remove_todo(self, _id):
        # this should return the info
        # about the item deleted
        to_remove = [t for t in self.get_todo_list() if t['id'] == _id]
        timeline = get_timeline()
        list_id, taskseries_id, task_id = _id.split('.')
        self.api.tasks.delete(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)
        self.invalidate()
        return to_remove[0]

    def get_tags(self):
        todos = self.get_todo_list()
        tags = defaultdict(int)
        for i in todos:
            if not 'done' in i or i['done'] == False:
                tags[i['group']] = tags[i['group']] + 1
        return tags

    def remove_tag(self, tag):
        for t in self.get_todo_list():
            if t['group'] == tag:
                self.delete_todo(t)
        self.invalidate()

    def update_tag(self, old_tag, new_tag):
        if new_tag == 'default':
            new_tag=''
        for t in self.get_todo_list():
            if t['group'] == old_tag:
                list_id, taskseries_id, task_id = t['id'].split('.')
                self.api.tasks.setTags(timeline=get_timeline(), list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=new_tag)
        self.invalidate()

