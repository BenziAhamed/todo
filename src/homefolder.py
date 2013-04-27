import os
import alfred
import config
import shutil
from uuid import uuid4
import config_keys as ck


def generate_no_conflict_feedbackitem(destination_path):
    feedback_items = []
    feedback_items.append(alfred.Item(
        attributes={
            'uid': uuid4(),
            'arg': 'no_conflict'
        },
        title="Move your Todo database",
        subtitle="Move it to '{0}'".format(destination_path),
        icon="5942F024-8248-41C6-8D33-422F4BFC7408.png"
    ))
    alfred.write(alfred.xml(feedback_items))


def generate_conflict_feedbackitem(destination_path):
    feedback_items = []
    feedback_items.append(alfred.Item(
        attributes={
            'uid': uuid4(),
            'arg': '',
            'valid': 'no'
        },
        title="Please choose an option from below",
        subtitle="Folder already has a Todo database: '{0}'".format(destination_path),
        icon="5942F024-8248-41C6-8D33-422F4BFC7408.png"
    ))
    alfred.write(alfred.xml(feedback_items))


def has_conflict(source_file, destination_file):
    return os.path.exists(source_file) and os.path.exists(destination_file)


# option if there is no conflict
def migrate_todo_list(source_path, destination_path, migration_option):
    source_file = os.path.join(source_path, "todo.yaml")
    destination_file = os.path.join(destination_path, "todo.yaml")

    if migration_option == "no_conflict":
        # Case A: file in source, move to destination
        if os.path.exists(source_file):
            shutil.move(source_file, destination_path)
        # Case B: no file in source, nothing to do
        # Case C: file in destination, leave it as is
        # Now update the config to point to new location
        config.put(ck.KEY_TODO, destination_file)

    elif migration_option == "keep_old":
        # Move the old file to the new location
        if os.path.exists(destination_file):
            os.remove(destination_file)
        shutil.move(source_file, destination_path)
        config.put(ck.KEY_TODO, destination_file)

    elif migration_option == "keep_new":
        # We do not touch the old file
        config.put(ck.KEY_TODO, destination_file)

    elif migration_option == "merge":
        old_todos = []
        with open(source_file) as source:
            old_todos = source.readlines()
        with open(destination_file, "a") as destination:
            destination.write(old_todos)
        config.put(ck.KEY_TODO, destination_file)

    config.put('todo.db.destination_path', '')


def generate_view(destination_path):
    source_file = config.get(ck.KEY_TODO)
    destination_file = os.path.join(destination_path, "todo.yaml")
    if not has_conflict(source_file, destination_file):
        generate_no_conflict_feedbackitem(destination_path)
    else:
        generate_conflict_feedbackitem(destination_path)


def main():
    (option, arg) = alfred.args2()
    if option == "-view":
        config.put('todo.db.destination_path', arg)
        generate_view(arg)
    elif option == "-migrate":
        migrate_todo_list(
            os.path.dirname(config.get(ck.KEY_TODO)),
            config.get('todo.db.destination_path'),
            arg
        )
    config.commit()


if __name__ == "__main__":
    main()
