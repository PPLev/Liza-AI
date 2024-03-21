import asyncio
import json

from pyrogram import Client
from pyrogram import compose as _compose

from core import Core, version

core = Core()

client: Client

users = {}


async def start(core: Core):
    manifest = {
        "name": "Плагин юзербота телеграм",
        "version": "1.1",
        "require_online": True,

        "default_options": {
            "client": {  # to get this data - use this link: https://my.telegram.org/auth
                "api_id": "3648362",
                "api_hash": "cacd564510b3498349d867a878557b19"
            },
            "users": {  # username: aliases
                "farirus": ["Петька", "петр", "петя"]
            }
        },
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    global client, users

    client = Client(
        name="tg_user",
        api_id=manifest["options"]["client"]["api_id"],
        api_hash=manifest["options"]["client"]["api_hash"],
        app_version=version,
        device_model="Liza-AI",
        system_version="Assistant"
    )
    users = manifest["options"]["users"]

    async def start_client():
        await _compose([client])

    # TODO: Сделать блокировку при первом входе для ввода данных телеграм
    asyncio.run_coroutine_threadsafe(start_client(), asyncio.get_event_loop())


def _client_wrapper(func: callable):
    async def wrapper(*args, **kwargs):
        await client.start()
        await func(*args, **kwargs)
        await client.stop()

    return wrapper


#@_client_wrapper
async def _send_message(user: str, message: str):
    async with client:
        await client.send_message(chat_id=user, text=message)


async def send_prompt_message(prompt: str):
    self_prompt = f"""
У меня есть список пользователей с которыми я веду диалог:
{json.dumps(users, indent=2)}
В этом списке содержиться юзернейм и список имен по которым я обращаюсь к этим пользователям.
Я хочу чтобы ты сделала это: {prompt}.
Тебе нужно определить какому пользователю нужно отправить сообщение.
Также нужно передать сообщение которое я хочу отправить этому пользователю.
В ответ надо прислать json с указанием юзернейма и текста сообщения которое ему предназначалось.
пример для "спроси у жени как у него дела":
{{
    "username": "EvgenY123",
    "message": "как твои дела?"
}}
Важно: не пиши ничего кроме json в ответе. Строго только json и ничего кроме json."""

    answer = await core.gpt.ask(self_prompt)
    answer = "{" + answer.split("{")[1]
    answer = answer.split("}")[0] + "}"
    json_data = json.loads(answer)

    await _send_message(user=json_data["username"], message=json_data["message"])
