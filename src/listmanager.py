# -*- coding: utf-8 -*-
import os
from uuid import uuid4

import config
import config_keys as ck
import helpers
import alfred
import store
import store_rtm as rtm


# The list of supported file type we have
supported_formats = ['.yaml','.taskpaper','.json','.rtm-todolist']

def generate_feedback(path, todo_file, active=False):
    ext = os.path.splitext(todo_file)[1]
    icon = "todo_edit.png" if active else "icon.png"
    if ext=='.rtm-todolist':
        icon='rtm.png'
    return alfred.Item(
        attributes={
            'uid': uuid4(),
            'arg': os.path.join(path, todo_file),
            'valid': 'yes' #if not active else 'no'
        },
        title=friendly_file(todo_file),
        subtitle=("[active]" if active else ""),
        icon=icon
    )

def generate_action_feedback(action='',title='',subtitle='',icon='icon.png'):
    return alfred.Item(
        attributes={
            'uid': uuid4(),
            'arg': action,
            'valid': 'yes'
        },
        title=title,
        subtitle=subtitle,
        icon=icon
    )


def friendly_file(todo_file):
    friendly = todo_file
    for f in supported_formats:
        friendly = friendly.replace(f,'')
    return friendly

def default_format():
    format = config.get(ck.KEY_FORMAT_DEFAULT)
    if format == 'todo.keyvalue.none':
        return ".yaml"
    return format


def generate_add_feedback(path, todo_file):
    todo_file = helpers.cleanup_filename(todo_file)
    return alfred.Item(
        attributes={
            'uid': uuid4(),
            'arg': os.path.join(path, todo_file+default_format()),
            'valid': 'yes' if todo_file != 'config' else 'no'
        },
        title="New list '" + todo_file + "'",
        subtitle="Format is: " + default_format(),
        icon="todo_add.png"
    )


def generate_view_rtm(feedback_items):
    # check if have RTM enabled
    if rtm.is_enabled():
        # not authenticated, and not started on
        if not rtm.is_authenticated():
            if not rtm.auth_in_progress() or rtm.auth_outdated():
                # add option to initiate auth
                feedback_items.append(generate_action_feedback(
                    title='[Authorize Todo]',
                    subtitle='Allow Todo to access your lists and tasks on RTM',
                    icon='rtm.png',
                    action='action.rtm.init_auth'
                ))
            else:
                feedback_items.append(generate_action_feedback(
                    title='[Load Lists]',
                    subtitle='Once you have authorized Todo in your browser, select this option',
                    icon='rtm.png',
                    action='action.rtm.end_auth'
                ))
        else:
            # utility to force a refresh of all items
            feedback_items.append(generate_action_feedback(
                title='[Refresh Lists]',
                icon='rtm.png',
                action='action.rtm.refresh'
            ))
        return True
    return False

def generate_view(query):
    feedback_items = []
    special_added = generate_view_rtm(feedback_items)

    lists, active = get_todo_lists()
    (path, db) = os.path.split(config.get(ck.KEY_TODO))
    lists = [f for f in lists if len(query) == 0 or friendly_file(f).lower().find(query.lower()) >= 0]
    feedback_items = feedback_items + map(lambda x: generate_feedback(path, x, x == active), lists)
    if len(feedback_items) == 0 or (special_added and len(feedback_items) == 1):
        feedback_items.append(generate_add_feedback(path, query))
    alfred.write(alfred.xml(feedback_items))


def is_supported_file(_file):
    for f in supported_formats:
        if _file.endswith(f):
            if f=='.rtm-todolist':
                return rtm.is_enabled() and rtm.is_authenticated()
            return True
    return False


def get_todo_lists():
    (path, db) = os.path.split(config.get(ck.KEY_TODO))
    lists = [f for f in os.listdir(path) if is_supported_file(f)]
    # remove config.yaml
    if 'config.yaml' in lists:
        lists.remove('config.yaml')
    if len(lists) == 0:
        lists.append('todo' + default_format())
        config.put(ck.KEY_TODO, os.path.join(path, 'todo'+default_format()))
    return sorted(lists), db


def action_rtm_init_auth():
    rtm.init_auth()

def action_rtm_end_auth():
    rtm.end_auth()
    action_rtm_refresh()

def action_rtm_refresh():
    rtm.refresh_lists()

def action(query):
    if query.startswith("action."):
        # custom actions from list view
        # for now, its all todo with Remember the Milk
        action_options = {
            'action.rtm.init_auth': lambda: action_rtm_init_auth(),
            'action.rtm.end_auth': lambda: action_rtm_end_auth(),
            'action.rtm.refresh': lambda: action_rtm_refresh()
        }
        action_options[query]()
        alfred.show('list ')
    else:
        todo_file = query
        if todo_file!=config.get(ck.KEY_TODO):
            if not os.path.exists(todo_file):
                store.Store().get_store(todo_file).clear_all_todos()
            config.put(ck.KEY_TODO, todo_file)
        alfred.show('todo ')



def delete_list(todo_file):
    if not todo_file.startswith('action.'):
        (path, todo_filename) = os.path.split(todo_file)
        # rtm special
        if todo_filename.endswith('.rtm-todolist'):
            if todo_filename.startswith("Inbox"):
                print "Cannot delete Inbox"
                todo_file = ''
            else:
                print "Deleting an RTM list is currently not allowed"
                todo_file = ''
        else:
            if os.path.exists(todo_file):
                os.remove(todo_file)
            print "Removed list '" + friendly_file(todo_filename) + "'"
        # if we removed the active one, switch to a new active list
        lists, active = get_todo_lists()
        if todo_file==config.get(ck.KEY_TODO):
            config.put(ck.KEY_TODO, os.path.join(path, lists[0]))
    alfred.show('list ')


def active_list():
    (path, db) = os.path.split(config.get(ck.KEY_TODO))
    return db

def main():
    (option, query) = alfred.args2()
    option_actions = {
        # Lists
        '-view': lambda q: generate_view(q),
        '-action': lambda q: action(q),
        '-delete': lambda q: delete_list(q)
    }
    option_actions[option](query)
    config.commit()

if __name__ == '__main__':
    main()
