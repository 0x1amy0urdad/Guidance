from __future__ import annotations

import os
import wx
import wx.lib.scrolledpanel as scrolled

import bg3moddinglib as bg3

from typing import Callable, cast
from uuid import uuid4

from ._guidance import APP_NAME, config, guidance
from ._logger import logger
from ._mod_metadata_dialog import ModMetadataDialog
from ._please_wait import PleaseWait
from ._runner import Runner
from ._splash import SplashScreen

class MainWindow(wx.Frame):
    ID_BTN_SCAN = wx.NewId()
    ID_BTN_SELECT_ALL = wx.NewId()
    ID_BTN_SHOW_ALL_MODS = wx.NewId()
    ID_BTN_MERGE = wx.NewId()
    ID_BTN_PATCH = wx.NewId()
    ID_BTN_OUTPUT = wx.NewId()
    ID_BTN_MODS = wx.NewId()
    ID_BTN_ABOUT = wx.NewId()
    ID_CONFLICT_LIST = wx.NewId()

    MOD_PRIORITY_LABELS = ('Top priority mod', '2nd priority mod', '3rd priority mod', 'th priority mod')

    __app: wx.App

    __g: guidance | None
    __config: config
    __select_all: bool
    __show_all_mods: bool
    __conflicts_detected: bool

    __splash: SplashScreen
    __please_wait: PleaseWait
    __runner: Runner
    __panel: wx.Panel
    __sizer: wx.BoxSizer

    __selections: dict[str, object]

    __timer: wx.Timer
    __state: int
    __handlers: dict[str, Callable[[dict], None]]

    __window_size: wx.Size

    __left_panel: wx.Panel
    __left_sizer: wx.BoxSizer
    __conflicts_label: wx.StaticText
    __mod_conflicts_list: wx.CheckListBox
    __left_bottom_panel: wx.Panel
    __left_bottom_sizer: wx.BoxSizer
    __select_all_button: wx.Button
    __show_all_mods_button: wx.Button
    __scan_mods_button: wx.Button
    
    __right_panel: wx.Panel
    __right_sizer: wx.BoxSizer
    __mod_priorities_labels: list[wx.StaticText]
    __mod_priorities_ids: list[int]
    __mod_priorities_choices: list[wx.Choice]
    __conflicted_dialogs_labels: list[wx.StaticText]
    __conflicts_summary: wx.StaticText
    __right_bottom_panel: wx.Panel
    __right_bottom_sizer: wx.BoxSizer
    __conflict_resolution_panel: scrolled.ScrolledPanel
    __conflict_resolution_sizer: wx.BoxSizer
    __merge_button: wx.Button
    __patch_button: wx.Button
    __output_button: wx.Button
    __about_button: wx.Button

    def __init__(self, app: wx.App, cfg: config, *args, **kwargs) -> None:
        super(MainWindow, self).__init__(None, *args, **kwargs)

        self.__app = app
        self.__splash = SplashScreen()
        self.__runner = Runner()
        self.__please_wait = PleaseWait(self, "Please wait ...", show_progress = True)
        self.__handlers = dict[str, Callable[[dict], None]]()
        self.__selections = dict[str, object]()
        self.__select_all = True
        self.__show_all_mods = False
        self.__conflicts_detected = False

        self.SetMinSize(wx.Size(1024, 768))
        self.SetSize(cfg.window_width, cfg.window_height)
    
        self.__mod_priorities_labels = list[wx.StaticText]()
        self.__mod_priorities_ids = list[int]()
        self.__mod_priorities_choices = list[wx.Choice]()
        self.__conflicted_dialogs_labels = list[wx.StaticText]()


        self.__g = None
        self.__config = cfg
        self.__state = 0
        self.__window_size = wx.Size(cfg.window_width, cfg.window_height)

        self.__panel = wx.Panel(self)
        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
    
        self.__left_panel = wx.Panel(self.__panel)
        self.__left_sizer = wx.BoxSizer(wx.VERTICAL)

        self.__mod_conflicts_list = wx.CheckListBox(self.__left_panel, id = MainWindow.ID_CONFLICT_LIST)
        self.__conflicts_label = wx.StaticText(self.__left_panel, label = 'Click "Scan mods" to find conflicts in your load order. Mods with conflicts will be listed below.')

        self.__left_bottom_panel = wx.Panel(self.__left_panel)
        self.__left_bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
    
        self.__scan_mods_button = wx.Button(self.__left_bottom_panel, id = MainWindow.ID_BTN_SCAN, label = 'Scan mods')
        self.__select_all_button = wx.Button(self.__left_bottom_panel, id = MainWindow.ID_BTN_SELECT_ALL, label = 'Select all')
        self.__show_all_mods_button = wx.Button(self.__left_bottom_panel, id = MainWindow.ID_BTN_SHOW_ALL_MODS, label = 'Show all mods')
    
        self.__left_bottom_sizer.Add(self.__scan_mods_button, proportion = 1, flag = wx.ALL, border = 5)
        self.__left_bottom_sizer.Add(self.__select_all_button, proportion = 1, flag = wx.ALL, border = 5)
        self.__left_bottom_sizer.Add(self.__show_all_mods_button, proportion = 1, flag = wx.ALL, border = 5)
    
        self.__left_bottom_panel.SetSizer(self.__left_bottom_sizer)

        self.__left_sizer.Add(self.__conflicts_label, proportion = 0, flag = wx.EXPAND | wx.ALL, border = 5)
        self.__left_sizer.Add(self.__mod_conflicts_list, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 5)
        self.__left_sizer.Add(self.__left_bottom_panel, proportion = 0, flag = wx.EXPAND)

        self.__left_panel.SetSizer(self.__left_sizer)

        self.__right_panel = wx.Panel(self.__panel)
        self.__right_sizer = wx.BoxSizer(wx.VERTICAL)

        self.__right_bottom_panel = wx.Panel(self.__right_panel)
        self.__right_bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.__merge_button = wx.Button(self.__right_bottom_panel, label = 'Merge', id = MainWindow.ID_BTN_MERGE)
        self.__patch_button = wx.Button(self.__right_bottom_panel, label = 'Patch', id = MainWindow.ID_BTN_PATCH)
        self.__output_button = wx.Button(self.__right_bottom_panel, label = 'Output', id = MainWindow.ID_BTN_OUTPUT)
        self.__mods_button = wx.Button(self.__right_bottom_panel, label = 'Mods', id = MainWindow.ID_BTN_MODS)
        self.__about_button = wx.Button(self.__right_bottom_panel, label = 'About', id = MainWindow.ID_BTN_ABOUT)

        self.__right_bottom_sizer.Add(self.__merge_button, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 5)
        self.__right_bottom_sizer.Add(self.__patch_button, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 5)
        self.__right_bottom_sizer.Add(self.__output_button, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 5)
        self.__right_bottom_sizer.Add(self.__mods_button, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 5)
        self.__right_bottom_sizer.Add(self.__about_button, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 5)

        self.__right_bottom_panel.SetSizer(self.__right_bottom_sizer)

        self.__conflicts_summary = wx.StaticText(self.__right_panel, label = "Details about conflicts will be shown below.")

        self.__conflict_resolution_panel = scrolled.ScrolledPanel(self.__right_panel, style = wx.BORDER_RAISED)
        self.__conflict_resolution_sizer = wx.BoxSizer(wx.VERTICAL)

        self.__conflict_resolution_sizer.Add(wx.StaticText(self.__conflict_resolution_panel, label = 'Please select conflicts that you would like to get resolved.'), flag = wx.TOP, border = 10)

        self.__conflict_resolution_panel.SetSizer(self.__conflict_resolution_sizer)
        self.__conflict_resolution_panel.SetupScrolling(False, True)
    
        self.__right_sizer.Add(self.__conflicts_summary, proportion = 0, flag = wx.EXPAND | wx.ALL, border = 5)
        self.__right_sizer.Add(self.__conflict_resolution_panel, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 5)
        self.__right_sizer.Add(self.__right_bottom_panel, proportion = 0, flag = wx.EXPAND)

        self.__right_panel.SetSizer(self.__right_sizer)

        self.__sizer.Add(self.__left_panel, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 5)
        self.__sizer.Add(self.__right_panel, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 5)

        self.__panel.SetSizer(self.__sizer)

        self.__timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.__timer)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_BUTTON, self.on_button)
        self.Bind(wx.EVT_CHECKLISTBOX, self.on_checklistbox)
        self.Bind(wx.EVT_CHOICE, self.on_choice)

        logger.info('Created main window')

    def start(self) -> None:
        self.register_handlers()
        self.__timer.Start(100)

    def register_handlers(self) -> None:
        self.__handlers['guidance_created'] = self.on_guidance_created
        self.__handlers['scan_mods'] = self.on_scan_mods_done
        self.__handlers['guidance_done'] = self.on_guidance_done

    #
    # Handlers
    #

    def on_guidance_created(self, d: dict) -> None:
        self.__splash.hide_splash_screen()
        self.__scan_mods_button.Enable()
        self.__select_all_button.Enable(self.__can_select_conflicts())
        self.__show_all_mods_button.Enable()
        self.__merge_button.Enable(self.__can_merge())
        self.__patch_button.Enable(self.__can_patch())
        self.Raise()
        self.Show()
        self.RequestUserAttention()

    def on_scan_mods_done(self, d: dict) -> None:
        self.__populate_conflicts()
        self.__select_all_button.Enable(self.__can_select_conflicts())
        self.__exit_wait_mode()
        self.__conflicts_detected = self.__conflicts_available()
        if not self.__conflicts_detected:
            wx.MessageBox(f'No conflicts are detected in your mods, you should be good to go.', caption = 'Guidance', style = wx.ICON_INFORMATION | wx.OK | wx.CENTER, parent = self)
        self.__patch_button.Enable(self.__can_patch())

    def on_guidance_done(self, d: dict) -> None:
        for i in range(self.__mod_conflicts_list.GetCount()):
            self.__mod_conflicts_list.Check(i, False)
        self.__exit_wait_mode()
        if 'status' not in d or not d['status']:
            wx.MessageBox(f'Something went wrong. Guidance failed. Please check the logs, or better yet, contact the author on discord.', caption = 'Guidance', style = wx.ICON_ERROR | wx.OK | wx.CENTER, parent = self)
        else:
            if self.__conflicts_detected:
                message = 'Guidance was successful. Conflicts were resolved.'
            else:
                message = 'Guidance was successful.'
            wx.MessageBox(message, caption = 'Guidance', style = wx.ICON_INFORMATION | wx.OK | wx.CENTER, parent = self)
            if self.__g:
                os.startfile(self.__g.env.output_path)
                appdata_path = guidance.find_bg3_appdata_path()
                if appdata_path:
                    os.startfile(os.path.join(appdata_path, 'Mods'))

    #
    # UI events
    #

    def on_timer(self, event: wx.Event) -> None:
        if self.__state == 0:
            self.__splash.show_splash_screen()
            self.__state = 1
            self.__create_guidance()
        elif self.__state == 1:
            r = self.__runner.poll_result()
            if r is None:
                return
            if self.__check_for_errors(r):
                return
            if 'result' in r:
                handler_name = r['result']
                if handler_name in self.__handlers:
                    logger.info(f'Running handler: {handler_name}')
                    self.__handlers[handler_name](r)
                else:
                    logger.error(f'Unknown handler {handler_name}; result: {r}')


    def on_size(self, event: wx.Event) -> None:
        self.__window_size = self.GetSize()
        self.__config.window_width = self.__window_size.width
        self.__config.window_height = self.__window_size.height
        event.Skip()

    def on_close(self, event: wx.Event) -> None:
        logger.info('Main window is closing')
        self.__config.save_config()
        self.__runner.stop()
        event.Skip()

    def on_button(self, event: wx.CommandEvent) -> None:
        if self.__g is None:
            event.StopPropagation()
            return
        if event.GetId() == MainWindow.ID_BTN_SCAN:
            self.__scan_mods()
            event.StopPropagation()
            return
        if event.GetId() == MainWindow.ID_BTN_SELECT_ALL:
            for i in range(0, self.__mod_conflicts_list.GetCount()):
                self.__mod_conflicts_list.Check(i, self.__select_all)
            self.__select_all = not self.__select_all
            if self.__select_all:
                self.__select_all_button.SetLabel('Select all')
            else:
                self.__select_all_button.SetLabel('Select none')
            self.__populate_conflict_info()
            self.__merge_button.Enable(self.__can_merge())
            self.__patch_button.Enable(self.__can_patch())
            event.StopPropagation()
            return
        if event.GetId() == MainWindow.ID_BTN_SHOW_ALL_MODS:
            if self.__show_all_mods:
                self.__show_all_mods_button.SetLabel('Show all mods')
                self.__show_all_mods = False
            else:
                self.__show_all_mods_button.SetLabel('Show conflicts only')
                self.__show_all_mods = True
            self.__populate_conflicts()
            self.__select_all = True
            self.__select_all_button.SetLabel('Select all')
            self.__select_all_button.Enable(self.__can_select_conflicts())
            self.__merge_button.Enable(self.__can_merge())
            self.__patch_button.Enable(self.__can_patch())
            event.StopPropagation()
            return
        if event.GetId() == MainWindow.ID_BTN_MERGE:
            self.__resolve_conflicts(bg3.conflict_resolution_method.MERGE)
            event.StopPropagation()
            return
        if event.GetId() == MainWindow.ID_BTN_PATCH:
            self.__resolve_conflicts(bg3.conflict_resolution_method.PATCH)
            event.StopPropagation()
            return
        if event.GetId() == MainWindow.ID_BTN_OUTPUT:
            if self.__g:
                os.startfile(self.__g.env.output_path)
            else:
                wx.MessageBox('Cannot find the output path :(', APP_NAME, style = wx.ICON_ERROR | wx.OK | wx.CENTER, parent = self)
            event.StopPropagation()
            return
        if event.GetId() == MainWindow.ID_BTN_MODS:
            appdata_path = guidance.find_bg3_appdata_path()
            if appdata_path:
                os.startfile(os.path.join(appdata_path, 'Mods'))
            else:
                wx.MessageBox('Cannot find the AppData path :(', APP_NAME, style = wx.ICON_ERROR | wx.OK | wx.CENTER, parent = self)
            event.StopPropagation()
            return
        if event.GetId() == MainWindow.ID_BTN_ABOUT:
            wx.MessageBox(
                f'{APP_NAME} made by Stan. The source code of this tool is available on GitHub under MIT License.\r\n'
                'Players can use this tool to resolve compatibility issues and conflicts in Baldur\'s Gate 3 mods.\r\n'
                'This tool is unofficial fan content, not reviewed/approved/endorsed by Larian Studios Ltd or Wizards of the Coast LLC.\r\n'
                'This tool uses a binary redistributable of LSLib made by Norbyte and collaborators.\r\n',
                caption = f'About {APP_NAME}',
                style = wx.ICON_INFORMATION | wx.OK | wx.CENTER, parent = self)
            event.StopPropagation()
            return

    def on_checklistbox(self, event: wx.CommandEvent) -> None:
        if self.__g is None:
            event.StopPropagation()
            return
        logger.info('on_checklistbox')
        if event.GetId() == MainWindow.ID_CONFLICT_LIST:
            self.__populate_conflict_info()
            self.__merge_button.Enable(self.__can_merge())
            self.__patch_button.Enable(self.__can_patch())
            event.StopPropagation()
            return

    def on_choice(self, event: wx.CommandEvent) -> None:
        if self.__g is None:
            event.StopPropagation()
            return
        n = self.__mod_conflicts_list.GetSelection()
        if n == wx.NOT_FOUND:
            event.StopPropagation()
            return
        conflict_name = self.__g.mod_manager.conflicts[n].get_conflict_name()
        selections_for_conflict = dict()
        for n in range(0, len(self.__mod_priorities_choices)):
            mod_priority_choice = self.__mod_priorities_choices[n]
            selections_for_conflict[f'mod_priority_{n}'] = mod_priority_choice.GetSelection()
        self.__selections[conflict_name] = selections_for_conflict
        logger.info(f'on_choice: {self.__selections}')

    def __can_select_conflicts(self) -> bool:
        return self.__mod_conflicts_list.GetCount() > 0

    def __can_patch(self) -> bool:
        if self.__g is None:
            return False
        n = 0
        for idx in self.__mod_conflicts_list.GetCheckedItems():
            if isinstance(idx, int):
                c = self.__g.mod_manager.conflicts[idx]
                if c.is_conflict:
                    return True
        return False

    def __can_merge(self) -> bool:
        return self.__can_patch() or len(self.__mod_conflicts_list.GetCheckedItems()) > 1

    def __enter_wait_mode(self) -> None:
        self.__please_wait.show()
        self.__scan_mods_button.Disable()
        self.__select_all_button.Disable()
        self.__show_all_mods_button.Disable()
        self.__merge_button.Disable()
        self.__patch_button.Disable()

    def __exit_wait_mode(self) -> None:
        self.__please_wait.hide()
        self.__scan_mods_button.Enable()
        self.__select_all_button.Enable(self.__can_select_conflicts())
        self.__show_all_mods_button.Enable()
        self.__merge_button.Enable(self.__can_merge())
        self.__patch_button.Enable(self.__can_patch())

    def __create_guidance_progress_callback(self, count: int, total: int, status: str) -> None:
        self.__splash.update_status(status)

    def __create_guidance(self) -> None:
        logger.info('Starting initialization')
        def payload(d: dict) -> dict:
            self.__g = guidance(self.__config)
            self.__g.mod_manager.reload_mods(progress_callback = self.__create_guidance_progress_callback)
            conflicts = list[str]()
            if self.__g.mod_manager.detect_conflicts():
                for mod_conflict in self.__g.mod_manager.conflicts:
                    if mod_conflict.is_conflict:
                        n = mod_conflict.get_conflict_name()
                        conflicts.append(n)
                        logger.info(f'conflict detected: {n}')
            logger.info('Finished initialization')
            self.__runner.add_result({ 'result': 'guidance_created' })
            return { 'result': 'scan_mods', 'conflicts': tuple(conflicts) }

        self.__runner.run_job(payload)

    def __scan_mods(self) -> None:
        def payload(d: dict) -> dict:
            if self.__g is None:
                return { 'result': 'scan_mods', 'conflicts': () }
            self.__g.mod_manager.reload_mods(progress_callback = self.__please_wait_progress_callback)
            if self.__g.mod_manager.detect_conflicts(progress_callback = self.__please_wait_progress_callback):
                conflicts = list[str]()
                for mod_conflict in self.__g.mod_manager.conflicts:
                    n = mod_conflict.get_conflict_name()
                    conflicts.append(n)
                    logger.info(f'conflict detected: {n}')
                return { 'result': 'scan_mods', 'conflicts': tuple(conflicts) }
            return { 'result': 'scan_mods', 'conflicts': () }

        self.__enter_wait_mode()
        self.__runner.run_job(payload)

    def __check_for_errors(self, r: dict) -> bool:
        if 'error' in r:
            self.__exit_wait_mode()
            exc_name = r['error']
            if 'message' in r:
                exc_message = r['message'].replace('D:\\bg3modding\\src\\bg3modding\\src', '...')
            else:
                exc_message = 'No further details are available'
            message = f'An unexpected error has occurred. Please check the log file for details.\nError message: "{exc_name}"\n{exc_message}\n'
            wx.MessageBox(message, caption = 'Guidance', style = wx.ICON_ERROR | wx.OK | wx.CENTER, parent = self)
            if self.__g is None or self.__splash.visible:
                self.__splash.hide_splash_screen()
                self.__runner.stop()
                self.Close(force = True)
                return True
            return True
        return False

    def __populate_conflicts(self) -> None:
        if self.__g is None:
            return
        self.__mod_conflicts_list.Clear()
        for c in self.__g.mod_manager.conflicts:
            if c.is_conflict or self.__show_all_mods:
                self.__mod_conflicts_list.Append(c.get_conflict_name())
        for i in range(self.__mod_conflicts_list.GetCount()):
            self.__mod_conflicts_list.Check(i, False)
        self.__populate_conflict_info()

    def __conflicts_available(self) -> bool:
        if self.__g is not None:
            for c in self.__g.mod_manager.conflicts:
                if c.is_conflict:
                    return True
        return False

    def __populate_conflict_info(self) -> None:
        if self.__g is None or len(self.__g.mod_manager.conflicts) == 0:
            self.__conflicts_summary.SetLabel(f'No conflicts are selected for resolution.')
            return

        for label in self.__mod_priorities_labels:
            self.__conflict_resolution_sizer.Detach(label)
            label.Destroy()
        for choice in self.__mod_priorities_choices:
            self.__conflict_resolution_sizer.Detach(choice)
            choice.Destroy()
        for label in self.__conflicted_dialogs_labels:
            self.__conflict_resolution_sizer.Detach(label)
            label.Destroy()

        self.__mod_priorities_labels = list[wx.StaticText]()
        self.__mod_priorities_ids = list[int]()
        self.__mod_priorities_choices = list[wx.Choice]()
        self.__conflicted_dialogs_labels = list[wx.StaticText]()

        selected_mods = list[bg3.mod_info]()
        selected_mods_uuids = set[str]()
        conflicting_dialogs = list[str]()
        n = 0
        for conflict in self.__g.mod_manager.conflicts:
            if not conflict.is_conflict and not self.__show_all_mods:
                continue
            selected = self.__mod_conflicts_list.IsChecked(n)
            n += 1
            if not selected:
                continue
            for mod in conflict.mods:
                if mod.mod_uuid not in selected_mods_uuids:
                    selected_mods_uuids.add(mod.mod_uuid)
                    selected_mods.append(mod)
            if conflict.dialogs:
                conflicting_dialogs.append(f'-- {conflict.get_conflict_name()} --')
                for dialog_uuid in conflict.dialogs:
                    dialog_name = self.__g.index.get_dialog_name(dialog_uuid)
                    if len(dialog_name) > 64:
                        dialog_name = dialog_name[:64]
                    conflicting_dialogs.append(f'{dialog_name:64} [{dialog_uuid}]')

        priority_items = [''] + [f'{mod.mod_name} [{mod.mod_uuid}]' for mod in selected_mods]
        for i in range(0, len(selected_mods)):
            choice_id = wx.NewId()
            choice = wx.Choice(self.__conflict_resolution_panel, choice_id)
            if i < len(MainWindow.MOD_PRIORITY_LABELS) - 1:
                label_text = MainWindow.MOD_PRIORITY_LABELS[i]
            else:
                label_text = f'{i}{MainWindow.MOD_PRIORITY_LABELS[-1]}'
            label = wx.StaticText(self.__conflict_resolution_panel, label = label_text)
            self.__mod_priorities_labels.append(label)
            self.__mod_priorities_ids.append(choice_id)
            self.__mod_priorities_choices.append(choice)
            choice.SetItems(priority_items)
            self.__conflict_resolution_sizer.Add(label, flag = wx.EXPAND)
            self.__conflict_resolution_sizer.Add(choice, flag = wx.EXPAND | wx.BOTTOM, border = 10)

        n = len(conflicting_dialogs)
        if n > 0:
            label = wx.StaticText(self.__conflict_resolution_panel, label = "Conflicts were found in the following dialogs:")
            self.__conflict_resolution_sizer.Add(label, flag = wx.TOP, border = 10)
            self.__conflicted_dialogs_labels.append(label)
            for line in conflicting_dialogs:
                label = wx.StaticText(self.__conflict_resolution_panel, label = line)
                self.__conflict_resolution_sizer.Add(label)
                self.__conflicted_dialogs_labels.append(label)

        self.__conflict_resolution_panel.Layout()
        self.__conflict_resolution_panel.SetupScrolling()

        if n == 0:
            self.__conflicts_summary.SetLabel(f'No conflicts are selected for resolution.')
        else:
            if n == 1:
                self.__conflicts_summary.SetLabel(f'Found 1 dialog file with conflicts.')
            else:
                self.__conflicts_summary.SetLabel(f'Found {n} dialog files with conflicts.')

    def __create_settings(self, method: bg3.conflict_resolution_method) -> str | bg3.conflict_resolution_settings:
        if self.__g is None:
            logger.info('__create_settings failed: guidance is not initialized')
            return 'Not initialized'

        if len(self.__mod_conflicts_list.GetCheckedItems()) == 0:
            return 'Please, check at least one conflict for resolution.'

        chosen_conflicts = list[int]()
        mod_priority_order = list[str]()

        for i in self.__mod_conflicts_list.GetCheckedItems():
            conflict_index = cast(int, i)
            chosen_conflicts.append(conflict_index)

        mod_names = list[str]()
        added_mod_uuids = set[str]()
        for choice in self.__mod_priorities_choices:
            choice_idx = choice.GetSelection()
            if choice_idx < 0:
                return 'Incomplete or incorrect mod priority list.'
            mod_name = choice.GetString(choice_idx)
            pos1 = mod_name.rfind('[')
            pos2 = mod_name.rfind(']')
            if pos1 == -1 or pos2 == -1 or pos2 <= pos1:
                return 'Incomplete or incorrect mod priority list.'
            mod_uuid = mod_name[pos1 + 1: pos2]
            if mod_uuid in added_mod_uuids:
                return 'Duplicates are in the mod priority list.'
            mod_priority_order.append(mod_uuid)
            added_mod_uuids.add(mod_uuid)
            mod_names.append(mod_name[: pos1].replace(' ', ''))

        mi = self.__g.mod_manager.get_mod_info(mod_priority_order[0])
        if method == bg3.conflict_resolution_method.PATCH:
            patch_name = f'Compatibility Patch'
            patch_description = f'Compatibility Patch for: {', '.join(mod_names)}'
            if len(patch_description) > 249:
                patch_description = patch_description[:249]
            default_metadata = {
                'mod_display_name': patch_name,
                'mod_description': patch_description,
                'mod_uuid': str(uuid4()),
                'mod_author': 'Anonymous',
                'mod_version': f'1.0.0.0'
            }
        else:
            default_metadata = {
                'mod_display_name': mi.mod_name,
                'mod_description': mi.mod_description,
                'mod_uuid': mi.mod_uuid,
                'mod_author': mi.mod_author,
                'mod_version': f'{mi.mod_version[0]}.{mi.mod_version[1]}.{mi.mod_version[2]}.{mi.mod_version[3]}'
            }

        dlg = ModMetadataDialog(self, default_metadata, method)
        dlg_choice = dlg.ShowModal()
        if dlg_choice != wx.ID_OK:
            return 'Cancelled by user'
        numbers = dlg.mod_metadata['mod_version'].split('.')
        version = (int(numbers[0]), int(numbers[1]), int(numbers[2]), int(numbers[3]))
        metadata = bg3.mod_metadata(
            bg3.mod_manager.make_mod_short_name(dlg.mod_metadata['mod_display_name']),
            dlg.mod_metadata['mod_display_name'],
            dlg.mod_metadata['mod_description'],
            dlg.mod_metadata['mod_uuid'],
            dlg.mod_metadata['mod_author'],
            version)
        install_when_done = dlg.install_when_done
        dlg.Destroy()

        return bg3.conflict_resolution_settings(tuple(chosen_conflicts), tuple(mod_priority_order), metadata = metadata, install_when_done = install_when_done)

    def __please_wait_progress_callback(self, count: int, total_count: int, message: str) -> None:
        if total_count <= 0 or count <= 0:
            progress = 0
        else:
            progress = int(100.0 * float(count) / float(total_count))
        self.__please_wait.update_status(message = message, progress = progress)

    def __resolve_conflicts(self, method: bg3.conflict_resolution_method) -> None:
        if self.__g is None:
            logger.info('__resolve_conflicts failed: guidance is not initialized')
            return

        settings = self.__create_settings(method)
        logger.info(f'__resolve_conflicts settings: {settings}')
        if isinstance(settings, str):
            logger.info(f'__resolve_conflicts failed: {settings}')
            wx.MessageBox(settings, caption = 'Failed to cast Guidance', style = wx.OK | wx.CENTER | wx.ICON_ERROR)
            return

        for conflict_index in settings.chosen_conflicts:
            logger.info(f"enabled for conflict '{self.__g.mod_manager.conflicts[conflict_index].get_conflict_name()}'")

        i = 0
        for mod_uuid in settings.priority_order:
            logger.info(f'mod_priority_order[i] = {mod_uuid}')
            i += 1

        self.__enter_wait_mode()

        def payload(d: dict) -> dict:
            if self.__g is None:
                return { 'result': 'guidance_done', 'status': False, 'message': 'Failed, Guidance is not initialized' }
            result = self.__g.mod_manager.resolve_conflicts(settings, method, progress_callback = self.__please_wait_progress_callback)
            return { 'result': 'guidance_done', 'status': result[0], 'message': result[1] }

        self.__runner.run_job(payload)
