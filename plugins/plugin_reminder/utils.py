import packages
from core import Core, F
import datetime
from .base import Notice

core = Core()


# @core.on_input.register(F.contains("напомни"))
# @core.on_input.register(F.contains("запомни"))
# @core.on_input.register(F.contains("запиши"))
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