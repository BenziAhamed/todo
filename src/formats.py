# -*- coding: utf-8 -*-
import alfred
import config
from uuid import uuid4
import config_keys as ck
import os

mapping = {
'.yaml': { 'title': 'Classic YAML', 'subtitle': 'extension: .yaml' },
'.taskpaper': { 'title': 'Taskpaper', 'subtitle': 'extension: .taskpaper' },
'.json': { 'title': 'JSON', 'subtitle': 'extension: .json' }
}

def feedback_item(format, is_default=False):
    return alfred.Item(
        attributes={'uid': uuid4(),'arg': format, 'valid':'no' if is_default else 'yes'},
        title=mapping[format]['title'],
        subtitle=mapping[format]['subtitle'],
        icon='todo_edit.png' if is_default else 'icon.png'
    )

def generate_view():
    feedback_items = []
    current = default_format()
    for format in mapping:
        feedback_items.append(feedback_item(format, format==current))
    alfred.write(alfred.xml(feedback_items))

def default_format():
    format = config.get(ck.KEY_FORMAT_DEFAULT)
    if format == 'todo.keyvalue.none':
        return ".yaml"
    return format

def set_format(format):
    config.put(ck.KEY_FORMAT_DEFAULT, format)
    # check if the current todo db exists
    # if not, update its extension
    todo_db = config.get(ck.KEY_TODO)
    if not todo_db.endswith(format):
        config.put(ck.KEY_TODO, os.path.splitext(todo_db)[0]+format)
    print mapping[format]['title'] + ' is now default'

def main():
    (option, query) = alfred.args2()
    option_actions = {
        '-view' : lambda x: generate_view(),
        '-set': lambda x: set_format(x)
    }
    option_actions[option](query)
    config.commit()


if __name__ == '__main__':
    main()