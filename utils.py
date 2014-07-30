class Event:
    def __init__(self):
        self.__list = []

    def __call__(self, *args, **kwords):
        for cb  in self.__list:
            cb(*args, **kwords)

    def register(self, cb):
        self.__list.append(cb)

class EventSource(object):
    def __init__(self):
        self.__events = dict()

    def connect(self, eventName, callback):
        self.__events.setdefault(eventName, Event()).register(callback)

    def event(self, eventName):
        return self.__events.get(eventName, Event())
