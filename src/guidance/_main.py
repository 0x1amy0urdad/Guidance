from __future__ import annotations

import os
import sys
import time
import traceback
import wx

import bg3moddinglib as bg3

from ._guidance import (
    APP_NAME,
    INITIALIZED,
    config,
    logger,
    guidance,
)
from ._wxapp import MainWindow


def open_bg3_exe(w: MainWindow) -> str:
    with wx.FileDialog(w, 'Locate bg3.exe on your PC', wildcard = 'bg3.exe|bg3.exe', style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as d:
        if d.ShowModal() == wx.ID_CANCEL:
            return ""
        return d.GetPath()

def main() -> int:
    logger.info(f'{APP_NAME} is starting up')
    app = wx.App()
    try:
        if not INITIALIZED:
            choice = wx.MessageBox(
                'Cannot initialize Guidance due to missing .NET 8.0 runtime binaries.\n' \
                'Click \'OK\' to open the download page. Click \'Cancel\' to exit.',
                caption = APP_NAME,
                style = wx.OK | wx.CANCEL | wx.CENTRE | wx.ICON_EXCLAMATION)
            if choice == wx.OK:
                os.startfile('https://dotnet.microsoft.com/en-us/download/dotnet/8.0')
            return 0

        if bg3.is_path_length_limited():
            logger.info('MAX_PATH limit is detected')
            limit_disabled = False
            choice = wx.MessageBox(
                'Cannot initialize Guidance due to Windows path length limit (aka MAX_PATH).\n' \
                'Click \'OK\' to run a command to disable this limit.\n' \
                'WARNING. This requires Administrator privileges, so Windows will ask you to approve that!\n'
                'Click \'Cancel\' to exit.',
                caption = APP_NAME,
                style = wx.OK | wx.CANCEL | wx.CENTRE | wx.ICON_EXCLAMATION)
            if choice == wx.OK:
                bg3.enable_long_paths_with_prompt()
                time.sleep(2.0)
                if bg3.check_long_path_enabled_registry_setting():
                    limit_disabled = True
                    choice = wx.MessageBox(
                        'The limit was successfully removed. You may need to restart your computer for this to take effect.',
                        caption = APP_NAME,
                        style = wx.OK | wx.CENTRE | wx.ICON_EXCLAMATION)
            if not limit_disabled:
                choice = wx.MessageBox(
                    'The limit was not removed. Guidance cannot work with the MAX_PATH limit enabled.\n'
                    'You can follow official instructions and disable the limit manually, please read more there:\n',
                    'https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation',
                    caption = APP_NAME,
                    style = wx.OK | wx.CENTRE | wx.ICON_EXCLAMATION)
            return 0
        else:
            logger.info('MAX_PATH limit was not detected')

        cfg = config()
        w = MainWindow(app, cfg, title = APP_NAME)
        if not cfg.bg3_exe_path or not os.path.isfile(cfg.bg3_exe_path):
            bg3_bin_path = guidance.find_bg3_bin_path()
            if bg3_bin_path and os.path.isfile(bg3_bin_path):
                cfg.bg3_exe_path = bg3_bin_path
            else:
                cfg.bg3_exe_path = open_bg3_exe(w)
        if not cfg.bg3_appdata_path:
            bg3_appdata_path = guidance.find_bg3_appdata_path()
            if bg3_appdata_path:
                cfg.bg3_appdata_path = bg3_appdata_path
        cfg.save_config()
        w.start()
        logger.info(f'{APP_NAME} is entering the main loop')
        app.MainLoop()
        
    except:
        exc_str = traceback.format_exc()
        logger.fatal(exc_str)
        sys.stderr.write(exc_str)
        logger.info(f'{APP_NAME} has crashed')
        return 1
    logger.info(f'shutdown')
    return 0
