# -*- coding: utf-8 -*-
import itertools
import os
import plistlib
import sys
from xml.etree.ElementTree import Element, SubElement, tostring
import subprocess
import unicodedata

_MAX_RESULTS = 100
UNESCAPE_CHARACTERS = u"""\\ ()[]{};`'"$"""

preferences = plistlib.readPlist('info.plist')
bundleid = preferences['bundleid']


class Item(object):

    @classmethod
    def unicode(cls, value):
        try:
            items = value.iteritems()
        except AttributeError:
            return unicode(value)
        else:
            return dict(map(unicode, item) for item in items)

    def __init__(self, attributes, title, subtitle, icon=None):
        self.attributes = attributes
        self.title = title
        self.subtitle = subtitle
        self.icon = icon

    def __str__(self):
        return tostring(self.xml(), encoding='utf-8')

    def xml(self):
        item = Element(u'item', self.unicode(self.attributes))
        SubElement(item, u'title').text = unicode(self.title)
        SubElement(item, u'subtitle').text = unicode(self.subtitle)
        for attribute in [u'icon']:
            value = getattr(self, attribute)
            if value is None:
                continue
            try:
                (value, attributes) = value
            except:
                attributes = {}
            SubElement(item, attribute, self.unicode(attributes)).text = unicode(value)
        return item


def args(characters=None):
    return tuple(unescape(decode(arg), characters) for arg in sys.argv[1:])


def args2():
    return (sys.argv[1], decode(' '.join(sys.argv[2:])))


def config():
    return _create('config')


def decode(s):
    return unicodedata.normalize('NFC', s.decode('utf-8'))


def uid(uid):
    return u'-'.join(map(unicode, (bundleid, uid)))


def unescape(query, characters=None):
    for character in (UNESCAPE_CHARACTERS if (characters is None) else characters):
        query = query.replace('\\%s' % character, character)
    return query


def work(volatile):
    path = {
        True: '~/Library/Caches/com.runningwithcrayons.Alfred-2/Workflow Data',
        False: '~/Library/Application Support/Alfred 2/Workflow Data'
    }[bool(volatile)]
    return _create(os.path.join(os.path.expanduser(path), bundleid))


def write(text):
    sys.stdout.write(text)


def xml(items):
    root = Element('items')
    for item in itertools.islice(items, _MAX_RESULTS):
        root.append(item.xml())
    return tostring(root, encoding='utf-8')


def _create(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    if not os.access(path, os.W_OK):
        raise IOError('No write access: %s' % path)
    return path


def show(query):
    subprocess.call(
        'osascript -e "tell application \\"Alfred 2\\" to search \\"' + query + '\\""',
        shell=True
    )
