from urlparse import urlparse
import os
import subprocess
import re
import config
import itemlist
from subprocess import call
import HTMLParser
import config_keys as ck

def smartcontent_enabled():
    return config.get(ck.KEY_FEATURE_SMARTCONTENT) == True


def smartcontent_pagetitle_enabled():
    return config.get(ck.KEY_FEATURE_SMARTCONTENT_PAGETITLE) == True


def perform_action(_id):
    content = itemlist.get_todo(_id)['title']
    (action, content) = analyse_content(content)
    smartcontent_actions = {
        'copy_to_clipboard': lambda _id, content: itemlist.copy_todo_to_clipboard(_id),
        'open_url': lambda _id, content: open_url(content),
        'open_file': lambda _id, content: open_url(content),
        'open_dir': lambda _id, content: open_url(content)
    }
    smartcontent_actions[action](_id, content)


def open_url(content):
    config.update_state(command='open_url')
    call(['open', content])


def analyse_content(content):
    content_action = 'copy_to_clipboard'
    # Directory
    if os.path.exists(content) and os.path.isdir(content):
        content_action = 'open_dir'
    # File
    elif os.path.exists(content):
        content_action = 'open_file'
    else:
        # URL
        pieces = urlparse(content)
        if (pieces.scheme in ['http', 'https', 'ftp'] and len(pieces.netloc) > 0):
            content_action = 'open_url'
        elif len(pieces.path) > 0 and pieces.path.find('.') > 0 and pieces.path.find(' ') < 0 and not os.path.exists(pieces.path):
            fragments = pieces.path.split('.')
            invalid = [f for f in fragments if len(f) < 2]
            if len(invalid) == 0:
                content_action = 'open_url'
                content = "http://" + content
    return (content_action, content)


def process_todo(t):
    if smartcontent_enabled():
        (content_action, content) = analyse_content(t['title'])
        if content_action == 'open_url':
            t['smartcontent_type'] = 'Web'
            if smartcontent_pagetitle_enabled():
                t['smartcontent_info'] = get_page_title(t['title'])
            else:
                t['smartcontent_info'] = ''
        elif content_action == 'open_dir':
            head, tail = os.path.split(os.path.abspath(content))
            t['smartcontent_type'] = 'Application' if tail.endswith('.app') else 'Directory'
            t['smartcontent_info'] = tail
        elif content_action == 'open_file':
            head, tail = os.path.split(content)
            t['smartcontent_type'] = 'File'
            t['smartcontent_info'] = tail


def get_page_title(content):
    proc = subprocess.Popen(["curl", "-sL", content], stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
    matches = re.match(r".*?<title>(?P<title>.*?)</title>", out, re.S | re.IGNORECASE)
    if not matches:
        title = u""
    else:
        title = matches.group('title')
        try:
            h = HTMLParser.HTMLParser()
            title = h.unescape(title.decode('utf-8'))
        except:
            pass
    return title.strip()
