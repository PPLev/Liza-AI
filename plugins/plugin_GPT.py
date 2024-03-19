import asyncio
import inspect
import json
import os
from typing import Coroutine

import requests

from core import Core, F
import sys

from utils.custom_filters import levenshtein_filter

core = Core()

gpt_url = ""
use_onerig_traslater = False
onerig_traslater_url = ""


async def start(core: Core):
    manifest = {
        "name": "Плагин GPT",
        "version": "1.1",
        "require_online": False,

        "default_options": {
            "gpt_url": "http://127.0.0.1:5000/v1/chat/completions",
            "use_onerig_traslater": False,
            "onerig_traslater_url": "http://127.0.0.1:4990/translate"
        },
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    global gpt_url, use_onerig_traslater, onerig_traslater_url

    gpt_url = manifest["options"]["gpt_url"]
    use_onerig_traslater = manifest["options"]["use_onerig_traslater"]
    onerig_traslater_url = manifest["options"]["onerig_traslater_url"]

    core.ask_gpt = ask_gpt
    core.translate = _translater


def get_plugin_funcs():
    func_list = {}
    for plugin_name in os.listdir("plugins"):
        if not __file__.endswith(plugin_name) and "__pycache__" not in plugin_name:
            import_name = f"plugins.{plugin_name.split('.py')[0]}"
            __import__(import_name)
            mod = sys.modules[import_name]
            func_list.update(
                {
                    import_name: {
                        name: obj for (name, obj) in vars(mod).items()
                        if
                        hasattr(obj, "__class__") and obj.__class__.__name__ == "function" and not name.startswith("_")
                    }
                }
            )
            for func in func_list[import_name].keys():
                func_list[import_name][func] = str(inspect.getfullargspec(func_list[import_name][func]).annotations)
    return func_list


async def _translater(text: str, from_lang: str, to_lang: str):
    global use_onerig_traslater, onerig_traslater_url
    if use_onerig_traslater:
        headers = {
            "Content-Type": "application/json"
        }
        # translate
        translated = requests.get(
            url=onerig_traslater_url,
            headers=headers,
            params={"text": text, "from_lang": from_lang, "to_lang": to_lang}
        )
        text = translated.json()["result"]

    return text


async def ask_gpt(prompt: str):
    global gpt_url
    context_prompt = f"""{{char}} is (Lisa)
    Age 21
    Female
    Personality: Feels like a robot, but behaves more humanely. Works as {{user}}'s assistant and follows all his instructions. Does not like empty talk, but prefers commands or orders.
    Description: When {{user}} asks to do something, {{char}} always tries to do it as best as possible and talks about his failures, which are incredibly rare. When {{char}} answers, her answers to questions do not contain unnecessary information. Does not express emotion unless {{user}} asks for it."""

    headers = {
        "Content-Type": "application/json"
    }

    prompt = await core.translate(text=prompt, from_lang="ru", to_lang="en")

    data = {
        "mode": "chat",
        "messages": [
            {"role": "system", "content": context_prompt},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(gpt_url, headers=headers, json=data, verify=False)
    assistant_message = response.json()['choices'][0]['message']['content']
    return assistant_message


@core.on_input.register()
async def _ask_gpt(core: Core, input_str: str):
    prompt = f"""
У меня есть список функций для разных модулей python:
{json.dumps(get_plugin_funcs(), indent=2)}
В списке указаны модули и их функции. Для каждой функции указаны их аргументы.
Тебе нужно определить какой модуль и какую функцию модуля следует использовать.
Нужно выполнить инструкцию: "{input_str}", с помощью модулей и их функций.
В ответ тебе нужно написать только строку в формате json.
Формат ответа должен соответствовать такому формату (пример "включи мультик"):
{{
    "module": "plugins.plugin_player",
    "function": "play_file",
    "file_path": "/mooves/cartoons",
    "file_name": "move.mp4"
}}
В начале идет название плагина, затем названия аргументов и их значения.
Все данные тебе нужно указать в зависимости от того, какая команда поступила от меня.
Важно: не пиши ничего кроме json в ответе. Строго только json и ничего кроме json.
"""

    assistant_message = await core.ask_gpt(prompt=prompt)

    assistant_message = "{" + assistant_message.split("{")[1]
    assistant_message = assistant_message.split("}")[0] + "}"
    json_data = json.loads(assistant_message)

    module = json_data.pop("module")
    function = json_data.pop("function")

    mod = sys.modules[module]
    func = vars(mod).get(function)
    if asyncio.iscoroutinefunction(func):
        await func(**json_data)
    else:
        func(**json_data)
