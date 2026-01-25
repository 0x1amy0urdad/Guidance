from __future__ import annotations

import bg3moddinglib as bg3

import json
import os

from dataclasses import dataclass
from typing import Callable, cast

from ._logger import logger


VERSION = (0, 2, 0, 1)
DEFAULT_MOD_NAME = 'CompatibilityPatch'
DEFAULT_MOD_UUID = '66553d67-3639-4530-babb-4535f3d61f04'

APP_NAME = f'Guidance {VERSION[0]}.{VERSION[1]}.{VERSION[2]}.{VERSION[3]}'
INITIALIZED = bg3.DOTNET_INITIALIZED

class config:
    __env_root_path: str = ""
    __bg3_exe_path: str = ""
    __bg3_appdata_path: str = ""
    __window_width: int = 1024
    __window_height: int = 768

    def __init__(self) -> None:
        self.__bg3_exe_path = ""
        local_appdata_path = os.getenv('LOCALAPPDATA')
        if local_appdata_path:
            self.__env_root_path = os.path.join(local_appdata_path, 'guidance')
        else:
            logger.warning(f'LOCALAPPDATA is not defined, will fall back to the current directory')
            self.__env_root_path = os.path.abspath(os.curdir)
        logger.info(f'Config file path: {self.config_file_path}')
        if self.config_exists:
            self.load_config()

    @property
    def env_root_path(self) -> str:
        return self.__env_root_path

    @property
    def bg3_exe_path(self) -> str:
        return self.__bg3_exe_path

    @bg3_exe_path.setter
    def bg3_exe_path(self, val: str) -> None:
        self.__bg3_exe_path = val

    @property
    def bg3_appdata_path(self) -> str:
        return self.__bg3_appdata_path

    @bg3_appdata_path.setter
    def bg3_appdata_path(self, val: str) -> None:
        self.__bg3_appdata_path = val

    @property
    def window_width(self) -> int:
        return self.__window_width

    @window_width.setter
    def window_width(self, val: int) -> None:
        self.__window_width = val

    @property
    def window_height(self) -> int:
        return self.__window_height

    @window_height.setter
    def window_height(self, val: int) -> None:
        self.__window_height = val

    @property
    def config_file_path(self) -> str:
        return os.path.join(self.__env_root_path, 'guidance.json')

    @property
    def config_exists(self) -> bool:
        return self.config_file_path != "" and os.path.isfile(self.config_file_path)

    def load_config(self) -> None:
        with open(self.config_file_path, 'rt') as f:
            logger.info(f'Loading configuration from {self.config_file_path}')
            cfg = cast(dict, json.load(f))
            if 'bg3_exe_path' in cfg:
                self.__bg3_exe_path = cast(str, cfg['bg3_exe_path'])
                logger.info(f'Configuration: bg3_exe_path = {self.__bg3_exe_path}')
            if 'bg3_appdata_path' in cfg:
                self.__bg3_appdata_path = cast(str, cfg['bg3_appdata_path'])
                logger.info(f'Configuration: bg3_appdata_path = {self.__bg3_appdata_path}')
            if 'window_width' in cfg:
                self.__window_width = int(cfg['window_width'])
                logger.info(f'Configuration: window_width = {self.__window_width}')
            if 'window_height' in cfg:
                self.__window_height = int(cfg['window_height'])
                logger.info(f'Configuration: window_height = {self.__window_height}')

    def save_config(self) -> None:
        os.makedirs(os.path.dirname(self.config_file_path), exist_ok = True)
        with open(self.config_file_path, 'wt') as f:
            cfg = dict()
            if self.__bg3_exe_path:
                cfg['bg3_exe_path'] = self.__bg3_exe_path
            if self.__bg3_appdata_path:
                cfg['bg3_appdata_path'] = self.__bg3_appdata_path
            cfg['window_width'] = self.__window_width
            cfg['window_height'] = self.__window_height
            f.write(json.dumps(cfg))
            logger.info(f'Saved configuration to {self.config_file_path}')


class guidance:
    __cfg: config
    __env: bg3.bg3_modding_env
    __tool: bg3.bg3_modding_tool
    __files: bg3.game_files
    __assets: bg3.bg3_assets
    __index: bg3.dialog_index
    __mod_mgr: bg3.mod_manager

    def __init__(self, cfg: config, progress_callback: Callable[[int, int, str], None] | None = None) -> None:
        self.__cfg = cfg
        self.__env = guidance.create_env(cfg)
        self.__tool = bg3.bg3_modding_tool(self.__env)
        self.__files = bg3.game_files(self.__tool, DEFAULT_MOD_NAME, DEFAULT_MOD_UUID)
        self.__assets = bg3.bg3_assets(self.__files)
        self.__index = self.__assets.index
        self.__mod_mgr = bg3.mod_manager(self.__files, cfg.bg3_appdata_path)

    @property
    def env(self) -> bg3.bg3_modding_env:
        return self.__env

    @property
    def tool(self) -> bg3.bg3_modding_tool:
        return self.__tool

    @property
    def files(self) -> bg3.game_files:
        return self.__files

    @property
    def assets(self) -> bg3.bg3_assets:
        return self.__assets

    @property
    def index(self) -> bg3.dialog_index:
        return self.__index

    @property
    def mod_manager(self) -> bg3.mod_manager:
        return self.__mod_mgr

    @staticmethod
    def find_bg3_bin_path() -> str | None:
        for env_var_name in ('ProgramFiles(x86)', 'ProgramW6432', 'ProgramFiles'):
            program_files_path = os.getenv(env_var_name)
            if program_files_path:
                logger.info(f'Program Files path = {program_files_path}')
                bg3_path = os.path.join(program_files_path, 'Steam', 'steamapps', 'common', 'Baldurs Gate 3', 'bin', 'bg3.exe')
                logger.info(f'Looking for BG3 at {bg3_path}')
                if os.path.isfile(bg3_path):
                    logger.info(f'Successfully found BG3 at {bg3_path}')
                    return bg3_path
        drives = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for drive in drives:
            steam_library_path = f'{drive}:\\SteamLibrary'
            if os.path.exists(steam_library_path):
                bg3_path = os.path.join(steam_library_path, 'steamapps', 'common', 'Baldurs Gate 3', 'bin', 'bg3.exe')
                logger.info(f'Looking for BG3 at {bg3_path}')
                if os.path.isfile(bg3_path):
                    logger.info(f'Successfully found BG3 at {bg3_path}')
                    return bg3_path
        logger.warning('Failed to locate BG3 location')
        return None

    @staticmethod
    def find_bg3_appdata_path() -> str | None:
        local_appdata_path = os.getenv('LOCALAPPDATA')
        if local_appdata_path:
            bg3_appdata_path = os.path.join(local_appdata_path, 'Larian Studios', "Baldur's Gate 3")
            if os.path.isdir(bg3_appdata_path):
                logger.info(f'Successfully found BG3 app data at {bg3_appdata_path}')
                return bg3_appdata_path
        logger.warning('Failed to locate BG3 app data')
        return None

    @staticmethod
    def create_env(cfg: config) -> bg3.bg3_modding_env:
        env_path = cfg.env_root_path
        if not os.path.exists(env_path):
            os.makedirs(env_path)
        logger.info(f'Successfully created a new environment at {cfg.env_root_path}')
        bg3_data_path = os.path.join(os.path.dirname(os.path.dirname(cfg.bg3_exe_path)), 'Data')
        logger.info(f'BG3 data path: {bg3_data_path}')
        return bg3.bg3_modding_env(env_path, bg3_data_path = bg3_data_path, skip_config = True)
