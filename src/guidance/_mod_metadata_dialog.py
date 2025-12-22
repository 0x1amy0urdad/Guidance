from __future__ import annotations

import bg3moddinglib as bg3

import re
import wx

class ModMetadataDialog(wx.Dialog):
    ID_COPY_TO_MODS_CHECKBOX = wx.NewIdRef()
    ID_USE_TOP_MOD_CHECKBOX = wx.NewIdRef()
    ID_GENERATE_UUID = wx.NewIdRef()
    ID_MOD_DISPLAY_NAME = wx.NewIdRef()
    ID_MOD_DESCRIPTION = wx.NewIdRef()
    ID_MOD_UUID = wx.NewIdRef()
    ID_MOD_AUTHOR = wx.NewIdRef()
    ID_MOD_VERSION = wx.NewIdRef()
    METADATA_KEYS = ('mod_display_name', 'mod_description', 'mod_uuid', 'mod_author', 'mod_version')

    __copy_result_to_mods: wx.CheckBox
    __use_top_mod_metadata: wx.CheckBox
    __mod_display_name: wx.TextCtrl
    __mod_description: wx.TextCtrl
    __mod_uuid: wx.TextCtrl
    __generate_uuid: wx.Button
    __mod_author: wx.TextCtrl
    __mod_version: wx.TextCtrl

    __mod_metadata: dict[str, str]
    __default_mod_metadata: dict[str, str]


    def __init__(
            self,
            parent: wx.Window,
            default_mod_metadata: dict[str, str],
            method: bg3.conflict_resolution_method,
            title: str = "Mod Metadata"
    ) -> None:
        super().__init__(parent, title = title, size = wx.Size(640, 520))
        
        self.__default_mod_metadata = default_mod_metadata
        self.__mod_metadata = dict[str, str]()
        for k in ModMetadataDialog.METADATA_KEYS:
            if k not in default_mod_metadata:
                raise ValueError(f'default_mod_metadata does not contain value for "{k}"')
            self.__mod_metadata[k] = default_mod_metadata[k]

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        panel = wx.Panel(self)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        panel_sizer.Add(wx.StaticText(panel, label = 'Please fill out mod metadata values and click "Ok" to generate the mod.'), 0, wx.TOP | wx.BOTTOM | wx.CENTER, 20)

        if method == bg3.conflict_resolution_method.MERGE:
            copy_to_mods__label = 'Replace merged mods with the new one'
        else:
            copy_to_mods__label = 'Put the patch into the mods folder'
        self.__copy_result_to_mods = wx.CheckBox(panel, label = copy_to_mods__label, id = ModMetadataDialog.ID_COPY_TO_MODS_CHECKBOX)
        panel_sizer.Add(self.__copy_result_to_mods, 0, wx.ALL, 10)

        self.__use_top_mod_metadata = wx.CheckBox(panel, label = 'Re-use metadata from the top priority mod', id = ModMetadataDialog.ID_USE_TOP_MOD_CHECKBOX)
        panel_sizer.Add(self.__use_top_mod_metadata, 0, wx.ALL, 10)
        
        panel_sizer.Add(wx.StaticText(panel, label = 'Mod display name:'), 0, wx.TOP | wx.LEFT | wx.RIGHT, 10)
        self.__mod_display_name = wx.TextCtrl(panel, id = ModMetadataDialog.ID_MOD_DISPLAY_NAME, value = self.__mod_metadata['mod_display_name'])
        panel_sizer.Add(self.__mod_display_name, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        panel_sizer.Add(wx.StaticText(panel, label = 'Mod description (up to 250 characters):'), 0, wx.TOP | wx.LEFT | wx.RIGHT, 10)
        self.__mod_description = wx.TextCtrl(panel, id = ModMetadataDialog.ID_MOD_DESCRIPTION, value = self.__mod_metadata['mod_description'])
        panel_sizer.Add(self.__mod_description, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        uuid_panel = wx.Panel(panel)
        uuid_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        panel_sizer.Add(wx.StaticText(panel, label = 'Mod UUID:'), 0, wx.TOP | wx.LEFT | wx.RIGHT, 10)
        self.__mod_uuid = wx.TextCtrl(uuid_panel, id = ModMetadataDialog.ID_MOD_UUID, value = self.__mod_metadata['mod_uuid'])
        self.__generate_uuid = wx.Button(uuid_panel, id = ModMetadataDialog.ID_GENERATE_UUID, label = 'Generate UUID')
        uuid_sizer.Add(self.__mod_uuid, 1, wx.EXPAND, 0)
        uuid_sizer.Add(self.__generate_uuid, 0, wx.EXPAND, 0)
        uuid_panel.SetSizer(uuid_sizer)
        panel_sizer.Add(uuid_panel, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        

        panel_sizer.Add(wx.StaticText(panel, label = 'Mod author:'), 0, wx.TOP | wx.LEFT | wx.RIGHT, 10)
        self.__mod_author = wx.TextCtrl(panel, id = ModMetadataDialog.ID_MOD_AUTHOR, value = self.__mod_metadata['mod_author'])
        panel_sizer.Add(self.__mod_author, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        panel_sizer.Add(wx.StaticText(panel, label = 'Mod version (must be 4 numbers separated by dots):'), 0, wx.TOP | wx.LEFT | wx.RIGHT, 10)
        self.__mod_version = wx.TextCtrl(panel, id = ModMetadataDialog.ID_MOD_VERSION, value = self.__mod_metadata['mod_version'])
        panel_sizer.Add(self.__mod_version, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        panel.SetSizer(panel_sizer)
        
        # Add panel to main sizer
        main_sizer.Add(panel, 1, wx.EXPAND)
        
        # Standard dialog buttons (OK and Cancel) - these are children of the dialog
        btn_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        main_sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        # Set the main sizer on the dialog
        self.SetSizer(main_sizer)
        
        # Bind events
        self.Bind(wx.EVT_CHECKBOX, self.on_checkbox)
        self.Bind(wx.EVT_BUTTON, self.on_ok, id = wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, id = wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_uuidgen, id = ModMetadataDialog.ID_GENERATE_UUID)


    @property
    def mod_metadata(self) -> dict[str, str]:
        return self.__mod_metadata

    @property
    def install_when_done(self) -> bool:
        return self.__copy_result_to_mods.IsChecked()

    def on_checkbox(self, event: wx.CommandEvent) -> None:
        is_checked = self.__use_top_mod_metadata.IsChecked()
        if is_checked:
            for k in ModMetadataDialog.METADATA_KEYS:
                self.__mod_metadata[k] = self.__default_mod_metadata[k]
            self.__mod_display_name.SetValue(self.__mod_metadata['mod_display_name'])
            self.__mod_description.SetValue(self.__mod_metadata['mod_description'])
            self.__mod_uuid.SetValue(self.__mod_metadata['mod_uuid'])
            self.__mod_author.SetValue(self.__mod_metadata['mod_author'])
            self.__mod_version.SetValue(self.__mod_metadata['mod_version'])
            self.__mod_display_name.Disable()
            self.__mod_description.Disable()
            self.__mod_uuid.Disable()
            self.__generate_uuid.Disable()
            self.__mod_author.Disable()
            self.__mod_version.Disable()
        else:
            self.__mod_display_name.Enable()
            self.__mod_description.Enable()
            self.__mod_uuid.Enable()
            self.__generate_uuid.Enable()
            self.__mod_author.Enable()
            self.__mod_version.Enable()
        event.Skip()


    def on_ok(self, event: wx.CommandEvent) -> None:
        self.__mod_metadata = {
            'mod_display_name': self.__mod_display_name.GetValue(),
            'mod_description': self.__mod_description.GetValue(),
            'mod_uuid': self.__mod_uuid.GetValue(),
            'mod_author': self.__mod_author.GetValue(),
            'mod_version': self.__mod_version.GetValue(),
        }
        if len(self.__mod_metadata['mod_display_name']) == 0:
            wx.MessageBox("Please enter a valid mod name.", "Validation Error", wx.OK | wx.ICON_WARNING)
            return
        if len(self.__mod_metadata['mod_description']) > 250:
            self.__mod_metadata['mod_description'] = self.__mod_metadata['mod_description'][:250]
        if re.match('^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', self.__mod_metadata['mod_uuid']) is None:
            wx.MessageBox("Please enter a valid UUID.", "Validation Error", wx.OK | wx.ICON_WARNING)
            return
        if len(self.__mod_metadata['mod_author']) == 0:
            wx.MessageBox("Please enter a valid mod name.", "Validation Error", wx.OK | wx.ICON_WARNING)
            return
        if re.match('^\\d+\\.\\d+\\.\\d+\\.\\d+$', self.__mod_metadata['mod_version']) is None:
            wx.MessageBox("Please enter a valid mod version, for examle: 1.2.3.4", "Validation Error", wx.OK | wx.ICON_WARNING)
            return
        event.Skip()


    def on_cancel(self, event: wx.CommandEvent) -> None:
        self.__mod_metadata = {
            'mod_display_name': '',
            'mod_description': '',
            'mod_uuid': '',
            'mod_author': '',
            'mod_version': '',
        }
        event.Skip()


    def on_uuidgen(self, event: wx.CommandEvent) -> None:
        self.__mod_uuid.SetValue(bg3.new_random_uuid())
        event.Skip()
