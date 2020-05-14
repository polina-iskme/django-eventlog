Django Event Logging Middleware
===============================

Django middleware for logging events. Events are put on a queue
and processed by a separate worker thread
(one thread total per server) to avoid
http request processing. The worker thread
sends the event asynchronously to a logstash server.
For greater resiliency against network errors
and intermittent log server availability, events
are saved in a persistent queue (a local sqlite database).
When the logging server is again availble,
queued events are sent and removed from the queue.

This package depends on [eventlog](https://github.com/iskme/eventlog),
which manages the queue and sending to logstash.
The middleware defined by this package logs each incoming
http request and sets up some "globals"
so that when events are logged by application
code, the event includes fields
(such as user id and requeust number) that
associate it with the http request.


Installation and setup
----------------------

This requires Django >= 1.10 and Python 2.7+ or 3.6+.
Not tested with Django 2.x.

1. Install the package::

    pip install https://github.com/iskme/django-eventlog



2. in site/settings.py, define the following.
(Alternately, these may be set as environment variables)::

    # EVENTLOG_HOST is Host name or IP address of logproxy server
    # to use console loging only, set EVENTLOG_HOST=""
    EVENTLOG_HOST = '172.17.0.1'
    # EVENTLOG_PORT is port number of logproxy listener
    EVENTLOG_PORT = 6801
    # EVENTLOG_CLIENT is a slug for client name
    EVENTLOG_CLIENT = "acme"
    # EVENTLOG_DATACTR is the datacenter or zone where servers are located
    EVENTLOG_DATACTR = "us-east-1"
    # EVENTLOG_CLUSTER is a cluster id within the data center, if applicable
    EVENTLOG_CLUSTER = ""
    # EVENTLOG_DEPLOY is an integer code for deploy type
    # 0: production, 1:staging, 2:development, 3:testing,
    # 4: demo, 5:pilot
    EVENTLOG_DEPLOY = 0

    # EVENTLOG_SESSION_HELPER is an optional function to return the
    #    user id and session id from the request object.
    #    A default implementation is in middleware.py, which should work
    #    if there's nothing special about your session object.
    #EVENTLOG_SESSION_HELPER = 'mysite.SessionEventHelper'


3. in site/settings.py, add the following to MIDDLEWARE::

    'django_eventlog.middleware.EventLogMiddleware'

This should be placed after Session middleware so that
the session is initialized and the current user is established.

