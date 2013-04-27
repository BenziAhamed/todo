# -*- coding: utf-8 -*-
import alfred
import itemlist
import config as todo_config
from YamlStore import YamlStore
from TaskpaperStore import TaskpaperStore
from JsonStore import JsonStore

def import_from_file(import_file):
    if import_file.lower().endswith(".taskpaper"):
        import_from_taskpaper(import_file)
    elif import_file.lower().endswith(".yaml"):
        import_from_yaml(import_file)
    elif import_file.lower().endswith(".json"):
        import_from_json(import_file)
    else:
        import_from_plaintext(import_file)


def import_from_plaintext(import_file):
    with open(import_file) as f:
        content = f.readlines()
    content = plaintext_normalize(content)
    r = itemlist.import_todo_items_threaded2(content)
    print "Imported {0} item{1} from '{2}'".format(
        r['imported'],
        "" if r['imported'] == 1 else "s",
        import_file
    )



def import_from_taskpaper(import_file):
    try:
        store = TaskpaperStore(import_file)
        todos = store.get_todo_list()
        itemlist.append_todo_list(todos)
        print "Imported {0} items from '{1}'".format(len(todos), import_file)
    except:
        print "Could not import anything from '{0}'".format(import_file)

def import_from_yaml(import_file):
    try:
        store = YamlStore(import_file)
        todos = store.get_todo_list()
        itemlist.append_todo_list(todos)
        print "Imported {0} items from '{1}'".format(len(todos), import_file)
    except:
        print "Could not import anything from '{0}'".format(import_file)

def import_from_json(import_file):
    try:
        store = JsonStore(import_file)
        todos = store.get_todo_list()
        itemlist.append_todo_list(todos)
        print "Imported {0} items from '{1}'".format(len(todos), import_file)
    except:
        print "Could not import anything from '{0}'".format(import_file)

def import_from_clipboard():
    content = helpers.macGetClipboard()
    content = normalize(content)
    r = itemlist.import_todo_items(content)
    print "Imported {0} item{1} from the clipboard".format(
        r['imported'],
        "" if r['imported'] == 1 else "s"
    )

def plaintext_normalize(contents):
    # remove empty lines
    contents = [c.strip() for c in contents if len(c.strip()) > 0]
    contents = [c.decode('utf-8') for c in contents]
    normalized = []
    saved_tag = 'default'
    for line in contents:
        tag = None
        task = line
        orig_line = line

        line = line.replace("!!", "")
        line = line.strip()
        (tag, task) = parser.get_tag_and_task(line)

        # if tag is present save the header
        # if line is not just tag, then
        # save the normalized line
        if tag is not None:
            saved_tag = tag
            if len(task) > 0:
                normalized.append(orig_line)
        # if tag is not present
        # add saved tag to the beginning with padding
        else:
            normalized.append(u"#{0} {1}".format(saved_tag, orig_line))
    return normalized

def main():
    (option, query) = alfred.args2()
    option_actions = {
        '-file': lambda x: import_from_file(query),
        '-clipboard': lambda x: import_from_clipboard()
    }
    option_actions[option](query)
    todo_config.commit()

if __name__ == "__main__":
    main()
