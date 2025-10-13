# translateNvdaAddonsWithCrowdin
# Copyright (C) 2025 Noelia Ruiz Martínez, other contributors
# Released under GPL 2

import os
import sys
import wx
import json
import re
import threading

import addonHandler
import config
import languageHandler
import ui
from speech.priorities import Spri
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel
from logHandler import log

from . import l10nUtil, markdownTranslate

addonHandler.initTranslation()

ADDON_SUMMARY = addonHandler.getCodeAddon().manifest["summary"]
AVAILABLE_FILES_PATH = os.path.join(os.path.dirname(__file__), "files.json")
L10N_UTIL_PATH = os.path.join(os.path.dirname(__file__), "l10nUtil.py")


languageMappings: dict[str, str] = {
	"af_ZA": "af",
	"de_CH": "de-CH",
	"es": "es-ES",
	"es_CO": "es-CO",
	"nb_NO": "nb",
	"nn_NO": "nn-NO",
	"pt_PT": "pt-PT",
	"pt_BR": "pt-BR",
	"sr": "sr-CS",
	"zh_CN": "zh-CN",
	"zh_HK": "zh-HK",
	"zh_TW": "zh-TW",
}

def exportTranslations(language: str | None = None) -> None:
	"""Export translations from Crowdin.
	:param language: The language of translation files.
	"""

	dir = getTranslationsDirectory()
	try:
		l10nUtil.exportTranslations(dir, language)
	except Exception as e:
		# Translators: Message presented when translations cannot be downloaded.
		ui.message(_("Cannot download translations. See NVDA log for more details"))
		log.error("Translations not downloaded", exc_info=True)
		return
	def mainThreadCallback():
		# Translators: Message presented when translations have been exported.
		ui.message(_("Translations exported"), Spri.NEXT)
	wx.CallAfter(mainThreadCallback)


def downloadTranslationFile(crowdinFilePath: str, localFilePath: str, language: str) -> None:
	"""Download a translation file from Crowdin.
	:param crowdinFilePath: The path to the file in Crowdin.
	:param localFilePath: The path to the file stored locally.
	:param language: The language of the translation file.
	"""
	try:
		l10nUtil.downloadTranslationFile(crowdinFilePath, localFilePath, language)
	except Exception as e:
		# Translators: Message presented when a translation file cannot be downloaded.
		ui.message(_("Cannot download translated file. See NVDA log for more details"))
		log.error("Translation file not downloaded", exc_info=True)
		return
	def mainThreadCallback():
		# Translators: Message presented when a translation file has been downloaded.
		ui.message(_("Translation file downloaded to %s" % localFilePath), Spri.NEXT)
	wx.CallAfter(mainThreadCallback)


def uploadTranslatedFile(crowdinFilePath: str, localFilePath: str, language: str):
	"""Upload a translated file to Crowdin.
	:param crowdinFilePath: The path to the file in Crowdin.
	:param localFilePath: The path to the file stored locally.
	:param language: The language of the translated file.
	"""
	if os.path.splitext(localFilePath)[1] == ".xliff":
		mdPath = os.path.join(os.path.dirname(localFilePath), "readme.md")
		if os.path.isfile(mdPath):
			markdownTranslate.translateXliff(localFilePath, language, mdPath, localFilePath)
			os.remove(mdPath)
	try:
		l10nUtil.uploadTranslationFile(crowdinFilePath, localFilePath, language)
	except Exception as e:
		# Translators: Message presented when a translation file cannot be uploaded.
		ui.message(_("Cannot upload translated file. See NVDA log for more details"))
		log.error("Translation file not uploaded", exc_info=True)
		return
	def mainThreadCallback():
		# Translators: Message presented when a translated file has been uploaded.
		ui.message(_("Translated file uploaded"), Spri.NEXT)
	wx.CallAfter(mainThreadCallback)


def getTranslationsDirectory() -> str:
	"""Get the directory to store translations.
	:return: The directory to store translations.
	"""

	dir = config.conf["translateNvdaAddonsWithCrowdin"]["translationsDirectory"]
	if not dir:
		dir = os.path.join("%appdata%", "translateNvdaAddonsWithCrowdin")
	return dir


