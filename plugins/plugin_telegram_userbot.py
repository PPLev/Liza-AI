import asyncio
import json

from pyrogram import Client

from core import Core

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
                "name": "bot1234",
                "api_id": "12345678",
                "api_hash": "abcd123510b3412349d123a871237b10"
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
        name=manifest["options"]["client"]["name"],
        api_id=manifest["options"]["client"]["api_id"],
        api_hash=manifest["options"]["client"]["api_hash"],
    )
    users = manifest["options"]["users"]

    # TODO: fix client start
    # await client.run()  # Not work(


async def _send_message(user: str, message: str):
    global client
    message = await core.translate(text=message, from_lang="en", to_lang="ru")
    async with client:
        await client.send_message(chat_id=user, text=message)


async def send_message_from_prompt(prompt: str):
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

    answer = await core.ask_gpt(self_prompt)
    answer = "{" + answer.split("{")[1]
    answer = answer.split("}")[0] + "}"
    json_data = json.loads(answer)

    await _send_message(user=json_data["username"], message=json_data["message"])
