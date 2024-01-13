from core import Core
import keyboard


async def start(core: Core):
    manifest = {
        "name": "Плагин медиаклавишь",
        "version": "1.0",
        "require_online": False,

        "default_options": {},
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    pass


def press_key(key_name: str):
    keyboard.press_and_release(key_name)
