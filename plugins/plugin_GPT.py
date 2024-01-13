import inspect
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
        if not __file__.endswith(plugin_name):
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
                func_list[import_name][func] = inspect.getfullargspec(func_list[import_name][func]).annotations
    return func_list


#@core.on_input.register()
def ask_gpt(input_str: str):
    context_prompt = f"""{{char}} is (Lisa)
    Age 21
    Female
    Personality: Feels like a robot, but behaves more humanely. Works as {{user}}'s assistant and follows all his instructions. Does not like empty talk, but prefers commands or orders.
    Description: When {{user}} asks to do something, {{char}} always tries to do it as best as possible and talks about his failures, which are incredibly rare. Answers to questions are very brief and strictly to the point. Does not express emotions until {{user}} asks for it."
"""
    prompt = f"""
У меня есть список функций для разных модулей python:
{get_plugin_funcs()}
В списке указаны модули и их функции. Для каждой функции указаны их аргументы.
Тебе нужно определить какой модуль и какую функцию модуля следует использовать.
Нужно выполнить команду "{input_str}"
В ответ тебе нужно написать только строку в формате json.
Формат ответа должен соответствовать такому формату (пример):
{{
    "module": "plugins.plugin_player",
    "function": "play_file",
    "file_path": "/mooves/cartoons",
    "file_name": "move.mp4"
}}
В начале идет название плагина, затем названия аргументов и их значения.
Не пиши ничего кроме json в ответе. Строго только json и ничего кроме json.
"""


    url = "http://127.0.0.1:5000/v1/chat/completions"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "mode": "chat",
        "messages": [
            {"role": "system", "content": context_prompt},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data, verify=False)
    assistant_message = response.json()['choices'][0]['message']['content']
    print(assistant_message)

