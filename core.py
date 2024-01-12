import asyncio

from magic_filter import MagicFilter
from termcolor import cprint, colored
import logging
from jaa import JaaCore

F = MagicFilter()
version = "0.0.1"

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",
                    level=logging.DEBUG)


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


class NotFoundFilerTextError(BaseException):
    pass


class EventObserver:
    def __init__(self):
        self.callbacks = []

    def register(self, filt: MagicFilter = None):
        def filt_wrap(func: callable):
            if filt:
                async def wrapper(*args, **kwargs):
                    if "for_filter" in kwargs:
                        for_filter = kwargs.pop("for_filter")
                    else:
                        raise NotFoundFilerTextError

                    if filt.resolve(for_filter):
                        await func(*args, **kwargs)
            else:
                async def wrapper(*args, **kwargs):
                    if "for_filter" in kwargs:
                        kwargs.pop("for_filter")
                    await func(*args, **kwargs)

            self.callbacks.append(wrapper)

        return filt_wrap

    async def event(self, *args, **kwargs):
        for callback in self.callbacks:
            await callback(*args, **kwargs)


class Core(JaaCore, metaclass=MetaSingleton):

    def __init__(self):
        super().__init__()

        self.ttsEngineId = []
        self.playwavs = {}
        self.playWavEngineId = ""
        self.ttss = {}
        self.print_red = lambda txt: cprint(txt, "red")
        self.format_print_key_list = lambda key, value: print(colored(key + ": ", "blue") + ", ".join(value))
        self.on_input = EventObserver()
        self.on_output = EventObserver()

    # def on_input(self, func: callable):
    #     async def wrapper(*args, **kwargs):
    #         await func(*args, **kwargs)
    #
    #     self.on_input_list.append(wrapper)
    #     return wrapper
    #
    # def on_output(self, func: callable):
    #     def wrapper(*args, **kwargs):
    #         return func(*args, **kwargs)
    #
    #     self.on_output_list.append(wrapper)
    #
    # def assimilate(self, func: callable):
    #     def wrapper(*args, **kwargs):
    #         return func(*args, **kwargs)
    #
    #     return wrapper
    #
    # def with_rgs(self, func: callable, pack_name):
    #     def wrapper(*args, **kwargs):
    #         func(pack_name, *args, **kwargs)
    #
    #     return wrapper
    #
    async def run_input(self, input_str=None):
        await self.on_input.event(self, input_str=input_str, for_filter=input_str)

    async def run_output(self, output_str=None):
        await self.on_output.event(self, output_str=output_str, for_filter=output_str)

    #
    # async def run_output(self, output_str):
    #     await self.output.event(self, output_str)
    #
    #
    async def init_with_plugins(self):
        await self.init_plugins()
    #
    # def display_init_info(self):
    #     cprint("VoiceAssistantCore v{0}:".format(version), "blue", end=' ')
    #     print("run ONLINE" if self.isOnline else "run OFFLINE")
    #
    #     self.format_print_key_list("TTS engines", self.ttss.keys())
    #     self.format_print_key_list("PlayWavs engines", self.playwavs.keys())
    #     self.format_print_key_list("FuzzyProcessor engines", self.fuzzy_processors.keys())
    #     self.format_print_key_list("Assistant names", self.voiceAssNames)
    #
    #     cprint("Commands list: " + "#" * 65, "blue")
    #     for plugin in self.plugin_commands:
    #         self.format_print_key_list(plugin, self.plugin_commands[plugin])
    #     cprint("#" * 80, "blue")
    async def start_loop(self):
        while True:
            await asyncio.sleep(0)


core = Core()


async def main():
    await core.init_with_plugins()
    await core.start_loop()


if __name__ == '__main__':
    asyncio.run(main())
