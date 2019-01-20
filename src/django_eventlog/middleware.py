import time
from django.conf import settings
from eventlog import Event, initMiddleware, logEvent
from random import random
from . thread_data import getCurrentRequest, getRequestId, setCurrentRequest, setRequestId
_sessionHelper = None


# returns tuple of requestId, user, sessionId
# this is a hook invoked by the eventlog package
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

        # set up callback so eventlog package can initialize
        # request-related information (reqid, user, session)
        initMiddleware(getUserContext)

        # start counter with a 32-bit int, but could be transferred as 64-bit int
        # Properties of reqid:
        # 1. randomness should provide uniqueness for sessions on same day
        #    even across sites (e.g., host/reqid )
        # 2. all events associated with a request have the same pid/reqid
        # 3. requests are increasing for same server until server restarts
        self.reqid = int(random()*0xffffffff)

    def forwardedFor(self, request):
        ff = request.META.get('HTTP_X_FORWARDED_FOR', None)
        if ff is not None:
            # make it a list
            return ff.replace(' ', '').split(',')
        else:
            return None

    def logHttpEvent(self, request, response, duration):
        method = request.META.get('REQUEST_METHOD', '').lower()
        event = Event(
            name='http_request',
            target=request.path,
            message=request.body,
            fields={
                'status': response.status_code,
                'duration': duration,
                'remoteHost':  request.get_host(),
                'path': request.path,  # (full path, not including query params)
                'method':  method,
                'userAgent': request.META.get('HTTP_USER_AGENT', ''),
                'remoteAddr': request.META.get('REMOTE_ADDR', ''),
                'query': request.META.get('QUERY_STRING', ''),
                'referer':  request.META.get('HTTP_REFERER', ''),
                'body': request.body,  # post body
                'forwardedProto': request.META.get('HTTP_X_FORWARDED_PROTO', None),
                'forwardedFor': self.forwardedFor(request),
            },
        )
        logEvent(event)

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