class AddonSettingsPanel(SettingsPanel):
	title = ADDON_SUMMARY

	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		crowdinTokenLabel = _(
			# Translators: label of a dialog.
			"Crowdin API token:",
		)
		self.crowdinTokenEdit = sHelper.addLabeledControl(crowdinTokenLabel, wx.TextCtrl)

		# Translators: The label of a grouping containing controls to select the destination directory for Crowdin translations.
		directoryGroupText = _("Translations directory:")
		groupSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=directoryGroupText)
		groupHelper = sHelper.addItem(guiHelper.BoxSizerHelper(self, sizer=groupSizer))
		groupBox = groupSizer.GetStaticBox()
		# Translators: The label of a button to browse for a directory.
		browseText = _("Browse...")
		# Translators: The title of the dialog presented when browsing for the translations directory.
		dirDialogTitle = _("Select translations directory")
		directoryPathHelper = guiHelper.PathSelectionHelper(groupBox, browseText, dirDialogTitle)
		directoryEntryControl = groupHelper.addItem(directoryPathHelper)
		self.translationsDirectoryEdit = directoryEntryControl.pathControl
		self.translationsDirectoryEdit.SetValue(config.conf["translateNvdaAddonsWithCrowdin"]["translationsDirectory"])

	def onSave(self):
		token = self.crowdinTokenEdit.GetValue().strip()
		if token:
			token_path = os.path.expanduser("~/.nvda_crowdin")
			with open(token_path, "w") as f:
				f.write(token)
		config.conf["translateNvdaAddonsWithCrowdin"]["translationsDirectory"] = self.translationsDirectoryEdit.Value


