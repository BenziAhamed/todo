# -*- coding: utf-8 -*-

import re
from pprint import pprint
import sys
from dateutil.relativedelta import *
from dateutil.parser import parse as date_parse
from datetime import *
import helpers


def parse(text):
    tag = None
    task = text
    pinned = False
    clear_due = False

    # check for pinned status
    if task.find("!!") >= 0:
        pinned = True
        task = task.replace("!!", "").strip()

    if task.find("@!") >= 0:
        clear_due = True
        task = task.replace("@!", "").strip()

    # (target_list, task) = get_list_and_task(task)
    (due, task) = get_due_and_task(task)
    (tag, task) = get_tag_and_task(task)

    return {
        'tag': tag,
        'task': task,
        'pinned': pinned,
        'due': due,
        'clear_due': clear_due
   }

def get_list_and_task(task):
    target_list = None
    m = re.match('^(?P<list>.*?):.*', task)
    if m:
        target_list = m.group('list')
        task = task.replace(target_list+':','')
        target_list = helpers.cleanup_filename(target_list)
    return target_list, task.strip()

def get_due_and_task(task):
    today = date.today()
    due = None

    # string codes
    if task.find("@tomorrow") >= 0:
        due = today + relativedelta(days=+1)
        task = task.replace("@tomorrow", "")
    elif task.find("@today") >= 0:
        due = today
        task = task.replace("@today", "")
    elif task.find("@weekend") >= 0:
        due = today + relativedelta(days=+1, weekday=SU(+1))
        task = task.replace("@weekend", "")
    elif task.find("@nextweek") >= 0:
        due = today + relativedelta(days=+1, weekday=MO(+1))
        task = task.replace("@nextweek", "")
    else:
        # short cuts
        g = re.match(r".*?@(?P<number>\d+)(?P<modifier>d|w|m).*?", task)
        if g:
            modifier = g.group('modifier')
            number = g.group('number')
            modifier_actions = {
                'd': lambda today, x:	today+relativedelta(days=x),
                'w': lambda today, x:	today+relativedelta(days=1, weekday=MO(+x)),
                'm': lambda today, x:	today+relativedelta(day=1, months=x)
            }
            due = modifier_actions[modifier](today, int(number))
            task = task.replace("@"+number+modifier, "")
        else:
            # weekdays
            g = re.match(r".*?@(?P<day>sun|mon|tue|wed|thu|fri|sat).*?", task)
            if g:
                day = g.group('day')
                day_actions = {
                    'mon': lambda today: today+relativedelta(days=+1, weekday=MO(+1)),
                    'tue': lambda today: today+relativedelta(days=+1, weekday=TU(+1)),
                    'wed': lambda today: today+relativedelta(days=+1, weekday=WE(+1)),
                    'thu': lambda today: today+relativedelta(days=+1, weekday=TH(+1)),
                    'fri': lambda today: today+relativedelta(days=+1, weekday=FR(+1)),
                    'sat': lambda today: today+relativedelta(days=+1, weekday=SA(+1)),
                    'sun': lambda today: today+relativedelta(days=+1, weekday=SU(+1))
                }
                due = day_actions[day](today)
                task = task.replace("@"+day, "")
            else:
                # fuzzy date
                g = re.match(
                    r".*?(?P<date>@(?P<p1>[0-9a-zA-Z]+)[ -/.]{1}(?P<p2>[0-9a-zA-Z]+)[ -/.]{1}(?P<p3>[0-9a-zA-Z]+)).*?", task)
                if g:
                    try:
                        due = date_parse(g.group('date'), fuzzy=True).date()
                        task = task.replace(g.group('date'), "")
                    except:
                        pass

    return (due, task.strip())


def get_tag_and_task(task):
    tag = None
    t = parse_for_tag(task)
    if t['mtag'] is not None:
        task = ""
        tag = t['mtag'].replace("#", "")
    elif t['btag'] is not None:
        task = task.replace(t['btag']+" ", "")
        tag = t['btag'].replace("#", "")
    elif t['etag'] is not None:
        task = task.replace(" "+t['etag'], "")
        tag = t['etag'].replace("#", "")
    return (tag, task.strip())


def parse_for_tag(text):
    g = re.match(r"^(?P<btag>#[^# ]+?)[ ]+.*|.*?[ ]+(?P<etag>#[^# ]+)$|^(?P<mtag>#[^# ]+)$", text.strip())
    o = {'mtag': None, 'etag': None, 'btag': None}
    tags = ['btag', 'etag', 'mtag']
    if g is not None:
        for t in tags:
            o[t] = g.group(t)
    return o


def showparse():
    pprint(parse(sys.argv[1]))


if __name__ == "__main__":
    showparse()
