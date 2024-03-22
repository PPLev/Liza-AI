import asyncio
import json
import os
import sys

import vosk

from core import Core
import pyaudio
import logging

logger = logging.getLogger("root")

core = Core()


async def run_vosk():
    """
    Распознование библиотекой воск
    """
    import sounddevice
    #:TODO настройка устройства вывода потом переписать
    # sounddevice.default.device = (1, None)
    # dev_out = sounddevice.query_devices(kind="input")
    # print(dev_out)
    # print(sounddevice.check_output_settings())

    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16,
                     channels=1,
                     rate=44100,
                     input=True,
                     frames_per_buffer=8000)


    if not os.path.isdir("models/vosk/"):
        logger.warning("Папка модели воск не найдена\n"
                       "Please download a model for your language from https://alphacephei.com/vosk/models")
        sys.exit(0)

    model = vosk.Model("models/vosk/vosk-model-small-ru-0.22")  # Подгружаем модель
    rec = vosk.KaldiRecognizer(model, 44100)

    logger.info("Запуск распознователя речи vosk вход в цикл")

    while True:
        await asyncio.sleep(0)

        data = stream.read(8000)
        if rec.AcceptWaveform(data):
            recognized_data = rec.Result()
            recognized_data = json.loads(recognized_data)
            voice_input_str = recognized_data["text"]
            if voice_input_str != "" and voice_input_str is not None:
                logger.info(f"Распознано Vosk: '{voice_input_str}'")
                await core.run_input(input_str=voice_input_str)


async def start(core: Core):
    manifest = {
        "name": "Плагин распознования речи с помощью воск",
        "version": "1.0",
        "require_online": False,

        "default_options": {},
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    asyncio.run_coroutine_threadsafe(run_vosk(), asyncio.get_running_loop())
