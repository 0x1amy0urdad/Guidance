from __future__ import annotations

import wx

class PleaseWait(wx.Frame):
    __progress_label: wx.StaticText | None
    __progress: wx.Gauge | None
    __panel: wx.Panel
    __sizer : wx.BoxSizer
    __status_label : wx.StaticText

    def __init__(self, parent: wx.Frame, message: str, show_progress : bool = False):
        super().__init__(
            parent,
            style = wx.CAPTION,
            title = message,
            size = wx.Size(160, 480)
        )
        
        # Main panel
        self.__panel = wx.Panel(self)
        #self.__panel.SetBackgroundColour(wx.Colour(40, 40, 40))
        
        
        # Label for status text
        self.__status_label = wx.StaticText(self.__panel, label = message)
        #self.__status_label.SetForegroundColour(wx.WHITE)
        font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.__status_label.SetFont(font)
        
        # Progress bar (optional)
        if show_progress:
            self.__progress_label = wx.StaticText(self.__panel, label = 'progress label')
            #self.__progress_label.SetForegroundColour(wx.WHITE)
            self.__progress = wx.Gauge(self.__panel, range = 100)
            self.__progress.SetValue(45)
        else:
            self.__progress = None
            self.__progress_label = None

        # Layout
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        inner_sizer = wx.BoxSizer(wx.VERTICAL)
        inner_sizer.Add(self.__status_label, 1, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 200)
        self.__sizer.Add(inner_sizer, 1, wx.TOP | wx.BOTTOM, 30)
        #self.__sizer.Add(self.__status_label, 1, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 200)
        if self.__progress is not None and self.__progress_label is not None:
            self.__sizer.Add(self.__progress_label, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)
            self.__sizer.Add(self.__progress, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        self.__panel.SetSizer(self.__sizer)
        self.__sizer.Fit(self)

    def show(self) -> None:
        self.CentreOnParent()
        self.Show()
        
    def hide(self) -> None:
        self.Hide()
    
    def update_status(self, message: str | None = None, progress: int | None = None) -> None:
        wx.CallAfter(self.__update_status, message, progress)

    def __update_status(self, message: str | None = None, progress: int | None = None):
        if self.__progress_label is not None and message is not None:
            self.__progress_label.SetLabel(message)
        if self.__progress is not None and progress is not None:
            self.__progress.SetValue(progress)
        wx.SafeYield()

