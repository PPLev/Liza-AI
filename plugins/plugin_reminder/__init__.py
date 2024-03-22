from core import Core, F

core = Core()


async def start(core: Core):
    manifest = {
        "name": "Плагин заметок",
        "version": "1.0",
        "require_online": False,

        "default_options": {},
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    print("reminder!!!!!!!!!!!!!!!!!!!!!!")

@core.on_input.register(F == "привет")
async def test(core, input_str):
    print("Работаем)")
    await core.run_output("ура")