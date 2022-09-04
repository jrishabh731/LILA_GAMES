import abc


class CacheAbstract(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_key(self, key):
        pass

    @abc.abstractmethod
    def set_key(self, key, value, ttl=None):
        pass
