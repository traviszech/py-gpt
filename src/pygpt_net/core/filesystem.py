#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.20 08:00:00                  #
# ================================================== #

import os
import shutil
from pathlib import PurePath

from PySide6.QtCore import QUrl


class Filesystem:
    def __init__(self, window=None):
        """
        Filesystem core

        :param window: Window instance
        """
        self.window = window
        self.workdir_placeholder = '%workdir%'
        self.styles = [
            'style.css',
            'style.dark.css',
            'style.light.css',
            'markdown.css',
            'markdown.dark.css',
            'markdown.light.css',
        ]

    def install(self):
        """Install provider data"""
        # output data directory
        data_dir = self.window.core.config.get_user_dir('data')
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)

        # install custom css styles for override default styles
        css_dir = os.path.join(self.window.core.config.path, 'css')
        if not os.path.exists(css_dir):
            os.mkdir(css_dir)

        src_dir = os.path.join(self.window.core.config.get_app_path(), 'data', 'css')
        dst_dir = os.path.join(self.window.core.config.path, 'css')

        try:
            for style in self.styles:
                src = os.path.join(src_dir, style)
                dst = os.path.join(dst_dir, style)
                if not os.path.exists(dst) and os.path.exists(src):
                    shutil.copyfile(src, dst)
        except Exception as e:
            print("Error while installing css files: ", e)

    def make_local(self, path: str) -> str:
        """
        Make local placeholder path

        :param path: path to prepare
        :return: local path with working dir placeholder
        """
        return path.replace(self.window.core.config.get_user_path(), self.workdir_placeholder)

    def make_local_list(self, paths: list) -> list:
        """
        Make local placeholder paths

        :param paths: list with paths to prepare
        :return: local paths with working dir placeholder
        """
        return [self.make_local(path) for path in paths]

    def get_url(self, url) -> QUrl:
        """
        Make current OS-specific URL to open file or directory

        :param url: URL to prepare
        :return: URL to open file or directory
        """
        if self.window.core.platforms.is_windows():
            if not url.startswith('file:///'):
                url = 'file:///' + url
            return QUrl(url, QUrl.TolerantMode)
        else:
            return QUrl.fromLocalFile(url)

    def get_path(self, path) -> str:
        """
        Prepare current OS-specific path from given path

        :param path: path to prepare
        :return: prepared OS-specific path
        """
        parts = PurePath(path).parts
        return os.path.join(*parts)  # rebuild OS directory separators

    def to_workdir(self, path) -> str:
        """
        Replace user path with current workdir

        :param path: path to fix
        :return: path with replaced user workdir
        """
        path = self.get_path(path)
        work_dir = self.window.core.config.get_user_path()  # current OS app workdir

        # try to find %workdir% placeholder in path
        if self.workdir_placeholder in path:
            return path.replace(self.workdir_placeholder, work_dir)

        # try to find workdir in path: old versions compatibility, < 2.0.113
        if work_dir.endswith('.config/pygpt-net'):
            work_dir = work_dir.rsplit('/.config/pygpt-net', 1)[0]
        elif work_dir.endswith('.config\\pygpt-net'):
            work_dir = work_dir.rsplit('\\.config\\pygpt-net', 1)[0]

        if self.window.core.platforms.is_windows():
            dir_index = path.find('\\.config\\pygpt-net\\') + 1
        else:
            dir_index = path.find('/.config/pygpt-net/') + 1

        parts = path[dir_index:]
        return os.path.join(work_dir, parts)

    def extract_local_url(self, path) -> (str, str):
        """
        Extract local url and path from url

        :param path: local path or url
        :return: url, path
        """
        if not path.startswith('http://') \
                and not path.startswith('https://'):
            path = self.to_workdir(path)

        prefix = ''
        if not path.startswith('file://') \
                and not path.startswith('http://') \
                and not path.startswith('https://'):
            if self.window.core.platforms.is_windows():
                prefix = 'file:///'
            else:
                prefix = 'file://'

        url = prefix + path
        return url, path

