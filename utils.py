# This file is part of Edia.
#
# Ediap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Edia is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Edia.  If not, see <http://www.gnu.org/licenses/>

# Copyright 2014 Matthieu Gautier dev@mgautier.fr

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

