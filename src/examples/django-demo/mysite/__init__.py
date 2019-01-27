# mysite.__init__.py


# this class implements a callback to determine the current user id and session id
# from the current request. Userid can be any unique string.
#
# "user" is the unique user id of the logged in user, or some other string ("guest") if the user is not logged in
# "session" should be a unique session identifier that is associated with a user login session
#
# It is preferable not to use an email address for the user id, to reduce the risk of PII entering the logging database
#
# This middleware should be invoked after session middleware
# so that session data is populated.
# Middleware ordering is defined in settings.py "MIDDLEWARE"
class SessionEventHelper(object):

    # return tuple (user,session) if user is logged in,
    # or ('guest','0') for guest users
    def getUserSession(self, request):

        if request and getattr(request, 'session', False):
            return (request.user, request.session)

        # if user is not logged in, return a unique token for guest/anonymous user
        return ('guest', '0')


    # tip: if session id is expensive to compute (e.g., has to be loaded from redis),
    # it can be cached in the request object as follows:

    #    if getattr(request, mySessionId, None) is None:
    #        # (perform expensive computation to calculate user&session ids)
    #        # then save them in request object
    #        request.mySessionId = '1234'
    #        request.myUserId = 'Mickey'
    #    return (request.myUserId, request.mySessionId)
