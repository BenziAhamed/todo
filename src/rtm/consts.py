# -*- coding: utf-8 -*-

SERVICE_URL = 'http://api.rememberthemilk.com/services/rest/'
AUTH_SERVICE_URL = 'http://www.rememberthemilk.com/services/auth/'

# API spec
API = {
    'auth': {
        'checkToken':
            [('auth_token',), ()],
        'getFrob':
            [(), ()],
        'getToken':
            [('frob',), ()]
    },
    'contacts': {
        'add':
            [('timeline', 'contact'), ()],
        'delete':
            [('timeline', 'contact_id'), ()],
        'getList':
            [(), ()]
    },
    'groups': {
        'add':
            [('timeline', 'group'), ()],
        'addContact':
            [('timeline', 'group_id', 'contact_id'), ()],
        'delete':
            [('timeline', 'group_id'), ()],
        'getList':
            [(), ()],
        'removeContact':
            [('timeline', 'group_id', 'contact_id'), ()],
    },
    'lists': {
        'add':
            [('timeline', 'name',), ('filter',)],
        'archive':
            [('timeline', 'list_id'), ()],
        'delete':
            [('timeline', 'list_id'), ()],
        'getList':
            [(), ()],
        'setDefaultList':
            [('timeline'), ('list_id')],
        'setName':
            [('timeline', 'list_id', 'name'), ()],
        'unarchive':
            [('timeline',), ('list_id',)]
    },
    'locations': {
        'getList':
            [(), ()]
    },
    'reflection': {
        'getMethodInfo':
            [('method_name',), ()],
        'getMethods':
            [(), ()]
    },
    'settings': {
        'getList':
            [(), ()]
    },
    'tasks': {
        'add':
            [('timeline', 'name',), ('list_id', 'parse',)],
        'addTags':
            [('timeline', 'list_id', 'taskseries_id', 'task_id', 'tags'),
             ()],
        'complete':
            [('timeline', 'list_id', 'taskseries_id', 'task_id',), ()],
        'delete':
            [('timeline', 'list_id', 'taskseries_id', 'task_id'), ()],
        'getList':
            [(),
             ('list_id', 'filter', 'last_sync')],
        'movePriority':
            [('timeline', 'list_id', 'taskseries_id', 'task_id', 'direction'),
             ()],
        'moveTo':
            [('timeline', 'from_list_id', 'to_list_id', 'taskseries_id',
              'task_id'),
             ()],
        'postpone':
            [('timeline', 'list_id', 'taskseries_id', 'task_id'),
             ()],
        'removeTags':
            [('timeline', 'list_id', 'taskseries_id', 'task_id', 'tags'),
             ()],
        'setDueDate':
            [('timeline', 'list_id', 'taskseries_id', 'task_id'),
             ('due', 'has_due_time', 'parse')],
        'setEstimate':
            [('timeline', 'list_id', 'taskseries_id', 'task_id'),
             ('estimate',)],
        'setLocation':
            [('timeline', 'list_id', 'taskseries_id', 'task_id'),
             ('location_id',)],
        'setName':
            [('timeline', 'list_id', 'taskseries_id', 'task_id', 'name'),
             ()],
        'setPriority':
            [('timeline', 'list_id', 'taskseries_id', 'task_id'),
             ('priority',)],
        'setRecurrence':
            [('timeline', 'list_id', 'taskseries_id', 'task_id'),
             ('repeat',)],
        'setTags':
            [('timeline', 'list_id', 'taskseries_id', 'task_id'),
             ('tags',)],
        'setURL':
            [('timeline', 'list_id', 'taskseries_id', 'task_id'),
             ('url',)],
        'uncomplete':
            [('timeline', 'list_id', 'taskseries_id', 'task_id'),
             ()],
    },
    'tasksNotes': {
        'add':
            [('timeline', 'list_id', 'taskseries_id', 'task_id',
              'note_title', 'note_text'), ()],
        'delete':
            [('timeline', 'note_id'), ()],
        'edit':
            [('timeline', 'note_id', 'note_title', 'note_text'), ()]
    },
    'test': {
        'echo':
            [(), ()],
        'login':
            [(), ()]
    },
    'time': {
        'convert':
            [('to_timezone',), ('from_timezone', 'to_timezone', 'time')],
        'parse':
            [('text',), ('timezone', 'dateformat')]
    },
    'timelines': {
        'create':
            [(), ()]
    },
    'timezones': {
        'getList':
            [(), ()]
    },
    'transactions': {
        'undo':
            [('timeline', 'transaction_id'), ()]
    },
}


# response format
_LIST_COMMON = {
    'list': ['archived', 'deleted', 'id', 'locked', 'name',
             'position', 'smart'],
}

_TASK_COMMON = {
    'lists': {
        'list': ['id', {
            'taskseries': ['created', 'id', 'modified', 'name',
                           'source', {
                'tags': [],
                'participants': [],
                'notes': [],
                'task': ['added', 'completed', 'deleted', 'due',
                         'estimate', 'has_due_time', 'id', 'postponed',
                         'priority'],
                },
            ],
            },
        ],
    },
}

