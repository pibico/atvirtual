# -*- coding: utf-8 -*-
# Copyright (c) 2021, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

import json, time, datetime
from frappe import msgprint, _

class StandardMessage(Document):
  def validate(self):
    """
    if not self.location and not self.role and not self.participant and not self.device:
      frappe.throw(_("You must select the message category"))
    """  
    if not self.std_message and not self.config and not self.is_command:
      frappe.throw(_("You must fill a text or config or command message"))
    if self.config and not self.wifi_config:
      frappe.throw(_("You must fill a config message"))
    if self.is_command and not self.order:
      frappe.throw(_("You must fill a command"))
    if self.email and not self.email_account:
      frappe.throw(_("You must fill the Sending Email Address"))
    """
    if self.location:
      if self.role or self.participant or self.device:
        self.role = 0
        self.participant = 0
        self.device = 0
        frappe.throw(_("Once selected location, rest are not selectable"))
    if self.role and not self.location:
      if self.participant or self.device:
        self.participant = 0
        self.device = 0
        frappe.throw(_("Once selected role, rest are not selectable"))
    if self.participant and not self.location and not self.role:
      if self.device:
        self.device = 0
        frappe.throw(_("Once selected participant, rest are not selectable"))
    if self.config:
      self.location = 0
      self.role = 0
      self.participant = 0
      if not self.device:
        self.device = 1
        frappe.throw(_("Configuration Messages are only sent to devices"))
    """
    if self.is_special:
      if not self.special_json:
        frappe.throw(_("You must indicate the special effect"))
        
  def before_save(self):
    ## Prepare json message
    json_message = {}
    """
    ## Fill message type
    if self.location:
      json_message['type'] = "location"
    elif self.role:
      json_message['type'] = "role"
    elif self.participant:
      json_message['type'] = "participant"
    elif self.device:
      json_message['type'] = "device"
    """
    ## Fill light section
    if self.light_rgb:
      light = {}
      rgb = frappe.get_doc("Light RGB", self.light_rgb)
      light['rgb'] = "(" + str(rgb.red) + "," + str(rgb.green) + "," + str(rgb.blue) + ")"
      light['lDur'] = self.light_sec
      light['bright'] = self.brightness
      json_message['light'] = light
    ## Fill sound section
    if self.sound_wav:
      sound = {}
      wav = frappe.get_doc("Sound WAV", self.sound_wav)
      if self.overwrite_sound:
        sound['overwrite_sound'] = True
      sound['wav'] = frappe.utils.get_url() + wav.sound_wav
      sound['sDur'] = self.sound_sec
      sound['volume'] = self.volume
      json_message['sound'] = sound
    ## Fill latency
    if self.latency:
      json_message['latency'] = self.latency
    ## Fill text section
    if self.std_message:
      message = {}
      message['text'] = self.std_message
      message['tDur'] = self.text_sec
      message['contrast'] = self.contrast
      json_message['message'] = message
    ## Fill time section
    if self.time_set or self.start_crono or self.timer_from != "0:00:00":
      strtime = {}
      if self.time_set:
        strtime['timeSet'] = str(datetime.datetime.strptime(self.time_set, "%Y-%m-%d %H:%M:%S"))
      if self.start_crono:
        strtime['crono'] = self.start_crono
      if self.stop_crono:
          strtime['stop_crono'] = self.stop_crono
      if self.timer_from != "0:00:00":
        strtime['timer'] = self.timer_from  
      json_message['time'] = strtime
    ## Fill config wifi section
    if self.config:
      if self.wifi_config:
        json_message['wifi_config'] =  self.wifi_config
      else:
        json_message['wifi_config'] = ""
    ## Fill email section
    if self.email:
      email = {}
      email['email_account'] = self.email_account
      email['subject'] = self.subject
      email['body'] = self.std_message
      json_message['email'] = email
    ## Fill command section
    if self.is_command:
      command = {}
      command['is_command'] = 1
      command['order'] = self.order
      if self.command_args:
        command['cArgs'] = self.command_args
      json_message['command'] = command
    ## Fill special effects section
    if self.is_special:
      json_message['effects'] = self.special_json
    ## save json
    self.json_message = json.dumps(json_message)