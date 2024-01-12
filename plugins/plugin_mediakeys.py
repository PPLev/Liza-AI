from core import Core


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

