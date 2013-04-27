# -*- coding: utf-8 -*-

import sys
import config
from collections import defaultdict
import itemlist
import alfred
from uuid import uuid4
import config_keys as ck


def export_txt(_tag=None):
    todos = itemlist.get_todo_list()
    tags = defaultdict(list)
    for i in todos:
        if not itemlist.feature(i, 'done'):
            tags[i['group']].append(
                {	'title': i['title'],
                  'created': i['created'],
                  'pinned': itemlist.feature(i, 'pinned'),
                  'due': itemlist.feature(i, 'due')
                  }
            )
    sorted_tags = sorted(tags, key=lambda x: x)
    for tag in sorted_tags:
        if _tag is None or tag == _tag:
            print u'#' + tag.encode('utf-8')
            pinned = [t for t in tags[tag] if t['pinned']]
            normal = [t for t in tags[tag] if not t['pinned']]
            for todo in pinned:
                print get_todo_text(todo)
            for todo in normal:
                print get_todo_text(todo)
            print " "


def get_todo_text(todo):
    pinned = todo['pinned']
    has_due = todo['due'] is not None
    due_text = "" if not has_due else (" @" + str(todo['due']))
    if pinned:
        return u'!! ' + todo['title'].encode('utf-8') + due_text.encode('utf-8')
    else:
        return todo['title'].encode('utf-8') + due_text.encode('utf-8')

def generate_feedbackitem(t):
    return alfred.Item(
        attributes={
            'uid': uuid4(),
            'arg': t['arg']
        },
        title=t['title'],
        subtitle=t['subtitle'],
        icon=t['icon']
    )

def generate_noitems():
    return alfred.Item(
        attributes={
            'uid': uuid4(),
            'arg': '',
            'valid': 'no'
        },
        title="Your todo list is empty",
        subtitle='You need to create some items first to export',
        icon="todo_export.png"
    )

def generate_export_view():
    feedback_items = []
    todos = itemlist.get_todo_list()
    if len(todos) == 0:
        feedback_items.append(generate_noitems())
    else:
        items = []
        items.append({'title': 'Export as plain text - clipboard', 'subtitle': '', 'arg': 'txt', 'icon': 'export_txt.png'})
        # Export by tag name
        todos = itemlist.get_todo_list()
        tags = defaultdict(list)
        for i in todos:
            tags[i['group']].append(1)
        for tag in tags:
            if tag != 'default':
                items.append({'title': u'Export #' + tag, 'subtitle': '{0} {1}'.format(len(tags[tag]), 'item' if len(tags[tag]) == 1 else 'items'), 'arg': 'txt ' + tag, 'icon': 'export_txt.png'})

        feedback_items = map(lambda x: generate_feedbackitem(x), items)
    alfred.write(alfred.xml(feedback_items))

def main():
    if len(sys.argv) == 1:
        generate_export_view()
    else:
        format = sys.argv[1]
        tag = None
        if len(sys.argv) == 3:
            tag = sys.argv[2]
        if format == "txt":
            export_txt(_tag=tag)
    config.commit()


if __name__ == "__main__":
    main()
