# -*- coding: utf-8 -*-

from uuid import uuid4

import alfred
import parser
import itemlist
import helpers
import config
import config_keys as ck


def generate_noitems_feedbackitem(query, info):
    return alfred.Item(
        attributes={
            'uid': uuid4(),
            'arg': '',
            'valid': 'no'
        },
        title="No items found",
        subtitle="",
        icon="todo_done.png"
    )


def generate_done_feedbackitem(t, info):
    return alfred.Item(
        attributes={
            'uid': uuid4(),
            'arg': helpers.encode_todo_id(str(t['id'])),
            'autocomplete': helpers.create_autocomplete(t, info)
        },
        title=helpers.create_title(t),
        subtitle=helpers.create_subtitle(t),
        icon="todo_done.png"
    )


def generate_view(query):
    info = parser.parse(query)
    tag = info['tag']
    task = info['task']
    due = info['due']
    todos = itemlist.get_todo_list()
    done = [t for t in todos if helpers.apply_filter(t, task, tag, due, q_done=True)]
    done = done[::-1]

    feedback_items = []
    if len(done) == 0:
        feedback_items.append(generate_noitems_feedbackitem(query, info))
    else:
        done = map(lambda x: generate_done_feedbackitem(x, info), done)
        feedback_items = done

    alfred.write(alfred.xml(feedback_items))

def main():
    (option, query) = alfred.args2()
    option_actions = {
        '-view': lambda q: generate_view(q)
    }
    option_actions[option](query)
    config.commit()

if __name__ == '__main__':
    main()
