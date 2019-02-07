import threading


def _globalStorage():
    tl = threading.local()
    if not hasattr(tl, 'eventGlobals'):
        tl.eventGlobals = {}
    return tl.eventGlobals


def setGlobal(key, val):
    _globalStorage()[key] = val


def getGlobal(key, defaultVal=None):
    return _globalStorage().get(key, defaultVal)


def unsetGlobal(key):
    try:
        del _globalStorage()[key]
    except KeyError:
        pass


# function to get current request object from thread local storage
# this is called by eventlogging to add sessionId,userId to each event record
def getCurrentRequest():
    return getGlobal('request', None)


def setCurrentRequest(req):
    setGlobal('request', req)
