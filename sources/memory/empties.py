
from collections import MutableSet


class ChangeEmptyError(Exception):
    pass


class EmptySet(MutableSet):

    def add(self, element):
        raise ChangeEmptyError

    def discard(self, element):
        pass

    def __contains__(self, value):
        return False

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0
