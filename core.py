import asyncio

from magic_filter import MagicFilter
from termcolor import cprint, colored

from jaa import JaaCore

F = MagicFilter()
version = "0.0.1"


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
        self.input = EventObserver()

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
        await self.input.event(self, input_str=input_str, for_filter=input_str)
    #
    # async def run_output(self, output_str):
    #     await self.output.event(self, output_str)
    #
    # def setup_assistant_voice(self):
    #     # init playwav engine
    #     try:
    #         self.playwavs[self.playWavEngineId][0](self)
    #     except Exception as e:
    #         self.print_error("Ошибка инициализации плагина проигрывания WAV (playWavEngineId)", e)
    #         self.print_red('Попробуйте установить в options/core.json: "playWavEngineId": "sounddevice"')
    #         self.print_red('...временно переключаюсь на консольный вывод ответа...')
    #         self.ttsEngineId = "console"
    #
    #     # init tts engine
    #     try:
    #         self.ttss[self.ttsEngineId][0](self)
    #     except Exception as e:
    #         self.print_error("Ошибка инициализации плагина TTS (ttsEngineId)", e)
    #         cprint(
    #             'Попробуйте установить в options/core.json: "ttsEngineId": "console" для тестирования вывода через консоль',
    #             "red")
    #         cprint('Позднее, если все заработает, вы сможете настроить свой TTS-движок', "red")
    #
    #         from sys import platform
    #         if platform == "linux" or platform == "linux2":
    #             cprint(
    #                 "Подробнее об установке на Linux: https://github.com/janvarev/Irene-Voice-Assistant/blob/master/docs/INSTALL_LINUX.md",
    #                 "red")
    #         elif platform == "darwin":
    #             cprint(
    #                 "Подробнее об установке на Mac: https://github.com/janvarev/Irene-Voice-Assistant/blob/master/docs/INSTALL_MAC.md",
    #                 "red")
    #         elif platform == "win32":
    #             # cprint("Подробнее об установке на Linux: https://github.com/janvarev/Irene-Voice-Assistant/blob/master/docs/INSTALL_LINUX.md", "red")
    #             pass
    #
    #         self.print_red('...временно переключаюсь на консольный вывод ответа...')
    #         self.ttsEngineId = "console"
    #
    # def init_with_plugins(self):
    #     self.init_plugins(["core"])
    #     self.display_init_info()
    #
    #     self.setup_assistant_voice()
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


core = Core()


@core.input.register()
async def m2(core: Core = None, input_str=None):
    print("ok")


async def main():
    await core.run_input(input_str="пРивет")


if __name__ == '__main__':
    asyncio.run(main())
