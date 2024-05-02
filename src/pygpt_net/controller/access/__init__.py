#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.05.02 19:00:00                  #
# ================================================== #

from pygpt_net.core.dispatcher import BaseEvent
from pygpt_net.core.access.events import ControlEvent, AppEvent

from .control import Control
from .voice import Voice


class Access:
    def __init__(self, window=None):
        """
        Accessibility controller

        :param window: Window instance
        """
        self.window = window
        self.control = Control(window)
        self.voice = Voice(window)

    def setup(self):
        """Setup accessibility"""
        self.voice.setup()

    def reload(self):
        """Reload accessibility"""
        self.voice.setup()

    def update(self):
        """Update accessibility"""
        self.voice.update()

    def handle(self, event: BaseEvent):
        """
        Handle accessibility event

        :param event: event object
        """
        if isinstance(event, ControlEvent):
            self.control.handle(event)
            event.stop = True
        elif isinstance(event, AppEvent):
            self.handle_app(event)
            event.stop = True

    def handle_app(self, event: AppEvent):
        """
        Handle accessibility event (app)

        :param event: event object
        """
        self.window.core.debug.info("EVENT APP: " + event.name)
        if event.name == AppEvent.VOICE_CONTROL_TOGGLE:
            self.voice.toggle_recording()
        self.voice.play(event)  # handle audio events

    def on_escape(self):
        """Handle escape key"""
        if self.voice.is_recording:
            self.voice.stop_recording(timeout=True)
        if self.window.core.plugins.get("audio_input").handler_simple.is_recording:
            self.window.core.plugins.get("audio_input").handler_simple.stop_recording(timeout=True)