class ToolsDialog(wx.Dialog):
	_instance = None

	def __new__(cls, *args, **kwargs):
		# Make this a singleton.
		if ToolsDialog._instance is None:
			return super(ToolsDialog, cls).__new__(cls, *args, **kwargs)
		return ToolsDialog._instance

	def __init__(self, parent):
		if ToolsDialog._instance is not None:
			return
		ToolsDialog._instance = self

		super().__init__(
			parent,
			# Translators: Title of a dialog.
			title=_("NVDA add-ons with Crowdin")
		)

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		self.languageNames = languageHandler.getAvailableLanguages(presentational=True)[1:]  # Exclude default Windows language
		index = [x[0] for x in self.languageNames].index("en")
		self.languageNames.pop(index)
		languageChoices = [x[1] for x in self.languageNames]
		# Translators: The label to select a language to translate add-ons.
		languageLabelText = _("&Language:")
		self.languageList = sHelper.addLabeledControl(
			languageLabelText,
			wx.Choice,
			choices=languageChoices,
		)
		try:
			index = [x[0] for x in self.languageNames].index(languageHandler.getLanguage())
		except ValueError:
			index = [x[0] for x in self.languageNames].index(languageHandler.getLanguage().split("_")[0])
		self.languageList.SetSelection(index)

		# Translators: Label of a dialog to filter a list of choices.
		searchTextLabel = _("&Filter by file list:")
		self.searchTextEdit = sHelper.addLabeledControl(searchTextLabel, wx.TextCtrl)
		self.searchTextEdit.Bind(wx.EVT_TEXT, self.onSearchEditTextChange)

		toolsListGroupSizer = wx.StaticBoxSizer(wx.StaticBox(self), wx.HORIZONTAL)
		toolsListGroupContents = wx.BoxSizer(wx.HORIZONTAL)
		changeToolsSizer = wx.BoxSizer(wx.VERTICAL)
		with open(AVAILABLE_FILES_PATH, "rt") as f:
			files = json.load(f)
			self._files = files.keys()
			self.choices = [file.replace(".pot", ".po") for file in self._files]
			self.choices.sort()
		self.filteredItems = []
		for n in range(len(self.choices)):
			self.filteredItems.append(n)
		self.toolsList = wx.ListBox(
			self,
			choices=self.choices,
		)
		self.toolsList.Selection = 0
		changeToolsSizer.Add(self.toolsList, proportion=1)
		changeToolsSizer.AddSpacer(guiHelper.SPACE_BETWEEN_BUTTONS_VERTICAL)

		# Translators: The label of a button to open a file to be translated.
		self.openButton = wx.Button(self, label=_("&Open file to translate"))
		self.openButton.Bind(wx.EVT_BUTTON, self.onOpen)
		self.AffirmativeId = self.openButton.Id
		self.openButton.SetDefault()
		changeToolsSizer.Add(self.openButton)

		toolsListGroupContents.Add(changeToolsSizer, flag=wx.EXPAND)
		toolsListGroupContents.AddSpacer(guiHelper.SPACE_BETWEEN_ASSOCIATED_CONTROL_HORIZONTAL)

		buttonHelper = guiHelper.ButtonHelper(wx.VERTICAL)
		# Translators: The label of a button to upload a translated file.
		self.uploadButton = buttonHelper.addButton(self, label=_("&Upload translated file"))
		self.uploadButton.Bind(wx.EVT_BUTTON, self.onUpload)

		# Translators: The label of a button to download translations for a specific language.
		self.downloadForLanguageButton = buttonHelper.addButton(self, label=_("&Download translations for the selected language"))
		self.downloadForLanguageButton.Bind(wx.EVT_BUTTON, self.onDownloadForLanguage)

		# Translators: The label of a button to download all translations.
		self.downloadButton = buttonHelper.addButton(self, label=_("Do&wnload all translations"))
		self.downloadButton.Bind(wx.EVT_BUTTON, self.onDownload)

	# Message translated in NVDA core, label of a button to close a dialog.
		closeButton = wx.Button(self, wx.ID_CLOSE, label=_("&Close"))
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Close())
		sHelper.addDialogDismissButtons(closeButton)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.EscapeId = wx.ID_CLOSE

		self.onToolsListChoice(None)
		mainSizer.Add(sHelper.sizer, flag=wx.ALL, border=guiHelper.BORDER_FOR_DIALOGS)
		mainSizer.Fit(self)
		self.Sizer = mainSizer
		self.toolsList.SetFocus()
		self.CentreOnScreen()

	def __del__(self):
		ToolsDialog._instance = None

	def onSearchEditTextChange(self, evt: wx.CommandEvent):
		self.toolsList.Clear()
		self.filteredItems = []
		# Based on the filter of the Input gestures dialog of NVDA's core.
		filter = self.searchTextEdit.Value
		if filter:
			filter = re.escape(filter)
			filterReg = re.compile(
				r"(?=.*?" + r")(?=.*?".join(filter.split(r"\ ")) + r")",
				re.U | re.IGNORECASE,
			)
		for index, choice in enumerate(self.choices):
			if filter and not filterReg.match(choice):
				continue
			self.filteredItems.append(index)
			self.toolsList.Append(choice)
		if len(self.filteredItems) >= 1:
			self.toolsList.Selection = 0
			self.onToolsListChoice(None)
		else:
			for control in (
				self.toolsList,
				self.openButton,
				self.uploadButton,
			):
				control.Enabled = False

	def onToolsListChoice(self, evt: wx.CommandEvent):
		self.toolsList.Enable()
		self.sel = self.toolsList.Selection
		self.stringSel = self.toolsList.GetString(self.sel)
		self.openButton.Enabled = self.sel >= 0
		self.uploadButton.Enabled = self.sel >= 0

	def onOpen(self, evt: wx.CommandEvent):
		translationsDirectory = getTranslationsDirectory()
		addonName = os.path.splitext(self.toolsList.GetStringSelection())[0]
		language = self.languageNames[self.languageList.GetSelection()][0]
		filename = self.toolsList.GetStringSelection()
		filePath = os.path.join(translationsDirectory, addonName, language, filename)
		if os.path.isfile(filePath):
			os.startfile(filePath)
		else:
			# Translators: Message presented when trying to open a file which doesn't exist.
			ui.message(_("File not found))"))

	def onUpload(self, evt: wx.CommandEvent):
		translationsDirectory = getTranslationsDirectory()
		addonName = os.path.splitext(self.toolsList.GetStringSelection())[0]
		crowdinLanguage = self._getLanguage()
		filename = self.toolsList.GetStringSelection()
		filePath = os.path.join(translationsDirectory, addonName, self.languageNames[self.languageList.GetSelection()][0], filename)
		# Translators: Message presented when trying to upload a translated file.
		wx.CallAfter(ui.message, _("Uploading file for {language}...").format(language=self.languageList.GetStringSelection()), Spri.NEXT)
		if os.path.isfile(filePath):
			threading.Thread(
				name="UploadTranslatedFile",
				target=uploadTranslatedFile(crowdinFilePath=filename, localFilePath=filePath, language=crowdinLanguage),
					daemon=True,
			).start()
		else:
			# Translators: Message presented when trying to upload a file which doesn't exist.
			ui.message(_("File not found))"))

	def onDownloadForLanguage(self, evt: wx.CommandEvent):
		crowdinLanguage = self._getLanguage()
		# Translators: Message presented when trying to download translations for the selected language.
		wx.CallAfter(ui.message, _("Downloading translations for {language}...").format(language=self.languageList.GetStringSelection()), Spri.NEXT)
		threading.Thread(
			name="DownloadTranslationsForLanguage",
			target=exportTranslations(language=crowdinLanguage),
				daemon=True,
		).start()

	def onDownload(self, evt: wx.CommandEvent):
		# Translators: Message presented when trying to download all translations.
		wx.CallAfter(ui.message, _("Downloading all translations..."), Spri.NEXT)
		threading.Thread(
					name="ExportTranslations",
					target=exportTranslations,
					daemon=True,
				).start()

	def onClose(self, evt: wx.CommandEvent):
		self.Destroy()
		ToolsDialog._instance = None

	def _getLanguage(self) -> str:
		"""Gets the language to be used when downloading translation files.
		:returns: The language used to download translation files.
		"""
		language = self.languageNames[self.languageList.GetSelection()][0]
		crowdinLanguage = languageMappings.get(language, language)
		return crowdinLanguage
