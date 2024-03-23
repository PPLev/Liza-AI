import asyncio
import os
import sys

from magic_filter import MagicFilter
from termcolor import cprint, colored
import logging
from jaa import JaaCore

F = MagicFilter()
version = "0.0.1"

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",
                    level=logging.INFO)


class NotFoundFilerTextError(BaseException):
    pass


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class EventObserver:
    def __init__(self):
        self.callbacks = {}

    async def _run_callback(self, callback, *args, **kwargs):
        try:
            await callback(*args, **kwargs)
        except Exception as exc:
            logging.exception(f'Сопрограмма вызвала исключение: {exc}')

    def register(self, filt: MagicFilter = None):
        def wrapper(func: callable):
            if filt:
                async def wrapper_(*args, **kwargs):
                    if "for_filter" in kwargs:
                        for_filter = kwargs.pop("for_filter")
                    else:
                        raise NotFoundFilerTextError

                    if filt.resolve(for_filter):
                        asyncio.run_coroutine_threadsafe(
                            coro=self._run_callback(func, *args, **kwargs),
                            loop=asyncio.get_event_loop()
                        )

            else:
                async def wrapper_(*args, **kwargs):
                    if "for_filter" in kwargs:
                        kwargs.pop("for_filter")

                    asyncio.run_coroutine_threadsafe(
                        coro=self._run_callback(func, *args, **kwargs),
                        loop=asyncio.get_event_loop()
                    )

            self.callbacks[f"{func.__module__}.{func.__name__}"] = wrapper_

        return wrapper

    async def __call__(self, *args, **kwargs):
        for callback in self.callbacks.values():
            await callback(*args, **kwargs)


class Core(JaaCore, metaclass=MetaSingleton):
    def __init__(self, observer_list=["on_input", "on_output"]):
        super().__init__()

        for observer in observer_list:
            self.add_observer(observer)

    def add_observer(self, observer_name):
        setattr(self, observer_name, EventObserver())

    @staticmethod
    async def start_loop():
        while True:
            await asyncio.sleep(0)

    @staticmethod
    async def _reboot():
        # No recommend for use
        python = sys.executable
        os.execl(python, python, *sys.argv)
