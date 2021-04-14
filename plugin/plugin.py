# -*- coding: utf-8 -*-

###########################################
# maintainer: <plnick@vuplus-support.org> #
##    http://www.vuplus-support.org      ##
###########################################

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.

# camera icon is taken from oxygen icon theme for KDE 4

from enigma import eActionMap, eConsoleAppContainer
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigSelection, ConfigEnableDisable, ConfigYesNo, ConfigInteger
from Components.Console import Console
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.Notifications import AddNotification
from Tools.BoundFunction import boundFunction
from datetime import datetime
from time import time as systime
from os import system, path, mkdir, makedirs
from __init__ import _

pluginversion = "Version: 0.2"
config.plugins.shootyourscreen = ConfigSubsection()
config.plugins.shootyourscreen.enable = ConfigEnableDisable(default=True)
config.plugins.shootyourscreen.switchhelp = ConfigYesNo(default=True)
config.plugins.shootyourscreen.path = ConfigSelection(default="/media/hdd", choices=[("/media/hdd"), ("/media/usb"), ("/media/hdd1"), ("/media/usb1"), ("/tmp", "/tmp")])
config.plugins.shootyourscreen.pictureformat = ConfigSelection(default="jpg", choices=[("", "bmp"), ("-j", "jpg"), ("-p", "png")])
config.plugins.shootyourscreen.jpegquality = ConfigSelection(default="100", choices=[("10"), ("20"), ("40"), ("60"), ("80"), ("100")])
config.plugins.shootyourscreen.picturetype = ConfigSelection(default="all", choices=[("all", "OSD + Video"), ("-v", "Video"), ("-o", "OSD")])
config.plugins.shootyourscreen.picturesize = ConfigSelection(default="default", choices=[("default", _("Skin resolution")), ("-r 480", "480"), ("-r 576", "576"), ("-r 720", "720"), ("-r 1280", "1280"), ("-r 1920", "1920")])
config.plugins.shootyourscreen.timeout = ConfigSelection(default="3", choices=[("1", "1 sec"), ("3", "3 sec"), ("5", "5 sec"), ("10", "10 sec"), ("off", _("no message")), ("0", _("no timeout"))])


def getPicturePath():
	picturepath = config.plugins.shootyourscreen.path.value
	if picturepath.endswith('/'):
		picturepath = picturepath + 'screenshots'
	else:
		picturepath = picturepath + '/screenshots'

	try:
		if (path.exists(picturepath) == False):
			makedirs(picturepath)
	except OSError:
		self.session.open(MessageBox, _("Sorry, your device for screenshots is not writeable.\n\nPlease choose another one."), MessageBox.TYPE_INFO, timeout=10)
	return picturepath


class getScreenshot:
	def __init__(self):
		self.ScreenshotConsole = Console()
		self.previousflag = 0
		eActionMap.getInstance().bindAction('', -0x7FFFFFFF, self.screenshotKey)

	def screenshotKey(self, key, flag):
		if config.plugins.shootyourscreen.enable.value:
			if key == 138:
				if not config.plugins.shootyourscreen.switchhelp.value:
					if flag == 3:
						self.previousflag = flag
						self.grabScreenshot()
						return 1
					if self.previousflag == 3 and flag == 1:
						self.previousflag = 0
						return 1
				else:
					if flag == 0:
						return 1
					if flag == 3:
						self.previousflag = flag
						return 0
					if flag == 1 and self.previousflag == 0:
						self.grabScreenshot()
						return 1
					if self.previousflag == 3 and flag == 1:
						self.previousflag = 0
						return 0
		return 0

	def grabScreenshot(self, ret=None):
		filename = self.getFilename()
		print "[ShootYourScreen] grab screenshot to %s" % filename
		cmd = "grab"
		if not config.plugins.shootyourscreen.picturetype.value == "all":
			cmdoptiontype = " " + str(config.plugins.shootyourscreen.picturetype.value)
			cmd += cmdoptiontype
		if not config.plugins.shootyourscreen.picturesize.value == "default":
			cmdoptionsize = " " + str(config.plugins.shootyourscreen.picturesize.value)
			cmd += cmdoptionsize
		cmdoptionformat = " " + str(config.plugins.shootyourscreen.pictureformat.value)
		cmd += cmdoptionformat
		if config.plugins.shootyourscreen.pictureformat.getText() == "jpg":
			cmdoptionquality = " " + str(config.plugins.shootyourscreen.jpegquality.value)
			cmd += cmdoptionquality
		cmd += " -s -q"
		extra_args = (filename)
		self.ScreenshotConsole.ePopen(cmd, self.gotScreenshot, extra_args)

	def gotScreenshot(self, data, retval, extra_args=None):
		if extra_args is not None:
			filename = extra_args
		else:
			filename = ""
		
		if not config.plugins.shootyourscreen.timeout.value == "off":
			messagetimeout = int(config.plugins.shootyourscreen.timeout.value)
			error = False
			if retval == 0 and filename:
				try:
					with open(filename, "wb") as file:
						file.write(data)
					msg_text = _("Screenshot successfully saved as:\n%s") % filename
					msg_type = MessageBox.TYPE_INFO
				except Exception, e:
					print "[ShootYourScreen] Error creating file", e
					error = True
			else:
				error = True
			if error:
				msg_text = _("Grabbing Screenshot failed !!!")
				msg_type = MessageBox.TYPE_ERROR
			AddNotification(MessageBox, msg_text, MessageBox.TYPE_INFO, timeout=messagetimeout)
		else:
			pass

	def getFilename(self):
		now = systime()
		now = datetime.fromtimestamp(now)
		now = now.strftime("%Y-%m-%d_%H-%M-%S")

		screenshottime = "screenshot_" + now
		
		if config.plugins.shootyourscreen.pictureformat.getText() == "bmp":
			fileextension = ".bmp"
		elif config.plugins.shootyourscreen.pictureformat.getText() == "jpg":
			fileextension = ".jpg"
		elif config.plugins.shootyourscreen.pictureformat.getText() == "png":
			fileextension = ".png"

		picturepath = getPicturePath()
		if picturepath.endswith('/'):
			screenshotfile = picturepath + screenshottime + fileextension
		else:
			screenshotfile = picturepath + '/' + screenshottime + fileextension
		return screenshotfile


