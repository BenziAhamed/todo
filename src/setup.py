import config
import sys
import os
import shutil
import alfred
import listmanager
import config_keys as ck


def update_todo_db_path(new_home):
    # move all yaml files that are present in the current home folder
    # to the destination home folder
    home, db = os.path.split(config.get(ck.KEY_TODO))
    if home == new_home:
        print "'{0}' is already your home folder".format(new_home)
        return

    lists, active = listmanager.get_todo_lists()
    conflicts = []
    for l in lists:
        src = os.path.join(home, l)
        dest = os.path.join(new_home, l)
        if os.path.exists(src):
            if not os.path.exists(dest):
                shutil.move(src, new_home)
            else:
                conflicts.append(listmanager.friendly_file(l))

    # update the active list
    config.put(ck.KEY_TODO, os.path.join(new_home, active))

    print "'{0}' is now your Todo home folder".format(new_home)
    if len(conflicts) > 0:
        print "not migrated: " + ",".join(conflicts)

    # Old menthod before lists came into play
    # # before updating the config, check if a todo file
    # # is already present. If yes, move existing file to the
    # # new location.
    # # If a file already exists at the destination, issue a warning
    # new_todo_db = os.path.join(path_for_todo_db, "todo.yaml")
    # old_todo_db = config.get(ck.KEY_TODO)
    # if new_todo_db == old_todo_db:
    #     print "'{0}'' is already your home folder".format(path_for_todo_db)
    #     return

    # if os.path.exists(new_todo_db):
    #     print "Oops! Looks like a todo.yaml file already exists in '{0}'".format(path_for_todo_db)
    #     return

    # if os.path.exists(old_todo_db):
    #     shutil.move(old_todo_db, path_for_todo_db)

    # config.put(ck.KEY_TODO, new_todo_db)
    # print "'{0}' is now configured as your Todo database folder".format(path_for_todo_db)


def reset():
    config.reset(config.pref_path())


def main():
    (command, data) = alfred.args2()
    if command == "-set-folder":
        update_todo_db_path(data)
    elif command == "-reset":
        reset()
    config.commit()


if __name__ == "__main__":
    main()
