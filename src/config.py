import os
from pprint import pprint
import sys

import alfred
import config_keys as ck
import yaml

# bad idea
cached_config = None

# Gets the key value of
# preference
def get(key, default="todo.keyvalue.none"):
	p = load()
	if key in p:
		return p[key]
	return default

# Updates the value
# of the specified key
def put(key, value, force_save=False):
	p = load()
	p[key] = value;
	if force_save:
		save(p)
	pass

# Loads the current preferences
def load():
	global cached_config
	if cached_config is None:
		init()
		f = open ( pref_path() )
		p = yaml.load(f)
		cached_config = p
	return cached_config

def save(p):
	f = open( pref_path(), 'w')
	yaml.dump(p, f)

def commit():
	global cached_config
	if cached_config is None:
		return
	f = open( pref_path(), 'w')
	yaml.dump(cached_config, f)

def default_pref():
	return { ck.KEY_TODO : default_todo_path(), ck.KEY_TAG_RECENT : 'default', ck.KEY_FORMAT_DEFAULT: '.yaml' }

def reset(path):
	p = default_pref()
	f = open( path, 'w')
	yaml.dump(p, f)

# if no preferences exists,
# create the default one
def init():
	path = pref_path()
	if not os.path.exists( path ):
		reset(path)
	return

def pref_path():
	return os.path.join ( alfred.work(False), "config.yaml" )

def default_todo_path():
	return os.path.join ( alfred.work(False), "todo.yaml" )

def update_state(view=None, command=None, tag=None, query=None):
	if view is not None:
		put(ck.KEY_VIEW_LAST, view)
	if command is not None:
		put(ck.KEY_COMMAND_LAST, command)
	if tag is not None:
		put(ck.KEY_TAG_RECENT, tag)
	if query is not None:
		put(ck.KEY_USER_QUERY, query)

def main():
	(command, data) = alfred.args2()
	if command == '-load':
		pprint(load())
	elif command == '-default':
		print default_pref()
	elif command == '-path':
		print pref_path()
	elif command == '-get':
		value = get(data)
		if value != '':
			print value
	elif command == '-put':
		put(sys.argv[2], sys.argv[3], force_save=True)
	elif command == '-init':
		init()
	elif command == "-reset":
		reset(pref_path())
	commit()

if __name__ == "__main__":
    main()