class ShootYourScreenConfig(Screen, ConfigListScreen):
	skin = """
		<screen position="center,center" size="650,400" title="ShootYourScreen for VU+" >
		<widget name="config" position="10,10" size="630,350" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ShootYourScreen/pic/button_red.png" zPosition="2" position="10,370" size="25,25" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ShootYourScreen/pic/button_green.png" zPosition="2" position="130,370" size="25,25" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ShootYourScreen/pic/button_yellow.png" zPosition="2" position="270,370" size="25,25" alphatest="on" />
		<widget name="key_red" position="40,372" size="100,20" valign="center" halign="left" zPosition="2" foregroundColor="white" font="Regular;18"/>
		<widget name="key_green" position="160,372" size="100,20" valign="center" halign="left" zPosition="2" foregroundColor="white" font="Regular;18"/>
		<widget name="key_yellow" position="300,372" size="100,20" valign="center" halign="left" zPosition="2" foregroundColor="white" font="Regular;18"/>
		</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		
		self.createConfigList()

		ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)

		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Save"))
		self["key_yellow"] = Label(_("Default"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"green": self.keyGreen,
				"red": self.cancel,
				"yellow": self.revert,
				"cancel": self.cancel,
				"ok": self.keyGreen,
			}, -2)
			
		self.onShown.append(self.setWindowTitle)

	def setWindowTitle(self):
		self.setTitle(_("ShootYourScreen for VU+ STB - %s") % pluginversion)

	def createConfigList(self):
		self.list = []
		self.list.append(getConfigListEntry(_("Enable ShootYourScreen :"), config.plugins.shootyourscreen.enable))
		if config.plugins.shootyourscreen.enable.value == True:
			self.list.append(getConfigListEntry(_("Screenshot of :"), config.plugins.shootyourscreen.picturetype))
			self.list.append(getConfigListEntry(_("Format for screenshots :"), config.plugins.shootyourscreen.pictureformat))
			if config.plugins.shootyourscreen.pictureformat.getText() == "jpg":
				self.list.append(getConfigListEntry(_("Quality of jpg picture :"), config.plugins.shootyourscreen.jpegquality))
			self.list.append(getConfigListEntry(_("Picture size (width) :"), config.plugins.shootyourscreen.picturesize))
			self.list.append(getConfigListEntry(_("Path for screenshots :"), config.plugins.shootyourscreen.path))
			self.list.append(getConfigListEntry(_("Switch Help and Help long button :"), config.plugins.shootyourscreen.switchhelp))
			self.list.append(getConfigListEntry(_("Timeout for info message :"), config.plugins.shootyourscreen.timeout))

	def changedEntry(self):
		self.createConfigList()
		self["config"].setList(self.list)

	def save(self):
		for x in self["config"].list:
			x[1].save()
		self.changedEntry()

	def keyGreen(self):
		self.save()
		self.close(False, self.session)

	def cancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"), MessageBox.TYPE_YESNO, default=True)
		else:
			for x in self["config"].list:
				x[1].cancel()
			self.close(False, self.session)

	def cancelConfirm(self, result):
		if result is None or result is False:
			print "[ShootYourScreen] Cancel not confirmed."
		else:
			print "[ShootYourScreen] Cancel confirmed. Configchanges will be lost."
			for x in self["config"].list:
				x[1].cancel()
			self.close(False, self.session)

	def revert(self):
		self.session.openWithCallback(self.keyYellowConfirm, MessageBox, _("Reset ShootYourScreen settings to defaults?"), MessageBox.TYPE_YESNO, timeout=20, default=True)

	def keyYellowConfirm(self, confirmed):
		if not confirmed:
			print "[ShootYourScreen] Reset to defaults not confirmed."
		else:
			print "[ShootYourScreen] Setting Configuration to defaults."
			config.plugins.shootyourscreen.enable.setValue(1)
			config.plugins.shootyourscreen.switchhelp.setValue(1)
			config.plugins.shootyourscreen.path.setValue("/media/hdd")
			config.plugins.shootyourscreen.pictureformat.setValue("-j")
			config.plugins.shootyourscreen.jpegquality.setValue("100")
			config.plugins.shootyourscreen.picturetype.setValue("all")
			config.plugins.shootyourscreen.picturesize.setValue("default")
			config.plugins.shootyourscreen.timeout.setValue("3")
			self.save()


def autostart(reason, **kwargs):
	if kwargs.has_key("session") and reason == 0:
		print "[ShootYourScreen] start...."
		getScreenshot()


def startSetup(session, **kwargs):
		print "[ShootYourScreen] start configuration"
		session.open(ShootYourScreenConfig)


def Plugins(**kwargs):
			return [PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=autostart),
				PluginDescriptor(name="ShootYourScreen Setup", description=_("make Screenshots with your VU+"), where=[PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU], icon="shootyourscreen.png", fnc=startSetup)]
