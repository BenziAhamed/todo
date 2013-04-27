from datetime import datetime, date
import re
import os
import itemlist
import smartcontent
import unicodedata
import subprocess
import codecs
import sys
import config_keys as ck
import config
import string

valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)


def cleanup_filename(filename):
    cleaned = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in cleaned if c in valid_filename_chars)



def create_title(t):
    if smartcontent.smartcontent_enabled():
        smartcontent_type = itemlist.feature(t, 'smartcontent_type')
        smartcontent_info = itemlist.feature(t, 'smartcontent_info')
        if len(smartcontent_type) > 0:
            if smartcontent_type == 'File' or smartcontent_type == 'Directory':
                return smartcontent_info
            elif smartcontent_type == 'Application':
                return smartcontent_info.replace(".app", "")
            elif smartcontent_type == 'Web':
                if len(smartcontent_info) > 0:
                    return smartcontent_info
    return t['title']


def create_subtitle(t):
    # option 1 - simple and clean
    subtitle = ""
    if itemlist.feature(t, 'due'):
        subtitle = due_date_text(t['due'])
    if t['group'] != "default":
        subtitle = subtitle + " #" + t['group']

    if smartcontent.smartcontent_enabled():
        smartcontent_type = itemlist.feature(t, 'smartcontent_type')
        smartcontent_info = itemlist.feature(t, 'smartcontent_info')
        if len(smartcontent_type) > 0:
            subtitle = subtitle + " " + t['title']
            # if smartcontent_type == "Web":
            #     if len(smartcontent_info) > 0:
            #         subtitle = subtitle + " Web: " + t["title"]
            #     else:
            #         subtitle = subtitle + " Web"
            # else:
            #     subtitle = subtitle + " " + smartcontent_type + ": " + t['title']

    return subtitle.strip()

    # option 2 - lots of info
    # use_created = True
    # done = itemlist.feature(t, 'done')
    # if done:
    # 	done_when = itemlist.feature(t, 'done_when')
    # 	use_created = False
    # created = t['created']
    # d = datetime.now()
    # if use_created:
    # 	d = d - created
    # else:
    # 	d = d - done_when
    # (days, hours, minutes) = (d.days, d.seconds//3600, (d.seconds//60)%60)
    # all_seconds = d.total_seconds()
    # subtitle = None
    # if all_seconds <= 60:
    # 	subtitle = "added moments ago"
    # elif all_seconds <= 120:
    # 	subtitle = "added 1 minute ago"
    # elif all_seconds <= 3600:
    # 	subtitle = "added {0} minutes ago".format(minutes)
    # elif all_seconds <= 7200:
    # 	subtitle = "added about an hour ago"
    # elif all_seconds <= 86400:
    # 	subtitle = "added {0} hours ago".format(hours)
    # if subtitle is None:
    # 	if days == 1:
    # 		subtitle = "added yesterday"
    # 	elif days < 7:
    # 		subtitle = "added this week"
    # 	elif days < 14:
    # 		subtitle = "added last week"
    # 	elif days < 30:
    # 		subtitle = "added {0} weeks ago".format(int(days/7))
    # 	elif days < 365:
    # 		subtitle = "added about {0} month{1} ago".format(int(days/30), "s" if days/30 > 1 else "")
    # 	else:
    # 		subtitle = "added before last year"

    # if not use_created:
    # 	subtitle = subtitle.replace("added ", "completed ")
    # if t['group'] != "default":
    # subtitle = "#{0} {1}".format(t['group'], subtitle)

    # return subtitle


def create_icon(t):
    pinned = itemlist.feature(t, 'pinned')
    if pinned:
        return "todo_pin.png"

    due = itemlist.feature(t, 'due')
    if due and due <= date.today():
        return "todo_old.png"

    if smartcontent.smartcontent_enabled():
        smartcontent_type = itemlist.feature(t, 'smartcontent_type')
        icon_types = {
            "Web": "todo_web.png",
            "File": "todo_file.png",
            "Directory": "todo_folder.png",
            "Application": "todo_app.png",
        }
        if smartcontent_type in icon_types:
            return icon_types[smartcontent_type]

    return "icon.png"


def due_date_text(due_date):
    today = date.today()
    if today == due_date:
        return "today"
    elif (due_date - today).days == 1:
        return "tomorrow"
    elif (due_date - today).days == -1:
        return "yesterday"
    try:
        return due_date.strftime("%a %d %b %Y").lower()
    except:
        return due_date.isoformat()


def create_autocomplete(t, info):
    # Press tab once to get the tag name
    # Press tab again to get the task title
    if t['group'] == 'default':
        autocomplete = t['title']
    else:
        autocomplete = '#' + t['group'] + ' '
        entered_tag = info['tag']
        if entered_tag == t['group']:
            autocomplete = '#' + t['group'] + ' ' + t['title']
    return autocomplete


def macSetClipboard(text):
    # sys.stdin = codecs.getreader("utf8")(sys.stdin)
    # sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    # p = Popen(['pbcopy'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    # p.communicate(input=text.encode('utf-8'))

    outf = os.popen('pbcopy', 'w')
    outf.write(text.encode('utf-8'))
    outf.close()

    # os.system('echo ' + text.encode('utf-8') + ' | pbcopy')


def macGetClipboard():
    outf = os.popen('pbpaste', 'r')
    content = outf.readlines()
    outf.close()
    return content


def is_todo(q):
    return q.startswith("_id:")


def is_tag(q):
    return q.startswith("_tag:")


def extract_tag(q):
    return q.replace("_tag:", "")


def extract_todo_id(q):
    return q.replace("_id:", "")


def encode_tag(q):
    return "_tag:" + q


def encode_todo_id(q):
    return "_id:" + q


def has_due(todo):
    return itemlist.feature(todo, 'due') is not None


def apply_filter_task(todo, q_task):
    if config.get(ck.KEY_FEATURE_FUZZYSEARCH) == True:
        t_task = todo['title'].lower()
        # just get the letters and alphabets
        # t_task = " ".join(re.findall(r'[a-zA-Z0-9-]+', t_task))
        q = [re.escape(c) for c in list(q_task)]
        m = re.match(".*?" + ".*?[ ]".join(q) + ".*", t_task)
        if m:
            return True
    return (q_task is None or q_task == '@' or todo['title'].lower().find(q_task.lower()) >= 0)


def apply_filter(todo, q_task, q_tag, q_due, q_done=False):
    # Narrow down todo list based on what was typed
    # The following filters are applied, not in the same order
    # 1. filter by tag if specified
    # 2. filter by query text if applicable (@ is a special keyword)
    # 3. filter by done status
    # 4. filter by due date if its specified
    # 5. filter by @ for all due items
    # thank god for short circuiting of boolean clauses :-)
    todo_is_not_done = (itemlist.feature(todo, 'done') == q_done)
    todo_has_due_if_needed = (q_task != '@' or has_due(todo))
    todo_matches_due_specified = (q_due is None or q_due == itemlist.feature(todo, 'due'))
    todo_matches_tag_specified = (q_tag is None or todo['group'].lower() == q_tag.lower())
    todo_matches_task_specified = apply_filter_task(todo, q_task)
    return (
        todo_is_not_done
        and todo_has_due_if_needed
        and todo_matches_due_specified
        and todo_matches_tag_specified
        and todo_matches_task_specified
    )
