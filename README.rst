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


# Installation and setup

This requires Django >= 1.10 and Python 2.7+ or 3.6+.
Not tested with Django 2.x.

1. Install the package
```
    pip install https://github.com/iskme/django-eventlog
```


2. in site/settings.py, define the following.
(Alternately, these may be set as environment variables):
```
    # eventlog configuration (logstash server)
    EVENTLOG_HOST = '172.17.0.1'
    EVENTLOG_PORT = 5001
    EVENTLOG_DB   = os.path.join(BASE_DIR, 'eventlog.db')

    # hostname identification for logging
    EVENTLOG_SITE = 'local'
    EVENTLOG_CLUSTER = 'local'
```

3. in site/settings.py, add the following to MIDDLEWARE

```
    'django_eventlog.middleware.EventLogMiddleware',
```
This should be placed after Session middleware so that
the session is initialized and the current user is established.

4. It may also be useful to update logging handlers in settings.py

5. Implement a handler to populate the "session" and "user"
fields of the Event object from the request. See ```examples/django-demo/mysite/__init__.py``` for an example.

After implementing the class, define the class name in ```settings.py```:

```
    EVENTLOG_SESSION_HELPER = 'mysite.SessionEventHelper'
```



# Usage

The usage is the same as described in the ```eventlog``` package.
