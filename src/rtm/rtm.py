# -*- coding: utf-8 -*-
# Python library for Remember The Milk API

__author__ = 'Sridhar Ratnakumar <http://purl.org/NET/srid/>'
__all__ = (
    'API',
    'API_RESPONSE',
    'createRTM',
    'set_log_level',
)


import json
import logging
from hashlib import md5

# rtm constant
from consts import *

try:  # Python 3
    from urllib.request import urlopen
    from urllib.parse import urlencode
except ImportError:  # Python 2.x
    from urllib import urlencode, urlopen
    input = raw_input

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class RTMError(Exception): pass

class RTMAPIError(RTMError): pass

class AuthStateMachine(object):

    class NoData(RTMError): pass

    def __init__(self, states):
        self.states = states
        self.data = {}

    def dataReceived(self, state, datum):
        if state not in self.states:
            raise RTMError('Invalid state <%s>' % state)
        self.data[state] = datum

    def get(self, state):
        if state in self.data:
            return self.data[state]
        else:
            raise AuthStateMachine.NoData('No data for <%s>' % state)


class RTM(object):

    def __init__(self, apiKey, secret, token=None):
        self.apiKey = apiKey
        self.secret = secret
        self.authInfo = AuthStateMachine(['frob', 'token'])

        # this enables one to do 'rtm.tasks.getList()', for example
        for prefix, methods in API.items():
            setattr(self, prefix, RTMAPICategory(self, prefix, methods))

        if token:
            self.authInfo.dataReceived('token', token)

    def _sign(self, params):
        "Sign the parameters with MD5 hash"
        pairs = ''.join(['%s%s' % (k, v) for k, v in sortedItems(params)])
        return md5((self.secret + pairs).encode('utf-8')).hexdigest()

    def get(self, **params):
        "Get the XML response for the passed `params`."
        params['api_key'] = self.apiKey
        params['format'] = 'json'
        params['api_sig'] = self._sign(params)

        data = openURL(SERVICE_URL, params).read()

        LOG.debug("JSON response: \n%s" % data)

        d = dottedDict('ROOT', json.loads(data.decode('utf-8')))
        rsp = d.rsp

        if rsp.stat == 'fail':
            raise RTMAPIError('API call failed - %s (%s)' % (
                rsp.err.msg, rsp.err.code))
        else:
            return rsp

    def getNewFrob(self):
        rsp = self.get(method='rtm.auth.getFrob')
        self.authInfo.dataReceived('frob', rsp.frob)
        return rsp.frob


    def getFrob(self):
        try:
            frob = self.authInfo.get('frob')
        except AuthStateMachine.NoData:
            frob = self.getNewFrob()
        return frob


    def setFrob(self, frob):
        self.authInfo.dataReceived('frob', frob)


    def getAuthURL(self):
        try:
            frob = self.authInfo.get('frob')
        except AuthStateMachine.NoData:
            frob = self.getNewFrob()

        params = {
            'api_key': self.apiKey,
            'perms': 'delete',
            'frob': frob
            }
        params['api_sig'] = self._sign(params)
        return AUTH_SERVICE_URL + '?' + urlencode(params)

    def getToken(self):
        frob = self.authInfo.get('frob')
        rsp = self.get(method='rtm.auth.getToken', frob=frob)
        self.authInfo.dataReceived('token', rsp.auth.token)
        return rsp.auth.token


class RTMAPICategory:
    "See the `API` structure and `RTM.__init__`"

    def __init__(self, rtm, prefix, methods):
        self.rtm = rtm
        self.prefix = prefix
        self.methods = methods

    def __getattr__(self, attr):
        if attr in self.methods:
            rargs, oargs = self.methods[attr]
            if self.prefix == 'tasksNotes':
                aname = 'rtm.tasks.notes.%s' % attr
            else:
                aname = 'rtm.%s.%s' % (self.prefix, attr)
            return lambda **params: self.callMethod(
                aname, rargs, oargs, **params)
        else:
            raise AttributeError('No such attribute: %s' % attr)

    def callMethod(self, aname, rargs, oargs, **params):
        # Sanity checks
        for requiredArg in rargs:
            if requiredArg not in params:
                raise TypeError('Required parameter (%s) missing' % (
                                requiredArg))

        for param in params:
            if param not in rargs + oargs:
                warnings.warn('Invalid parameter (%s)' % param)

        token = self.rtm.authInfo.get('token')
        if params.get('auth_token'):
            # auth.checkToken api needs auth_token parameter
            token = params.pop('auth_token')

        return self.rtm.get(method=aname, auth_token=token, **params)


# Utility functions

def sortedItems(dictionary):
    """ Return a list of (key, value) sorted based on keys
    >>> list(sortedItems({'a': 1, 1: 55, 'key': 7}))
    [(1, 55), ('a', 1), ('key', 7)]
    """
    keys = list(dictionary.keys())
    keys.sort(key=str)
    for key in keys:
        yield key, dictionary[key]

def openURL(url, queryArgs=None):
    """
    >>> q = {'query': 'test'}
    >>> r = openURL('http://www.rememberthemilk.com/', q)
    >>> r.geturl()
    'http://www.rememberthemilk.com/?query=test'
    """
    if queryArgs:
        url = url + '?' + urlencode(queryArgs)
    LOG.debug("URL> %s", url)
    return urlopen(url)

class dottedDict(object):
    """Make dictionary items accessible via the object-dot notation."""

    def __init__(self, name, dictionary):
        self._name = name
        self._dictionary = dictionary

        if type(dictionary) is dict:
            for key, value in dictionary.items():
                if type(value) is dict:
                    value = dottedDict(key, value)
                elif type(value) in (list, tuple) and key != 'tag':
                    value = [dottedDict('%s_%d' % (key, i), item)
                             for i, item in indexed(value)]
                setattr(self, key, value)
        else:
            raise ValueError('not a dict: %s' % dictionary)

    def __dict__(self):
        return self._dictionary

    def __repr__(self):
        return str(self._dictionary)
        # children = [c for c in dir(self) if not c.startswith('_')]
        # return 'dotted <%s> : %s' % (
        #     self._name,
        #     ', '.join(children))

def indexed(seq):
    """
    >>> list(indexed(['a', 'b', 'c']))
    [(0, 'a'), (1, 'b'), (2, 'c')]
    """
    index = 0
    for item in seq:
        yield index, item
        index += 1

def createRTM(apiKey, secret, token=None):
    rtm = RTM(apiKey, secret, token)
    return rtm

def set_log_level(level):
    '''Sets the log level of the logger used by the module.

    >>> import rtm
    >>> import logging
    >>> rtm.set_log_level(logging.INFO)
    '''

    LOG.setLevel(level)
