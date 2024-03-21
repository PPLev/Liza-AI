import asyncio
import logging
import os
import time

import sounddevice
import torch

from core import Core

logger = logging.getLogger("root")
core = Core()

silero_model = None


async def start(core: Core):
    manifest = {
        "name": "Плагин генерации речи с помощью silero",
        "version": "1.0",
        "require_online": False,

        "default_options": {},
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    pass


async def _say_silero(core: Core, output_str):
    global silero_model
    if silero_model is None:  # Подгружаем модель если не подгрузили ранее
        logger.debug("Загрузка модели силеро")
        if not os.path.isfile("models/silero/v4_ru.pt"):  # Если нет файла модели - скачиваем
            logger.debug("Скачивание модели silero")
            torch.hub.download_url_to_file("https://models.silero.ai/models/tts/ru/v4_ru.pt", "models/silero/v4_ru.pt")

        silero_model = torch.package.PackageImporter("models/silero/v4_ru.pt").load_pickle("tts_models", "model")
        device = torch.device("cpu")
        silero_model.to(device)
        logger.debug("Загрузка модели силеро завершена")

    if not output_str:
        return

    say_str = output_str.replace("…", "...")

    logger.info(f"Генерация аудио для '{say_str}'")
    audio = silero_model.apply_tts(text=say_str,
                                   speaker="xenia",
                                   sample_rate=24000)

    sounddevice.default.device = (None, 30)
    sounddevice.play(audio, samplerate=24000)
    sounddevice.wait()
    # time.sleep((len(audio) / 24000) + 0.5)
    # sounddevice.stop()


# @core.on_output.register()
# async def say_silero(core: Core = None, output_str=None):
#     await _say_silero(core, output_str)


@core.on_input.register()
async def say_all(core: Core = None, input_str=None):
    if core and input_str:
        await _say_silero(core, input_str)
