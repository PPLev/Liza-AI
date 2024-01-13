import inspect
import json
import os
import requests

from core import Core
import sys

core = Core()


async def start(core: Core):
    manifest = {
        "name": "Плагин GPT",
        "version": "1.0",
        "require_online": False,

        "default_options": {},
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    pass


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
                        if hasattr(obj, "__class__") and obj.__class__.__name__ == "function"
                    }
                }
            )
            for func in func_list[import_name].keys():
                func_list[import_name][func] = str(inspect.getfullargspec(func_list[import_name][func]).annotations)
    return func_list


#@core.on_input.register()
def ask_gpt(input_str: str):
    context_prompt = f"""{{char}} is (Lisa)
    Age 21
    Female
    Personality: Feels like a robot, but behaves more humanely. Works as {{user}}'s assistant and follows all his instructions. Does not like empty talk, but prefers commands or orders.
    Description: When {{user}} asks to do something, {{char}} always tries to do it as best as possible and talks about his failures, which are incredibly rare. When {{char}} answers, her answers to questions do not contain unnecessary information. Does not express emotion unless {{user}} asks for it."""
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


    url = "http://127.0.0.1:5000/v1/chat/completions"

    headers = {
        "Content-Type": "application/json"
    }

    # translate
    translated = requests.get(
        url="http://127.0.0.1:4990/translate",
        headers=headers,
        params={"text": prompt, "from_lang": "ru", "to_lang": "en"}
    )
    prompt = translated.json()["result"]

    data = {
        "mode": "chat",
        "messages": [
            {"role": "system", "content": context_prompt},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data, verify=False)
    assistant_message = response.json()['choices'][0]['message']['content']
    assistant_message = "{" + assistant_message.split("{")[1]
    assistant_message = assistant_message.split("}")[0] + "}"
    json_data = json.loads(assistant_message)

    module = json_data.pop("module")
    function = json_data.pop("function")

    mod = sys.modules[module]
    func = vars(mod).get(function)
    func(**json_data)

