# -*- coding: utf-8 -*-

import sys
import codecs
import itemlist
import store
import os


def main():
    # export_csv.py input output
    # input todo file
    input_file = sys.argv[1]
    # target csv file
    export_file = sys.argv[2]

    if not os.path.exists(input_file):
        return

    todos = store.Store().get_store(input_file).get_todo_list()

    csv_data = []

    pinned = [t for t in todos if itemlist.feature(t,'pinned')==True and not itemlist.feature(t,'done')==True]
    due = [t for t in todos if itemlist.feature(t,'pinned')==False and itemlist.feature(t,'due') is not None and not itemlist.feature(t,'done')==True]
    others = [t for t in todos if itemlist.feature(t,'pinned')==False and itemlist.feature(t,'due') is None and not itemlist.feature(t,'done')==True]

    for t in pinned:
        csv_data.append(get_task_line(t))
    for t in due:
        csv_data.append(get_task_line(t))
    for t in others:
        csv_data.append(get_task_line(t))

    if len(csv_data) > 0:
        with codecs.open(export_file, "w", "utf-8") as f:
            f.write("\n".join(csv_data))

def get_task_line(t):
    # CSV format
    # important, task, due + tag
    important = "important" if itemlist.feature(t,'pinned') else ""
    due = str(itemlist.feature(t,'due')) if itemlist.feature(t,'due') is not None else ""
    task = itemlist.feature(t,'title')
    tag = ("#" + itemlist.feature(t,'group')) if itemlist.feature(t,'group')!='default' else ""
    task_line = [important, task, due + " " + tag]
    task_line = u",".join(task_line)
    return task_line

if __name__ == '__main__':
    main()
