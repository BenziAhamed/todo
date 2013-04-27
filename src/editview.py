
# -*- coding: utf-8 -*-

from uuid import uuid4

import alfred
import config
import config_keys as ck
import helpers
import integration
import itemlist
import parser
import listmanager


def generate_view(query):
    edit_item = config.get(ck.KEY_EDIT_ITEM)
    have_tag = helpers.is_tag(edit_item)
    have_todo = helpers.is_todo(edit_item)
    if have_todo:
        _id = helpers.extract_todo_id(edit_item)
        generate_view_itemedit(_id, query)
    elif have_tag:
        generate_view_tagedit(helpers.extract_tag(edit_item), query)
    else:
        generate_select_item()


def generate_select_item():
    feedback_items = []
    feedback_items.append(alfred.Item(
        attributes={
        'uid': uuid4(),
        'arg': '',
        'valid': 'no'
        },
        title="Nothing to edit",
        subtitle="Select an item to edit first",
        icon="todo_edit.png"
    ))
    alfred.write(alfred.xml(feedback_items))


def generate_view_tagedit(old_tag, query):
    info = parser.parse(query)
    new_tag = info['tag']
    new_text = info['task']
    tag_changed = new_tag and new_tag != old_tag
    only_tag_changed = tag_changed and len(new_text) == 0

    feedback_items = []
    # action item
    feedback_items.append(alfred.Item(
        attributes={
        'uid': uuid4(),
        'arg': query + "  ",
        'valid': 'yes' if only_tag_changed else 'no'
        },
        title="Update tag" if only_tag_changed else "Nothing to update",
        subtitle="Enter a new tag name" if not only_tag_changed else "",
        icon="todo_edit.png"
    ))
    # tag info item
    feedback_items.append(alfred.Item(
        attributes={
        'uid': uuid4(),
        'arg': "",
        'valid': 'no',
        'autocomplete': "#"+old_tag
        },
        title="#"+old_tag,
        subtitle="Change to #" + new_tag if only_tag_changed else "",
        icon="todo_tag.png"
    ))
    alfred.write(alfred.xml(feedback_items))


# edit view
# change tag name
# change item details (tag, text)
def generate_view_itemedit(_id, query):
    todo = itemlist.get_todo(_id)
    if not todo:
        generate_select_item()
        return

    todo_tag = todo['group']
    todo_text = todo['title']
    todo_due = itemlist.feature(todo, 'due')

    info = parser.parse(query)
    edit_tag = info['tag']
    edit_text = info['task']
    edit_due = info['due']
    edit_clear_due = info['clear_due']

    # TODO: Change this later so that parse will handle this
    clear_due = False
    if edit_clear_due and todo_due is not None:
        clear_due = True
        edit_text = edit_text.replace('@!', '').strip()

    feedback_items = []

    tag_changed = edit_tag and edit_tag != todo_tag
    task_changed = len(edit_text) > 0 and edit_text != todo_text
    due_changed = edit_due and edit_due != todo_due

    nothing_to_update = not task_changed and not tag_changed and not due_changed and not clear_due

    changed_items = []
    if (task_changed):
        changed_items.append('text')
    if (tag_changed):
        changed_items.append('tag')
    if (due_changed or clear_due):
        changed_items.append('due')

    pinned = itemlist.feature(todo, 'pinned')
    done = itemlist.feature(todo, 'done')

    # integration items
    integration.apply_integration(feedback_items, todo, query)

    # action item
    feedback_items.append(alfred.Item(
        attributes={
        'uid': uuid4(),
        'arg': query + "  ",
        'valid': 'no' if nothing_to_update else 'yes'
        },
        title="No change" if nothing_to_update else "Change " + ", ".join(changed_items),
        subtitle="",
        icon="todo_edit.png"
    ))

    # info item - task title
    # if a edit tag is specified, append that and add todo text
    text_autocomplete = "".join([
        "" if not edit_tag else "#"+edit_tag+' ',
        todo_text
    ]).strip()
    if len(text_autocomplete) == 2:
        text_autocomplete = text_autocomplete + "  "
    feedback_items.append(alfred.Item(
        attributes={
        'uid': uuid4(),
        'arg': '',
        'valid': 'no',
        'autocomplete': text_autocomplete
        },
        title=todo_text,
        subtitle=u"Change to: {0}".format(edit_text) if task_changed else "No change",
        icon="todo_done.png" if done else ("todo_pin.png" if pinned else "icon.png")
    ))

    # info item - tag name
    formatted_query = query
    if edit_tag:
        formatted_query = formatted_query.replace("#"+edit_tag, "")
    tag_autocomplete = "".join([
        "#" + todo_tag + " ",
        formatted_query.strip()
    ]).strip()
    if len(tag_autocomplete) == 2:
        tag_autocomplete = tag_autocomplete + "  "
    feedback_items.append(alfred.Item(
        attributes={
        'uid': uuid4(),
        'arg': '',
        'valid': 'no',
        'autocomplete': tag_autocomplete
        },
        title="#" + todo_tag,
        subtitle=u"Change to: #{0}".format(edit_tag) if tag_changed else "No change",
        icon="todo_tag.png"
    ))

    # due item
    subtitle = "No change"
    if todo_due is not None:
        subtitle = subtitle + " (@! will clear)"
    if due_changed:
        subtitle = u"Change to: {0}".format(helpers.due_date_text(edit_due))
    if clear_due:
        subtitle = "Clear due"

    feedback_items.append(alfred.Item(
        attributes={
        'uid': uuid4(),
        'arg': '',
        'valid': 'no'
        },
        title=helpers.due_date_text(todo_due) if todo_due else "No due date",
        subtitle=subtitle,
        icon="todo_due.png"
    ))

    # in which list is this item
    feedback_items.append(alfred.Item(
        attributes={
        'uid': uuid4(),
        'arg': '',
        'valid': 'no'
        },
        title='List: ' + listmanager.friendly_file(listmanager.active_list()),
        subtitle="",
        icon="icon.png"
    ))

    alfred.write(alfred.xml(feedback_items))
