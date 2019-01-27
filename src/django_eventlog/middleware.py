import time
from django.conf import settings
from random import random
from . thread_data import getCurrentRequest, getRequestId, setCurrentRequest, setRequestId
_sessionHelper = None


# returns tuple of requestId, user, sessionId
# This hook allows Events to contain user and sessionid, even if the Event
# is created deep in the call stack where the 'request' object is not available.
def getUserContext():
    req, reqid = getCurrentRequest(), getRequestId()
    user, session = '', ''
    if req and _sessionHelper:
        (user, session) = _sessionHelper(req)
    return (reqid, user, session)


# get app-defined helper function for
# retrieving user and session id
if getattr(settings, 'EVENTLOG_SESSION_HELPER', None):
    import importlib
    helper = settings.EVENTLOG_SESSION_HELPER
    (mod, cls) = helper.rsplit('.', 1)
    clasz = getattr(importlib.import_module(mod), cls)
    _sessionHelper = clasz()


class EventLogMiddleware(object):

    def __init__(self, processRequest):
        self.processRequest = processRequest

        # start counter with a 32-bit int, but could be transferred as 64-bit int
        # Properties of reqid:
        # 1. randomness should provide uniqueness for sessions on same day
        #    even across sites (e.g., host/reqid )
        # 2. all events associated with a request have the same pid/reqid
        # 3. requests are increasing for same server until server restarts
        self.reqid = int(random()*0xffffffff)

        # defer defining logEvent so django can initialize alternate handler
        from eventlog import Event, initMiddleware, defaultEventHandler
        # set up callback so eventlog package can initialize
        # request-related information (reqid, user, session)
        initMiddleware(getUserContext)
        # use django-defined handler if defined,
        # otherwise, use system default
        try:
            self.logEvent = settings.EVENT_HANDLER.logEvent
        except Exception:
            self.logEvent = defaultEventHandler().logEvent
        self._Event = Event

    def logHttpEvent(self, request, response, duration):
        rmeta = request.META
        forwardedFor = rmeta.get('HTTP_X_FORWARDED_FOR', None)
        if forwardedFor is not None:
            # make it a list
            forwardedFor = forwardedFor.replace(' ', '').split(',')

        event = self._Event(
            name='http_request',
            target=request.path,
            message=request.body,
            fields={
                'status': response.status_code,
                'duration': duration,
                'remoteHost':  request.get_host(),
                'path': request.path,  # (full path, not including query params)
                'method':  rmeta.get('REQUEST_METHOD', '').lower(),
                'userAgent': rmeta.get('HTTP_USER_AGENT', ''),
                'remoteAddr': rmeta.get('REMOTE_ADDR', ''),
                'query': rmeta.get('QUERY_STRING', ''),
                'referer':  rmeta.get('HTTP_REFERER', ''),
                'body': request.body,  # post body
                'forwardedProto': rmeta.get('HTTP_X_FORWARDED_PROTO', None),
                'forwardedFor': forwardedFor,
            },
        )
        self.logEvent(event)

    def __call__(self, request):
        self.reqid = self.reqid + 1
        setRequestId(self.reqid)
        setCurrentRequest(request)
        startTime = time.clock()
        try:
            response = self.processRequest(request)
            self.logHttpEvent(request, response, time.clock()-startTime)
            return response
        finally:
            setCurrentRequest(None)
            setRequestId(0)
