import asyncio

import packages
from core import Core


async def main():
    core = Core()
    await core.init_plugins()
    await core.on_input(
        package=packages.TextPackage(
            input_text="запомни через пять дней в семнадцать тридцать три мне надо созвониться",
            core=core,
            hook=packages.NULL_HOOK
        )
    )
    await core.start_loop()


if __name__ == '__main__':
    asyncio.run(main())
