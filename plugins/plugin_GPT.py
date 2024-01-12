import inspect
import os

from core import Core
import sys

core = Core()


async def start(core: Core):
    manifest = {
        "name": "Плагин GPT",
        "version": "1.0",
        "require_online": False,

        "default_options": {},
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    pass


def get_plugin_funcs():
    func_list = {}
    for plugin_name in os.listdir("."):
        if not __file__.endswith(plugin_name):
            import_name = f"plugins.{plugin_name.split('.py')[0]}"
            __import__(import_name)
            mod = sys.modules[import_name]
            func_list.update(
                {
                    import_name: {
                        name: obj for (name, obj) in vars(mod).items()
                        if hasattr(obj, "__class__") and obj.__class__.__name__ == "function"
                    }
                }
            )
            for func in func_list[import_name].keys():
                func_list[import_name][func] = inspect.getfullargspec(func_list[import_name][func]).annotations
    return func_list


@core.on_input.register()
async def ask_gpt(core: Core, input_str: str):
    pass
