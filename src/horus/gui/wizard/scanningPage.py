#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: October 2014                                                    #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>                    #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 2 of the License, or     #
# (at your option) any later version.                                   #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          #
# GNU General Public License for more details.                          #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with this program. If not, see <http://www.gnu.org/licenses/>.  #
#                                                                       #
#-----------------------------------------------------------------------#

__author__ = "Jesús Arroyo Torrens <jesus.arroyo@bq.com>"
__license__ = "GNU General Public License v2 http://www.gnu.org/licenses/gpl.html"

import wx._core

from horus.gui.wizard.wizardPage import WizardPage

from horus.util import profile

from horus.engine.driver import Driver
from horus.engine.scan import PointCloudGenerator

class ScanningPage(WizardPage):
	def __init__(self, parent, buttonPrevCallback=None, buttonNextCallback=None):
		WizardPage.__init__(self, parent,
							title=_("Scanning"),
							buttonPrevCallback=buttonPrevCallback,
							buttonNextCallback=buttonNextCallback)

		self.driver = Driver.Instance()
		self.pcg = PointCloudGenerator.Instance()

		#TODO: use dictionaries

		value = profile.getProfileSettingInteger('exposure_scanning')
		if value > 25:
			value = _("High")
		elif value > 12:
			value = _("Medium")
		else:
			value = _("Low")
		self.luminosityLabel = wx.StaticText(self.panel, label=_("Luminosity"))
		self.luminosityComboBox = wx.ComboBox(self.panel, wx.ID_ANY,
											value=value,
											choices=[_("High"), _("Medium"), _("Low")],
											style=wx.CB_READONLY)

		value = abs(float(profile.getProfileSetting('step_degrees_scanning')))
		if value > 1.35:
			value = _("Low")
		elif value > 0.625:
			value = _("Medium")
		else:
			value = _("High")
		self.resolutionLabel = wx.StaticText(self.panel, label=_("Resolution"))
		self.resolutionComboBox = wx.ComboBox(self.panel, wx.ID_ANY,
												value=value,
												choices=[_("High"), _("Medium"), _("Low")],
												style=wx.CB_READONLY)

		value = profile.getProfileSetting('use_laser')
		self.laserLabel = wx.StaticText(self.panel, label=_("Laser"))
		self.laserComboBox = wx.ComboBox(self.panel, wx.ID_ANY,
										value=value,
										choices=[_("Use Left Laser"), _("Use Right Laser"), _("Use Both Laser")],
										style=wx.CB_READONLY)

		self.scanTypeLabel = wx.StaticText(self.panel, label=_("Scan Type"))
		value = profile.getProfileSetting('scan_type')
		self.scanTypeComboBox = wx.ComboBox(self.panel, wx.ID_ANY,
											value=value,
											choices=[_("Without Texture"), _("With Texture")],
											style=wx.CB_READONLY)

		self.skipButton.Hide()

		#-- Layout
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.luminosityLabel, 0, wx.ALL^wx.BOTTOM|wx.EXPAND, 18)
		hbox.Add(self.luminosityComboBox, 1, wx.ALL^wx.BOTTOM|wx.EXPAND, 12)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 5)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.resolutionLabel, 0, wx.ALL^wx.BOTTOM|wx.EXPAND, 18)
		hbox.Add(self.resolutionComboBox, 1, wx.ALL^wx.BOTTOM|wx.EXPAND, 12)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 5)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.laserLabel, 0, wx.ALL^wx.BOTTOM|wx.EXPAND, 18)
		hbox.Add(self.laserComboBox, 1, wx.ALL^wx.BOTTOM|wx.EXPAND, 12)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 5)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.scanTypeLabel, 0, wx.ALL^wx.BOTTOM|wx.EXPAND, 18)
		hbox.Add(self.scanTypeComboBox, 1, wx.ALL^wx.BOTTOM|wx.EXPAND, 12)
		vbox.Add(hbox, 0, wx.ALL|wx.EXPAND, 5)
		self.panel.SetSizer(vbox)
		self.Layout()

		self.luminosityComboBox.Bind(wx.EVT_COMBOBOX, self.onLuminosityComboBoxChanged)
		self.resolutionComboBox.Bind(wx.EVT_COMBOBOX, self.onResolutionComboBoxChanged)
		self.laserComboBox.Bind(wx.EVT_COMBOBOX, self.onLaserComboBoxChanged)
		self.scanTypeComboBox.Bind(wx.EVT_COMBOBOX, self.onScanTypeComboBoxChanged)
		self.Bind(wx.EVT_SHOW, self.onShow)

		self.videoView.setMilliseconds(20)
		self.videoView.setCallback(self.getFrame)

	def onShow(self, event):
		if event.GetShow():
			self.updateStatus(self.driver.isConnected)
		else:
			try:
				self.videoView.stop()
			except:
				pass

	def onLuminosityComboBoxChanged(self, event):
		value = event.GetEventObject().GetValue()
		if value ==_("High"):
			value = 32
		elif value ==_("Medium"):
			value = 16
		elif value ==_("Low"):
			value = 8
		profile.putProfileSetting('exposure_scanning', value)
		self.driver.camera.setExposure(value)

	def onResolutionComboBoxChanged(self, event):
		value = event.GetEventObject().GetValue()
		if value ==_("High"):
			value = -0.45
		elif value ==_("Medium"):
			value = -0.9
		elif value ==_("Low"):
			value = -1.8
		profile.putProfileSetting('step_degrees_scanning', value)
		self.pcg.setDegrees(value)

	def onLaserComboBoxChanged(self, event):
		value = event.GetEventObject().GetValue()
		profile.putProfileSetting('use_laser', value)
		useLeft = value == _("Use Left Laser") or value ==_("Use Both Laser")
		useRight = value == _("Use Right Laser") or value ==_("Use Both Laser")
		if useLeft:
			self.driver.board.setLeftLaserOn()
		else:
			self.driver.board.setLeftLaserOff()

		if useRight:
			self.driver.board.setRightLaserOn()
		else:
			self.driver.board.setRightLaserOff()
		self.pcg.setUseLaser(useLeft, useRight)

	def onScanTypeComboBoxChanged(self, event):
		value = event.GetEventObject().GetValue()
		profile.putProfileSetting('scan_type', value)

	def getFrame(self):
		frame = self.driver.camera.captureImage()
		return frame

	def updateStatus(self, status):
		if status:
			profile.putPreference('workbench', 'scanning')
			self.GetParent().parent.workbenchUpdate(False)
			self.videoView.play()
			value = profile.getProfileSetting('use_laser')
			if value ==_("Use Left Laser"):
				self.driver.board.setLeftLaserOn()
				self.driver.board.setRightLaserOff()
			elif value ==_("Use Right Laser"):
				self.driver.board.setLeftLaserOff()
				self.driver.board.setRightLaserOn()
			elif value ==_("Use Both Laser"):
				self.driver.board.setLeftLaserOn()
				self.driver.board.setRightLaserOn()
		else:
			self.videoView.stop()