import sys
import os
import alfred
import helpers
import config
import itemlist
import tagview
import itemview
import smartcontent
import edit
import listmanager
import config_keys as ck


def process_todo_query(raw_query):
    (tag_view_preferred, entered_tag, parse_info) = tagview.get_tag_state(raw_query)
    if tag_view_preferred:
        tagview.generate_view(raw_query, entered_tag, parse_info)
    else:
        itemview.generate_view(raw_query, parse_info)

def actionize(query):
    if len(query) <= 0:
        return
    have_tag = helpers.is_tag(query)
    have_todo = helpers.is_todo(query)

    if not (have_tag or have_todo):
        itemlist.save_todo(query)
    elif have_todo:
        _id = helpers.extract_todo_id(query)

        # smart content is a bit rudimentary at the moment
        if smartcontent.smartcontent_enabled():
            smartcontent.perform_action(_id)
        else:
            itemlist.copy_todo_to_clipboard(_id)

    elif have_tag:
        config.put(ck.KEY_TAG_RECENT, "#"+helpers.extract_tag(query))


def toggle_pin(query):
    if helpers.is_todo(query):
        itemlist.toggle_pinned(helpers.extract_todo_id(query))


def toggle_done(query):
    if helpers.is_todo(query):
        itemlist.toggle_done(helpers.extract_todo_id(query))


def main():
    (option, query) = alfred.args2()
    option_actions = {
        # Clearing items
        '-c': lambda q: itemlist.clear_all_todos(),
        '-ct': lambda q: itemlist.clear_todos(done=False),
        '-cd': lambda q: itemlist.clear_todos(done=True),
        # Processing query input
        '-a': lambda q:	actionize(q),
        '-q': lambda q:	process_todo_query(q),
        '-r': lambda q:	itemlist.remove_item(q),
        # Item toggles
        '-p': lambda q:	toggle_pin(q),
        '-d': lambda q:	toggle_done(q)
    }
    option_actions[option](query)
    config.commit()

if __name__ == "__main__":
    main()