_TASK_TAGS = {
    'lists': {
        'list': ['id', {
            'taskseries': ['created', 'id', 'modified', 'name',
                           'source', {
                'tags': {
                    'tag': [],
                },
                'participants': [],
                'notes': [],
                'task': ['added', 'completed', 'deleted', 'due',
                         'estimate', 'has_due_time', 'id', 'postponed',
                         'priority'],
                },
            ],
            },
        ],
    },
}

_TASK_RRULE = {
    'lists': {
        'list': ['id', {
            'taskseries': ['created', 'id', 'modified', 'name',
                           'source', {
                'rrule': ['every'],
                'tags': [],
                'participants': [],
                'notes': [],
                'task': ['added', 'completed', 'deleted', 'due',
                         'estimate', 'has_due_time', 'id', 'postponed',
                         'priority'],
                },
            ],
            },
        ],
    },
}

_TASK_TAGS_RRULE = {
    'lists': {
        'list': ['id', {
            'taskseries': ['created', 'id', 'modified', 'name',
                           'source', {
                'rrule': ['every'],
                'tags': {
                    'tag': [],
                },
                'participants': [],
                'notes': [],
                'task': ['added', 'completed', 'deleted', 'due',
                         'estimate', 'has_due_time', 'id', 'postponed',
                         'priority'],
                },
            ],
            },
        ],
    },
}

API_RESPONSE = {
    'auth': {
        'checkToken': {
            'auth': {
                'token': [],
                'perms': [],
                'user': ['fullname', 'id', 'username'],
            },
        },
        'getFrob': {
            'frob': [],
        },
        'getToken': {
            'auth': {
                'token': [],
                'perms': [],
                'user': ['fullname', 'id', 'username'],
            },
        },
    },
    'contacts': {
        'add': {
            'contact': ['fullname', 'id', 'username'],
        },
        'delete': [],
        'getList': {
            'contacts': {
                'contact': ['fullname', 'id', 'username'],
            },
        },
    },
    'groups': {
        'add': {
            'group': ['id', 'name', {
                'contacts': [],
                },
            ],
        },
        'addContact': [],
        'delete': [],
        'getList': {
            'groups': {
                'group': ['id', 'name', {
                    'contact': ['id'],
                    },
                ],
            },
        },
        'removeContact': [],
    },
    'lists': {
        'add': _LIST_COMMON,
        'archive': _LIST_COMMON,
        'delete': _LIST_COMMON,
        'getList': {
            'lists': _LIST_COMMON,
        },
        'setDefaultList': [],
        'setName': _LIST_COMMON,
        'unarchive': _LIST_COMMON,
    },
    'locations': {
        'getList': {
            'locations': {
                'location': ['address', 'id', 'latitude', 'longitude',
                             'name', 'viewable', 'zoom'],
            },
        },
    },
    'reflection': {
        'getMethodInfo': {
            'method': [
                'name', 'needslogin', 'needssigning', 'requiredperms',
                {
                    'description': [],
                },
                {
                    'response': [],
                },
                {
                    'arguments': {
                        'artument': ['name', 'optional'],
                    },
                },
                {
                    'errors': {
                        'error': ['code', 'message'],
                    },
                },
            ],
        },
        'getMethods': {
            'methods': {
                'method': [],
            },
        },
    },
    'settings': {
        'getList': {
            'settings': {
                'dateformat': [],
                'defaultlist': [],
                'language': [],
                'timeformat': [],
                'timezone': [],
            },
        },
    },
    'tasks': {
        'add': _TASK_COMMON,
        'addTags': _TASK_TAGS,
        'complete': _TASK_COMMON,
        'delete': _TASK_COMMON,
        'getList': _TASK_COMMON,
        'movePriority': _TASK_COMMON,
        'moveTo': _TASK_TAGS,
        'postpone': _TASK_COMMON,
        'removeTags': _TASK_TAGS,
        'setDueDate': _TASK_COMMON,
        'setEstimate': _TASK_COMMON,
        'setLocation': _TASK_COMMON,
        'setName': _TASK_COMMON,
        'setPriority': _TASK_COMMON,
        'setRecurrence': _TASK_RRULE,
        'setTags': _TASK_TAGS_RRULE,
        'setURL': _TASK_COMMON,
        'uncomplete': _TASK_COMMON,
    },
    'tasksNotes': {
        'add': {
            'note': ['created', 'id', 'modified', 'title'],
        },
        'delete': [],
        'edit': {
            'note': ['created', 'id', 'modified', 'title'],
        },
    },
    'test': {
        'echo': {
            'method': [],
        },
        'login': {
            'user': ["id", {
                "username": [],
                },
            ],
        },
    },
    'time': {
        'convert': {
            'time': ['timezone'],
        },
        'parse': {
            'time': ['precision'],
        },
    },
    'timelines': {
        'create': {
            'timeline': [],
        },
    },
    'timezones': {
        'getList': {
            'timezones': {
                'timezone': ['current_offset', 'dst', 'id', 'name', 'offset'],
            },
        },
    },
    'transactions': {
        'undo': [],
    },
}
