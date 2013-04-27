# -*- coding: utf-8 -*-
import alfred
import config
import config_keys as ck
import editview
import helpers
import itemlist
import parser


def process_query(query):
    if query.startswith("_integration:"):
        integration_action(query.replace("_integration:", ""))
        return
    edit_item = config.get(ck.KEY_EDIT_ITEM)
    have_tag = helpers.is_tag(edit_item)
    have_todo = helpers.is_todo(edit_item)
    if have_todo:
        _id = helpers.extract_todo_id(edit_item)
        update_todo(_id, query)
    elif have_tag:
        update_tag(helpers.extract_tag(edit_item), query)
    config.put(ck.KEY_EDIT_ITEM, '')


def integration_action(task):
    edit_item = config.get(ck.KEY_EDIT_ITEM)
    _id = helpers.extract_todo_id(edit_item)
    todo = itemlist.get_todo(_id)['title']
    if task.startswith("eggtimer:"):
        alarm_time = task.replace("eggtimer:", "")
        alarm_command = "alarm " + alarm_time + " " + todo
        config.put(ck.KEY_EDIT_ACTION, 'integration')
        config.put(ck.KEY_INTEGRATION_COMMAND, alarm_command)


def update_todo(_id, query):
    info = parser.parse(query)
    todo = itemlist.get_todo(_id)

    done = itemlist.feature(todo, 'done')

    edit_tag = info['tag']
    edit_text = info['task']
    edit_due = info['due']
    edit_clear_due = info['clear_due']
    todo_tag = todo['group']
    todo_text = todo['title']
    todo_due = itemlist.feature(todo, 'due')

    tag_changed = edit_tag and edit_tag != todo_tag
    task_changed = len(edit_text) > 0 and edit_text != todo_text
    due_changed = edit_due and edit_due != todo_due
    title = todo['title']
    tag = todo['group']
    update_info = {}
    if (task_changed):
        update_info['title'] = edit_text
        title = edit_text
    if (tag_changed):
        update_info['group'] = edit_tag
        tag = edit_tag
    if (due_changed):
        update_info['due'] = edit_due
    if edit_clear_due:
        update_info['due'] = None

    itemlist.update_todo(_id, update_info)

    config.put(ck.KEY_EDIT_ACTION, 'edit_done' if done else 'edit_todo')
    if tag != 'default':
        print ("Updated '" + title + "' tagged #" + tag).encode('utf-8')
    else:
        print ("Updated '" + title + "'").encode('utf-8')


def update_tag(old_tag, query):
    info = parser.parse(query)
    new_tag = info['tag']

    if not new_tag:
        return

    itemlist.update_tag(old_tag, new_tag)

    config.put(ck.KEY_EDIT_ACTION, 'edit_tag')
    print ("Updated tag #" + old_tag + " to #" + new_tag).encode('utf-8')


def main():
    (option, query) = alfred.args2()
    option_actions = {
        # Editing
        '-view': lambda q: editview.generate_view(q),
        '-action': lambda q: process_query(q)
    }
    option_actions[option](query)
    config.commit()

if __name__ == '__main__':
    main()
