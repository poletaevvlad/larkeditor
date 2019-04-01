from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable, Tuple

T = TypeVar("T")
Callback = Callable[[T], None]


class BaseObservable(ABC):
    def __init__(self):
        self.callbacks = list()

    def call_callback(self):
        for callback in self.callbacks:
            callback(*self.get_callback_args())

    def bind(self, callback):
        self.callbacks.append(callback)
        callback(*self.get_callback_args())

    def unbind(self, callback):
        self.callbacks.remove(callback)

    @abstractmethod
    def get_callback_args(self):
        pass


class Observable(BaseObservable, Generic[T]):
    def __init__(self, value: T):
        super().__init__()
        self.value: T = value

    def set(self, value: T):
        if self.value != value:
            self.value = value
            self.call_callback()

    def get_callback_args(self):
        return self.value,


class ObservableUnion(BaseObservable):
    def __init__(self, *values: Observable):
        super().__init__()
        self.values: Tuple[Observable] = values
        for observable in values:
            observable.bind(lambda x: self.call_callback())

    def get_callback_args(self):
        return (o.value for o in self.values)
