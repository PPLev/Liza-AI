import logging
import os

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


@core.on_output.register()
async def _say_silero(core: Core, output_str):
    global silero_model
    if silero_model is None:  # Подгружаем модель если не подгрузили ранее
        logger.debug("Загрузка модели силеро")
        if not os.path.isfile("silero.pt"):  # Если нет файла модели - скачиваем
            logger.debug("Скачивание модели silero")
            torch.hub.download_url_to_file("https://models.silero.ai/models/tts/ru/v4_ru.pt", "silero.pt")

        silero_model = torch.package.PackageImporter("silero.pt").load_pickle("tts_models", "model")
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

    sounddevice.play(audio, samplerate=24000)
