import asyncio

import packages
from core import Core, F
import datetime
from .base import Notice

core = Core()


@core.on_input.register(F.func(lambda t: any([i in t for i in ["напомни", "запомни", "запиши"]])))
async def new_notice(package: packages.TextPackage):
    now = datetime.datetime.now()
    prompt = f"""
Сформируй json из следующего запроса: "{package.input_text}"
Тебе необходимо указать следующие поля:
value - значение
day_before - сколько дней осталось
time - время в которое нужно сделать действие

Пример: "Напомни мне послезавтра про то что мне нужно забрать заказ из интернет магазина после работы"
Ответ:
{{
"value": "забрать заказ из магазина"
"day_before": "2"
"time": "18:45"
}}
В ответе можно указывать только json!
    """

    answer = await core.gpt.ask(prompt)
    json_data = core.gpt.find_json(answer)
    if json_data:
        print(json_data)
        date = datetime.date(now.year, now.month, now.day) + datetime.timedelta(days=int(json_data["day_before"]))
        tz = datetime.timezone(datetime.timedelta(hours=3), name='МСК')
        time = datetime.time(int(json_data["time"].split(":")[0]), int(json_data["time"].split(":")[1]), tzinfo=tz)
        time_data = datetime.datetime.combine(date, time)

        notice = Notice.create(
            value=json_data["value"],
            remind_date=time_data
        )
        package.text = f"Создана заметка с айди {notice.id}"

        await package.run_hook()


class Reminder:
    def __init__(self, core: Core, loop_timer: int = None, observer_name: str = None):
        self.core = core
        self.loop_timer = loop_timer or 60 * 30
        self.observer_name = observer_name or "on_input"
        self._is_loop_run = False

    async def loop(self):
        self._is_loop_run = True
        while True:
            if not self._is_loop_run:
                return

            # TODO: Делаем опрос бд и шлем ивенты

            await asyncio.sleep(self.loop_timer)

    async def start_loop(self):
        if not self._is_loop_run:
            asyncio.run_coroutine_threadsafe(coro=self.loop(), loop=asyncio.get_event_loop())

    async def stop_loop(self):
        self._is_loop_run = False
