from core import Core, F
from plugins.plugin_reminder import Notice

core = Core()

@core.on_input.register(F.startswith("напомни"))
async def ff():
    core.gpt.ask

    Notice.create()