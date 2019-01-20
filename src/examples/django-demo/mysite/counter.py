from django.http import HttpResponse
import logging

from eventlog import Event, defaultAsyncLogger
logEvent = defaultAsyncLogger().logEvent


logger = logging.getLogger('mysite-counter')
logger.addHandler(defaultAsyncLogger())
logger.setLevel(logging.DEBUG)

# A simple counter object that logs changes
class Counter(object):

  def __init__(self, name, initialValue=0):
    self.value = initialValue
    self.name = name or "count"

  def get(self):
    return self.value

  def set(self,val):
    self.value = val
    # record counter.set event
    logEvent(Event(self.name + "_set","", value=self.value))
    return self.value

  def inc(self,amt):
    self.value += amt
    # record counter.increment event
    logEvent(Event(self.name + "_increment", "", value=self.value, \
                   fields={'amount':amt}))
    return self.value



# counterAPI provides rest api for manipulating counter
class CounterAPI:

    def __init__(self, name, initialValue=0):
        self.counter = Counter(name, initialValue)

    def _makeResponse(self):
        return HttpResponse("value=%d\n" % self.counter.get(),
          content_type = 'text/plain')

    def get(self, request):
        return self._makeResponse()

    def set(self, request, val):
        self.counter.set(int(val))
        return self._makeResponse()

    def inc(self, request, amt=1):
        self.counter.inc(int(amt))
        return self._makeResponse()
