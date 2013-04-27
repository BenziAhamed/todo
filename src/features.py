# -*- coding: utf-8 -*-
import alfred
import config
from uuid import uuid4
import config_keys as ck
import store_rtm as rtm

def feedback_item(title, subtitle, arg):
    return alfred.Item(
        attributes={'uid': uuid4(),'arg': arg},
        title=title,
        subtitle=generate_toggle(arg) + subtitle,
        icon=generate_icon(arg)
    )

features = [
    {'id': ck.KEY_FEATURE_QUICKCREATE, 'title': 'Quick Create', 'subtitle': ' creating new todo items without Alfred flashing'},
    {'id': ck.KEY_FEATURE_FUZZYSEARCH, 'title': 'Anchored Search', 'subtitle': ' e.g. finding "this is great" by typing "tig"'},
    {'id': ck.KEY_FEATURE_SMARTCONTENT, 'title': 'Smart Content', 'subtitle': ' recognizing web urls, files, folders and applications'},
    {'id': ck.KEY_FEATURE_SMARTCONTENT_PAGETITLE, 'title': 'Smart Content - Page Titles', 'subtitle': ' loading web page title for web urls'},
    {'id': ck.KEY_FEATURE_EGGTIMER, 'title': 'EggTimer2 in Edit mode', 'subtitle': ' experimental integration'},
    {'id': ck.KEY_FEATURE_RTM, 'title': 'Remember The Milk (beta)', 'subtitle': ' basic support for lists and tasks'}

]


def generate_view():
    feedback_items = []
    if not all_enabled():
        feedback_items.append(feedback_item("Enable all", '', 'special_enable'))
    else:
        feedback_items.append(feedback_item("Disable all", '', 'special_disable'))

    feedback_items = feedback_items + map(lambda f: feedback_item(f['title'], f['subtitle'], f['id']), features)
    alfred.write(alfred.xml(feedback_items))


def generate_toggle(feature):
    if feature.startswith('special'):
        return ''
    if config.get(feature) == True:
        return "disable"
    return "enable"


def all_enabled():
    enabled = True
    for f in features:
        e = config.get(f['id']) == True
        enabled = enabled and e
    return enabled


def generate_icon(feature):
    if feature == 'special_enable' or config.get(feature) == True:
        return "todo_done.png"
    return "todo_old.png"


def set_all(target):
    for f in features:
        config.put(f['id'], target)
    print "All features enabled" if target else "All features disabled"


def toggle_feature(feature):
    current = False
    if not feature.startswith('special'):
        current = config.get(feature) == True
        config.put(feature, not current)
        feature = [f for f in features if f['id']==feature][0]
        print feature['title'] + ' ' + ("disabled" if current else "enabled")
    else:
        set_all( True if feature=='special_enable' else False )

    # post toggle actions
    if feature['id']==ck.KEY_FEATURE_RTM:
        if config.get(ck.KEY_FEATURE_RTM) == False:
            rtm.reset()


def main():
    (option, query) = alfred.args2()
    option_actions = {
        # Features
        '-view': lambda q: generate_view(),
        '-toggle': lambda q: toggle_feature(q)
    }
    option_actions[option](query)
    config.commit()

if __name__ == '__main__':
    main()
