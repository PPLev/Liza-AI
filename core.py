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
        self.callbacks = []

    def register(self, filt: MagicFilter = None):
        def wrapper(func: callable):
            if filt:
                async def wrapper_(*args, **kwargs):
                    if "for_filter" in kwargs:
                        for_filter = kwargs.pop("for_filter")
                    else:
                        raise NotFoundFilerTextError

                    if filt.resolve(for_filter):
                        asyncio.run_coroutine_threadsafe(func(*args, **kwargs), asyncio.get_event_loop())
            else:
                async def wrapper_(*args, **kwargs):
                    if "for_filter" in kwargs:
                        kwargs.pop("for_filter")
                    asyncio.run_coroutine_threadsafe(func(*args, **kwargs), asyncio.get_event_loop())

            self.callbacks.append(wrapper_)

        return wrapper

    async def event(self, *args, **kwargs):
        for callback in self.callbacks:
            await callback(*args, **kwargs)


class Core(JaaCore, metaclass=MetaSingleton):
    def __init__(self):
        super().__init__()

        self.print_red = lambda txt: cprint(txt, "red")
        self.format_print_key_list = lambda key, value: print(colored(key + ": ", "blue") + ", ".join(value))
        self.on_input = EventObserver()
        self.on_output = EventObserver()

    async def run_input(self, input_str=None):
        await self.on_input.event(core=self, input_str=input_str, for_filter=input_str)

    async def run_output(self, output_str=None):
        await self.on_output.event(core=self, output_str=output_str, for_filter=output_str)

    @staticmethod
    async def start_loop():
        while True:
            await asyncio.sleep(0)

    @staticmethod
    async def reboot():
        # No recommend
        python = sys.executable
        os.execl(python, python, *sys.argv)


async def main():
    core = Core()
    await core.init_plugins()
    await core.start_loop()


if __name__ == '__main__':
    asyncio.run(main())
