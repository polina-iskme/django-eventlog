import time
import random
from django.conf import settings
from . thread_data import getCurrentRequest, setCurrentRequest
from eventlog.event_pb2 import HttpMethod

_sessionHelper = None


# returns tuple of user, sessionId
# This hook allows Events to contain user and sessionid, even if the Event
# is created deep in the call stack where the 'request' object is not available.
def getUserContext():
    req = getCurrentRequest()
    user, session = '', ''
    if req and _sessionHelper:
        (user, session) = _sessionHelper(req)
    return (user, session)


# default SessionEventHelper, if it's not overridden in settings
class SessionEventHelper(object):
    # return tuple (user,session) if user is logged in,
    # or ('guest','0') for guest users
    def getUserSession(self, request):
        if request and getattr(request, 'session', False):
            return (request.user, request.session)
        # if user is not logged in, return a unique token
        # for guest/anonymous user
        return ('guest', '0')


# get app-defined helper function for
# retrieving user and session id
if getattr(settings, 'EVENTLOG_SESSION_HELPER', None):
    import importlib
    helper = settings.EVENTLOG_SESSION_HELPER
    (mod, cls) = helper.rsplit('.', 1)
    clasz = getattr(importlib.import_module(mod), cls)
    _sessionHelper = clasz()
else:
    _sessionHelper = SessionEventHelper()

class EventLogMiddleware(object):

    def __init__(self, processRequest):
        self.processRequest = processRequest

        # defer defining logEvent so django can initialize alternate handler
        from eventlog import newEvent, initMiddleware, defaultEventHandler
        # set up callback so eventlog package can initialize
        # request-related information (user, session)
        initMiddleware(getUserContext)
        # use django-defined handler if defined,
        # otherwise, use system default
        try:
            self.logEvent = settings.EVENT_HANDLER.logEvent
        except Exception:
            self.logEvent = defaultEventHandler().logEvent
        self.newEvent = newEvent

    def logHttpEvent(self, request, response, duration):
        rmeta = request.META
        forwardedFor = rmeta.get('HTTP_X_FORWARDED_FOR', None)
        if forwardedFor is not None:
            # make it a list
            forwardedFor = forwardedFor.replace(' ', '').split(',')
        e = self.newEvent(
            name='http_request',
            target=request.path,
            value=response.status_code,
            duration = duration
            )
        e.http.status = response.status_code
        e.http.method = HttpMethod.Value(rmeta.get('REQUEST_METHOD', '').upper())
        e.http.path = request.path  # (full path, not including query params)
        e.http.query = rmeta.get('QUERY_STRING', '')
        e.http.remote_host = request.get_host()
        e.http.remote_addr = rmeta.get('REMOTE_ADDR', '')
        e.http.referer = rmeta.get('HTTP_REFERER', '')
        e.http.user_agent = rmeta.get('HTTP_USER_AGENT', '')
        e.http.body = request.body
        e.http.forwarded_proto = rmeta.get('HTTP_X_FORWARDED_PROTO', '')
        e.http.forwarded_for = rmeta.get('HTTP_X_FORWARDED_FOR', '')
        self.logEvent(e)

    def __call__(self, request):
        setCurrentRequest(request)
        startTime = time.clock()
        try:
            response = self.processRequest(request)
            self.logHttpEvent(request, response, time.clock()-startTime)
            return response
        finally:
            setCurrentRequest(None)
