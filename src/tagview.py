# -*- coding: utf-8 -*-
import itemlist
import alfred
import config
import helpers
import parser
import itemview
from uuid import uuid4


def has_priority(query):
    (only_tag, tag, info) = get_tag_state(query)
    return only_tag


def get_tag_state(query):
    info = parser.parse(query)
    tag = info['tag']

    # determine if only a tag has been entered
    tag_view_needed = (query == '#' or (tag and len(info['task']) == 0))

    # if there are not existing tags, then just go to add mode
    # -- or --
    # if a tag name matches exactly with an existing tag
    # we do not want tag view, but rather item list view
    if tag_view_needed and tag:
        tags = itemlist.get_tags()
        if len(tags) == 0:
            tag_view_needed = False
        else:
            tag_view_needed = not (tag in tags)

    return (tag_view_needed, tag, info)


def generate_view(query, entered_tag, info):
    feedback_items = []
    tags = itemlist.get_tags()

    # check if we have any tags
    if len(tags) == 0:
        feedback_items.append(default_no_tags())
        config.update_state(tag='#default')
    else:
        if entered_tag:
            feedback_items.append(itemview.generate_add_feedbackitem(query, info))
        sorted_tags = sorted(tags, key=lambda x: x)
        for tag in sorted_tags:
            if not entered_tag or tag.lower().find(entered_tag.lower()) >= 0:
                count = tags[tag]
                feedback_items.append(
                    alfred.Item(
                        attributes={
                            'uid': uuid4(),
                            'arg': helpers.encode_tag(tag),
                            'autocomplete': "#{0} ".format(tag),
                            'valid': 'yes'
                        },
                        title="#{0}".format(tag),
                        subtitle="{0} item{1}".format(count, ('' if count == 1 else 's')),
                        icon="todo_tag.png"
                    )
                )
    config.update_state(view='tag_view', command='display_tags')
    alfred.write(alfred.xml(feedback_items))


def default_no_tags():
    title = "Sorry, no tags exist"
    subtitle = "Type something to create a new todo"
    return alfred.Item(
        attributes={
            'uid': alfred.uid("notags"),
            'arg': '',
            'valid': 'no'
        },
        title=title,
        subtitle=subtitle,
        icon="todo_tag.png"
    )
