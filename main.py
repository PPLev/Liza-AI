import asyncio
from core import Core


async def main():
    core = Core()
    await core.init_plugins()
    await core.on_input(input_str="без звука", for_filter="без звука")
    await core.start_loop()


if __name__ == '__main__':
    asyncio.run(main())
