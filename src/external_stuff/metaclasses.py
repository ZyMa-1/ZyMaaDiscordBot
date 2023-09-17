from typing import Type, TypeVar

T = TypeVar('T')


class SingletonMeta(type):
    _instances = {}

    def __call__(cls: Type[T], *args, **kwargs):
        if cls not in cls._instances:
            instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def get_instance(self: Type[T]) -> T:
        try:
            return self._instances.get(self)
        except KeyError:
            raise KeyError("Singleton instance has not been created yet")
