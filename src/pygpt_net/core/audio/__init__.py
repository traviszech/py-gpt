#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.12.08 00:00:00                  #
# ================================================== #

import re

from pygpt_net.provider.audio_input.base import BaseProvider as InputBaseProvider
from pygpt_net.provider.audio_output.base import BaseProvider as OutputBaseProvider


class Audio:
    def __init__(self, window=None):
        """
        Audio input/output core

        :param window: Window instance
        """
        self.window = window
        self.providers = {
            "input": {},
            "output": {},
        }

    def get_input_devices(self) -> list:
        """
        Get input devices

        :return devices list: [(id, name)]
        """
        import pyaudio
        devices = []
        try:
            p = pyaudio.PyAudio()
            num_devices = p.get_device_count()
            for i in range(num_devices):
                info = p.get_device_info_by_index(i)
                if info["maxInputChannels"] > 0:
                    devices.append((i, info["name"]))
                    # print(f"Device ID {i}: {info['name']}")
            p.terminate()
        except Exception as e:
            print(f"Audio input devices receive error: {e}")
        return devices

    def is_device_compatible(self, device_index) -> bool:
        """
        Check if device is compatible

        :param device_index: device index
        :return: True if compatible
        """
        import pyaudio
        p = pyaudio.PyAudio()
        info = p.get_device_info_by_index(device_index)
        supported = False
        try:
            p.is_format_supported(
                rate=44100,
                input_device=info['index'],
                input_channels=1,
                input_format=pyaudio.paInt16)
            supported = True
        except ValueError:
            supported = False
        p.terminate()
        return supported

    def is_registered(self, id: str, type: str = "output") -> bool:
        """
        Check if provider is registered

        :param id: provider id
        :param type: provider type
        :return: True if registered
        """
        if type in self.providers:
            return id in self.providers[type]
        return False

    def get_providers(self, type: str = "output") -> dict:
        """
        Get all providers

        :param type: provider type
        :return: providers dict
        """
        if type in self.providers:
            return self.providers[type]
        return {}

    def get_ids(self, type: str = "output") -> list:
        """
        Get all providers ids

        :param type: provider type
        :return: providers ids list
        """
        if type in self.providers:
            return list(self.providers[type].keys())
        return []

    def get(self, id: str, type: str = "output") -> InputBaseProvider or OutputBaseProvider:
        """
        Get provider instance

        :param id: provider id
        :param type: provider type
        :return: provider instance
        """
        if self.is_registered(id, type):
            return self.providers[type][id]
        return None

    def register(self, provider: InputBaseProvider or OutputBaseProvider, type: str = "output"):
        """
        Register provider

        :param provider: provider instance
        :param type: provider type
        """
        id = provider.id
        self.providers[type][id] = provider

    def clean_text(self, text: str) -> str:
        """
        Clean text before send to audio synthesis

        :param text: text
        :return: cleaned text
        """
        return re.sub(r'~###~.*?~###~', '', str(text))
