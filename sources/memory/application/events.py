
from collections import MutableMapping
from utils.properties import lazy, roproperty
from ..generic import MemoryBase
from .catalogs import MemoryEventsCatalog, MemoryEventsDynamicCatalog
from .event import MemoryEventSketch


class MemoryEvents(MemoryBase, MutableMapping):

    def __init__(self, owner):
        self._owner = owner

    @lazy
    def _items(self):
        return {}

    @lazy
    def _all_items(self):
        return self._owner.application.events.catalog._items

    @lazy
    def _catalog(self):
        if self._owner.is_application:
            return MemoryEventsCatalog(self)
        else:
            return MemoryEventsDynamicCatalog(self)

    owner = roproperty("_owner")
    catalog = roproperty("_catalog")

    def new_sketch(self, name, restore=False):

        def on_complete(item):
            with self._owner.lock:
                self._items[item.source_object.id, item.name] = item

                if not self._owner._virtual:
                    self._all_items[item.source_object.id, item.name] = item

                if not restore:
                    self._owner.autosave()

        return MemoryEventSketch(on_complete, self._owner, name)

    def new(self, name):
        item = self.new_sketch(name)
        return ~item

    def clear(self):
        with self._owner.lock:
            if not self._owner._virtual:
                for key in self._items:
                    del self._all_items[key]
            self._items.clear()
            self._owner.autosave()

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key, value):
        raise Exception(u"Use 'new' to create new event")

    def __delitem__(self, key):
        with self._owner.lock:
            if not self._owner._virtual:
                del self._all_items[key]
            del self._items[key]
            self._owner.autosave()

    def __iter__(self):
        return iter(self.__dict__.get("_items", ()))

    def __len__(self):
        return len(self.__dict__.get("_items", ()))

    def __str__(self):
        return "events of %s" % self._owner
