from __future__ import annotations

import os
import sys
import traceback
import wx


from ._guidance import (
    APP_NAME,
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
