# -*- coding: utf-8 -*-

from uuid import uuid4

import alfred
import parser
import itemlist
import helpers
import config
from datetime import date
import config_keys as ck


# for what it's worth, quickcreate is slightly buggy
def quickcreate_enabled():
    return config.get(ck.KEY_FEATURE_QUICKCREATE) == True


def generate_add_feedbackitem(query, info):
    q = info['task']
    tag = info['tag']
    pinned = info['pinned']
    due = info['due']
    clear_due = info['clear_due']

    title = "New item '" + ('...' if len(q) == 0 else q) + "'"
    subtitle = "Type something to create a new todo"

    if tag is None:
        tag = 'default'

    # generate the subtitle, based on sections entered
    # pin, tag, due date
    s_subtitle = []
    if pinned:
        s_subtitle.append("pinned item")
    if due and not clear_due:
        s_subtitle.append(helpers.due_date_text(due))
    if tag != 'default':
        s_subtitle.append("#{0}".format(tag))

    if len(s_subtitle) > 0:
        subtitle = " ".join(s_subtitle)

    quick_create = False
    if quickcreate_enabled():
        quick_create = True
        config.update_state(command='quick_create', tag='#'+tag)

    if quick_create:
        return alfred.Item(
            attributes={
                'uid': uuid4(),
                'arg': query,
                'valid': 'no',
                'autocomplete': ''
            },
            title=title,
            subtitle=subtitle,
            icon="todo_add.png"
        )
    else:
        return alfred.Item(
            attributes={
                'uid': uuid4(),
                'arg': query,
                'valid': 'no' if len(q) == 0 else 'yes'
            },
            title=title,
            subtitle=subtitle,
            icon="todo_add.png"
        )


def generate_todo_feedbackitem(t, info):
    return alfred.Item(
        attributes={
            'uid': uuid4(),
            'arg': helpers.encode_todo_id(str(t['id'])),
            'autocomplete': helpers.create_autocomplete(t, info)
        },
        title=helpers.create_title(t),
        subtitle=helpers.create_subtitle(t),
        icon=helpers.create_icon(t)
    )


def generate_view(query, info):

    # The following works only if QuickCreate is enabled
    #
    # Quick create works by utilizing the fact that Alfred
    # will autocomplete a non-valid item. In quick create mode,
    # the user entered query is always saved, and the add item
    # feedback option is marked as non-valid. So when the user
    # hits Enter, autocomplete will kick in, the query will become
    # an empty string. By knowing that we have a zero length query
    # and that the last command was quick_create (set when a add item
    # option is displayed), we know that we have to add the previous
    # user query.
    #
    # The only drawback is that if the user deletes what was typed,
    # this mode will kick-in and create unintended todo items.
    # From a state machine perspective, there is currently not enough
    # information from Alfred to detect backspace/word deletes, and
    # so this simply *cannot* be fixed. One can always disable the
    # feature though :-)
    #
    # Also, possible Alfred bug, if you press escape, Alfred fires your keyword
    # with an empty query, so your script will execute even with Alfred not
    # being visible...
    #
    # Hmmm.
    if quickcreate_enabled():
        if len(query) == 0 and config.get(ck.KEY_COMMAND_LAST) == 'quick_create':
            add_query = config.get(ck.KEY_USER_QUERY)
            itemlist.save_todo(add_query, silent=True)
            config.update_state(command='')
        # always save the user's query to be used for later processing
        config.put(ck.KEY_USER_QUERY, query)

    tag = info['tag']
    task = info['task']
    due = info['due']
    feedback_items = []

    # check if have a task that previously matched
    # a prefix task string that did not yield any results
    # in that case, we can just show the add new item
    # feedback option immediately
    noitemprefix = config.get(ck.KEY_USER_QUERY_NOITEMPREFIX)
    if len(noitemprefix) > 0 and query.startswith(noitemprefix) and len(task) > 0:
        feedback_items.append(generate_add_feedbackitem(query, info))
    else:

        # Record the existence of an explicit user tag
        # This is used for command continuation scenarios
        # e.g. add a new item tagged #tag and Todo will resume
        # with #tag pre-filled
        config.put(ck.KEY_USER_QUERY_HASTAG, tag is not None)

        todos = itemlist.get_todo_list()
        filtered = [t for t in todos if helpers.apply_filter(t, task, tag, due)]

        # If we did not find any items that match the user query,
        # it is certain that any further query with the same query prefix
        # string will not yield any results. In order to avoid having
        # to parse the todo list in such cases, record the current prefix string
        # now so that we can later ignore processing such queries
        if len(filtered) == 0:
            # we do not have any matching todo's with the query entered
            # save the query to match prefixes later on so as to avoid having
            # to search the todo list all over again
            if len(query) > 0 and task not in ('#', '@'):
                config.put(ck.KEY_USER_QUERY_NOITEMPREFIX, query)
            feedback_items.append(generate_add_feedbackitem(query, info))
        else:
            # we now have results, so clear the prefix
            config.put(ck.KEY_USER_QUERY_NOITEMPREFIX, '')

            # this section is only to group the output, and should
            # always partition the filtered list
            pinned = [t for t in filtered if itemlist.feature(t, 'pinned') == True]
            pinned = pinned[::-1]
            # all due items will be list sorted by due date
            due = [t for t in filtered if itemlist.feature(t, 'pinned') == False and helpers.has_due(t)]
            due = sorted(due, key=lambda t: itemlist.feature(t, 'due'))
            # then all other items
            normal = [t for t in filtered if itemlist.feature(t, 'pinned') == False and not helpers.has_due(t)]
            normal = normal[::-1]

            pinned = map(lambda x: generate_todo_feedbackitem(x, info), pinned)
            due = map(lambda x: generate_todo_feedbackitem(x, info), due)
            normal = map(lambda x: generate_todo_feedbackitem(x, info), normal)
            feedback_items = pinned + due + normal

    alfred.write(alfred.xml(feedback_items))
