from django.http import HttpResponse
import logging

from eventlog import Event, asyncEventLogger
logEvent = asyncEventLogger.logEvent


logger = logging.getLogger('mysite-counter')
logger.addHandler(asyncEventLogger)
logger.setLevel(logging.DEBUG)

counter = { 'value': 0 }

class Counter(object):

  def __init__(self, initialValue=0):
    self.value = initialValue

  def getVal(self):
    return self.value

  def setVal(self,val):
    self.value = val
    # record counter.set event
    logEvent(Event('set','counter',metrics=[('value',self.value)]))

  def incrementVal(self,amt):
    self.value += amt
    # record counter.increment event
    logEvent(Event('increment','counter',metrics=[('amount', amt),('value',self.value)]))


_counter = Counter()


def set(request, val='0'):
  logger.debug("view.set, val=%s" % val)
  _counter.setVal(int(val))
  return HttpResponse("Counter value is now %d\n" % _counter.getVal(),
          content_type = 'text/plain')

def increment(request, amt='1'):
  logger.debug("view.increment, amt=%s" % amt)
  _counter.incrementVal(int(amt))
  return HttpResponse("Counter value is now %d\n" % _counter.getVal(),
          content_type = 'text/plain')

