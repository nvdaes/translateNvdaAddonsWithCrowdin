# -*- coding: utf-8 -*-
"""GUI for the Crowdin integration add-on."""

from __future__ import annotations

import wx


class CrowdinDialog(wx.Dialog):
	def __init__(self, parent=None):
		# Translators: Title of a dialog.
		title = _("NVDA add-ons with Crowdin")
		super().__init__(parent, title=title)

		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)

		# Translators: label of a dialog
		crowdinTokenLabel = _("Crowdin API token:")
		tokenLabel = wx.StaticText(panel, label=crowdinTokenLabel)
		self.tokenCtrl = wx.TextCtrl(panel)

		sizer.Add(tokenLabel, 0, wx.ALL, 5)
		sizer.Add(self.tokenCtrl, 0, wx.EXPAND | wx.ALL, 5)

		btnSizer = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
		sizer.Add(btnSizer, 0, wx.EXPAND | wx.ALL, 5)

		panel.SetSizerAndFit(sizer)
		self.Fit()

	def GetToken(self):
		return self.tokenCtrl.GetValue()
