# translateNvdaAddonsWithCrowdin
# Copyright (C) 2025 Noelia Ruiz Martínez, other contributors
# Released under GPL 2

import wx

import addonHandler
import config
import globalPluginHandler
import gui
from gui.settingsDialogs import NVDASettingsDialog
from scriptHandler import script
from globalCommands import SCRCAT_CONFIG
from inputCore import InputGesture

from .addonGui import AddonSettingsPanel, ToolsDialog, ADDON_SUMMARY

addonHandler.initTranslation()


confspec = {
	"translationsDirectory": "string(default='')",
}

config.conf.spec["translateNvdaAddonsWithCrowdin"] = confspec


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = ADDON_SUMMARY

	def __init__(self):
		super().__init__()
		NVDASettingsDialog.categoryClasses.append(AddonSettingsPanel)
		self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
		# Translators: the name of a menu item.
		self.crowdinItem = self.toolsMenu.Append(wx.ID_ANY, _("&Translate add-ons with Crowdin..."))
		gui.mainFrame.sysTrayIcon.Bind(
			wx.EVT_MENU,
			self.onCrowdin,
			self.crowdinItem,
		)

	def terminate(self):
		NVDASettingsDialog.categoryClasses.remove(AddonSettingsPanel)
		self.toolsMenu.Remove(self.crowdinItem)

	def onCrowdin(self, evt: wx.CommandEvent):
		gui.mainFrame.prePopup()
		d = ToolsDialog(gui.mainFrame)
		d.Show()
		gui.mainFrame.postPopup()

	def onSettings(self, evt: wx.CommandEvent):
		gui.mainFrame.popupSettingsDialog(NVDASettingsDialog, AddonSettingsPanel)

	@script(
		# Translators: message presented in input mode.
		description=_("Shows the Translate NVDA Add-ons with Crowdin settings."),
		category=SCRCAT_CONFIG,
	)
	def script_settings(self, gesture: InputGesture):
		wx.CallAfter(self.onSettings, None)

	@script(
		# Translators: message presented in input mode.
		description=_("Shows the Translate NVDA Add-ons with Crowdin dialog."),
	)
	def script_tools(self, gesture: InputGesture):
		wx.CallAfter(self.onCrowdin, None)
