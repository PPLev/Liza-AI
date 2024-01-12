import hashlib
import os
import sys
import threading
import time

from core import Core

modname = os.path.basename(__file__)[:-3]
core = Core()



def start(core: Core):
    manifest = {
        "name": "Плагин перезагрузки плагинов",
        "version": "1.0",
        "require_online": False,

        "default_options": {
            "reload_on_edit": False,
            "no_reload": ["plugin_reload", "plugin_timer", "core", "__pycache__"]
        },
        "commands": {
            "полная перезагрузка": full_reload,
            "перезагрузка всех плагинов": (reloader, "all"),
            "перезагрузи плагин даты": (reloader, "datetime"),
            "новый плагин": add_new_plugin,
            "выключение|выключись": lambda *_: sys.exit("Выключение через плагин")
        }
    }

    return manifest


def start_with_options(core: VACore, manifest: dict):
    core.no_reload = manifest["default_options"]["no_reload"]
    core.reload_list, _ = get_reload_files(core.no_reload)
    if manifest["default_options"]["reload_on_edit"]:  # если reload_on_edit то запускаем поток слежения
        thread = threading.Thread(target=auto_reinit, args=(core.no_reload,))
        thread.start()

@core.on_input
def get_reload_files(no_reload: list):  # возвращает список файлов из папок с плагинами и настройками
    files_plugins = filter(lambda file: file.split(".")[0] not in no_reload, os.listdir("plugins/"))
    files_plugins = list([f"plugins/{file}" for file in files_plugins])
    files_options = filter(lambda file: file.split(".")[0] not in no_reload, os.listdir("options/"))
    files_options = list([f"options/{file}" for file in files_options])
    return files_plugins, files_options


def full_reload(core: VACore = None, phrase: str = None, command: str = None):  # полный перезапуск
    if core is not None:
        core.say("Начинаю полную перезагрузку")
    else:
        print("Начинаю полную перезагрузку")
    os.execv(sys.executable, [sys.executable] + sys.argv)


def reloader(core: VACore, phrase: str = None, command: str = None):
    if command == "all":  # перезагружает все плагины
        for plugin in core.reload_list:
            reloader(core, command=plugin[8:-3])

        core.say("Все плагины перезагружены")

    else:  # перезагружает конкретный плагин
        if command in core.reload_list:
            try:
                del sys.modules["plugins."+command]
            except Exception as err:
                print(f"Не удалось деимпортровать плагин {command}: {err}")
        core.init_plugin(command)


def add_new_plugin(core: VACore = None, phrase: str = None, command: str = None):
    # импортирует новые плагины из папки plugins если они не импортированы ранее
    plugins, _ = get_reload_files(core.no_reload)
    new_plugins = list([plugin for plugin in plugins if plugin not in core.reload_list])
    if len(new_plugins):
        for new_plugin in new_plugins:
            reloader(core, command=new_plugin[8:-3])
            core.reload_list.append(new_plugin)
    else:
        core.say("Новые плагины не найдены")


def file_as_bytes(file):
    with file:
        return file.read()


def auto_reinit(no_reload: list):
    #  Функция следит за хэшами файлов и в случае их изменения/удаления - запускает полный перезапуск

    plugins, options = get_reload_files(no_reload)
    files = plugins + options
    files_hashes = {}

    for fname in files:  # собираем хэши во время запуска один раз
        files_hashes[fname] = hashlib.md5(file_as_bytes(open(fname, 'rb'))).hexdigest()

    while True:
        for fname in files:
            if not os.path.isfile(fname):  # если удален
                full_reload()
            if files_hashes[fname] != hashlib.md5(file_as_bytes(open(fname, 'rb'))).hexdigest():  # если изменен
                full_reload()

        time.sleep(3)  # задержка между сканированиями
