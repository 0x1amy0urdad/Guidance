from __future__ import annotations

import os
import os.path
import sys
import wx

# import wx.adv


# class SplashScreen:
#     __splash_screen: wx.adv.SplashScreen | None

#     def __init__(self) -> None:
#         self.__splash_screen = None

#     def show_splash_screen(self) -> None:
#         try:
#             image_path = os.path.join(getattr(sys, '_MEIPASS'), 'guidance.png')
#         except:
#             image_path = os.path.join(os.getcwd(), 'src', 'guidance', 'guidance.png')
#         splash_png = wx.Bitmap(image_path, wx.BITMAP_TYPE_PNG)
#         self.__splash_screen = wx.adv.SplashScreen(
#             splash_png,
#             wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_NO_TIMEOUT,
#             0,
#             None)
#         self.__splash_screen.Show()


#     def hide_splash_screen(self) -> None:
#         if self.__splash_screen is not None:
#             self.__splash_screen.Destroy()


class SplashScreen:
    __splash_screen: wx.Frame
    __static_bitmap: wx.StaticBitmap
    __original_bitmap: wx.Bitmap
    __visible: bool

    def __init__(self) -> None:
        try:
            image_path = os.path.join(getattr(sys, '_MEIPASS'), 'guidance.png')
        except:
            image_path = os.path.join(os.getcwd(), 'src', 'guidance', 'guidance.png')
        
        self.__original_bitmap = wx.Bitmap(image_path, wx.BITMAP_TYPE_PNG)
        
        #self.__splash_screen = wx.Frame(None, style = wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_STATIC)
        self.__splash_screen = wx.Frame(None, style = wx.BORDER_STATIC)
        self.__static_bitmap = wx.StaticBitmap(self.__splash_screen, bitmap = wx.BitmapBundle.FromBitmap(self.__original_bitmap))
        self.__visible = False

    @property
    def visible(self) -> bool:
        return self.__visible

    def show_splash_screen(self) -> None:
        self.__splash_screen.SetDoubleBuffered(True)
        self.__splash_screen.Fit()
        self.__splash_screen.Centre()
        self.__splash_screen.Show()
        
        self.update_status("Loading...")
        self.__visible = True

    def update_status(self, message: str) -> None:
        wx.CallAfter(self.__update_status, message)

    def __update_status(self, message: str) -> None:
        self.__splash_screen.Freeze()
        try:
            bitmap = self.__original_bitmap.ConvertToImage().ConvertToBitmap()
            dc = wx.MemoryDC(bitmap)
            dc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT))
            dc.SetTextForeground(wx.WHITE)
            dc.SetTextBackground(wx.BLACK)

            while True:        
                text_width, text_height = dc.GetTextExtent(message)
                if text_width > 540:
                    n = len(message) - 6
                    message = message[:n] + '...'
                else:
                    break
            x = 15
            y = int(bitmap.GetHeight() - text_height - 10)
            
            dc.DrawText(message, x, y)
            dc.SelectObject(wx.NullBitmap)
            
            self.__static_bitmap.SetBitmap(bitmap)
            self.__splash_screen.Refresh()
        finally:
            self.__splash_screen.Thaw()
        wx.SafeYield()

    def hide_splash_screen(self) -> None:
        self.__splash_screen.Destroy()
