import asyncio
import logging
import os
import time

import sounddevice
import torch

from core import Core
from utils.custom_filters import levenshtein_filter

logger = logging.getLogger("root")
core = Core()

silero_model = None
is_mute = False
model_settings = {}
output_device_id = None


async def start(core: Core):
    manifest = {
        "name": "Плагин генерации речи с помощью silero",
        "version": "1.1",
        "require_online": False,
        "is_active": True,

        "default_options": {
            "model_settings": {
                "model_path": "",
                "model_name": "silero.pt",
                "model_url": "https://models.silero.ai/models/tts/ru/v4_ru.pt"
            },
            "output_device_id": None
        },
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    global model_settings, output_device_id
    model_settings = manifest["options"]["model_settings"]
    output_device_id = manifest["options"]["output_device_id"]


async def _say_silero(core: Core, output_str):
    global silero_model, model_settings
    if is_mute:
        return
    if silero_model is None:  # Подгружаем модель если не подгрузили ранее
        logger.debug("Загрузка модели силеро")
        # Если нет файла модели - скачиваем
        if not os.path.isfile(model_settings["model_path"] + model_settings["model_name"]):
            logger.debug("Скачивание модели silero")
            torch.hub.download_url_to_file(
                model_settings["model_url"], model_settings["model_path"] + model_settings["model_name"]
            )

        silero_model = torch.package.PackageImporter(
            model_settings["model_path"] + model_settings["model_name"]
        ).load_pickle("tts_models", "model")
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

    if output_device_id:
        sounddevice.default.device = (None, output_device_id)

    sounddevice.play(audio, samplerate=24000)
    # TODO: Сделать блокировку распознавания при воспроизведении
    sounddevice.wait()


@core.on_output.register()
async def say_silero(core: Core = None, output_str=None):
    await _say_silero(core, output_str)


@core.on_input.register(levenshtein_filter("без звука", min_ratio=85))
async def say_all(core: Core = None, input_str=None):
    global is_mute
    is_mute = not is_mute
