import asyncio

from magic_filter import MagicFilter
from termcolor import cprint, colored
import logging
from jaa import JaaCore

F = MagicFilter()
version = "0.0.1"

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",
                    level=logging.DEBUG)


class NotFoundFilerTextError(BaseException):
    pass


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Filter:
    def __init__(self, filt: MagicFilter):
        self.filt = filt

    def __call__(self, fn):
        @self.filt.cast
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper


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
                        await func(*args, **kwargs)
            else:
                async def wrapper_(*args, **kwargs):
                    if "for_filter" in kwargs:
                        kwargs.pop("for_filter")
                    await func(*args, **kwargs)

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
        await self.on_input.event(self, input_str=input_str, for_filter=input_str)

    async def run_output(self, output_str=None):
        await self.on_output.event(self, output_str=output_str, for_filter=output_str)

    async def init_with_plugins(self):
        await self.init_plugins()

    async def start_loop(self):
        while True:
            await asyncio.sleep(0)


core = Core()


async def main():
    await core.init_with_plugins()
    await core.start_loop()


if __name__ == '__main__':
    asyncio.run(main())
