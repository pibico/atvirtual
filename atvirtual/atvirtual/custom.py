# -*- coding: utf-8 -*-
# Copyright (c) 2020, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime

@frappe.whitelist()
def get_image(slide):
  """ Get from database all committments amounts from not cancelled Purchase Orders
  on specific Project
  """
  data = frappe.db.sql("""
		SELECT * FROM `tabWebsite Slideshow Item` WHERE  parent=%s and docstatus<2""", slide, True)
  return data

@frappe.whitelist()
def get_fullname(user):
  """ Get from database fullname for user
  """
  data = frappe.db.sql("""
		SELECT full_name FROM `tabUser` WHERE  name=%s and docstatus<2""", user, True)
  return data

@frappe.whitelist()
def get_course_from_device(device):
  """ Get from database course assigned to a device not yet returned
  """
  data = frappe.db.sql("""
		SELECT * FROM `tabSession Role Item` WHERE NOT assigned_date IS NULL AND returned_date IS NULL AND device = %s AND docstatus < 2
""",(device), True)
  return data
  
@frappe.whitelist()
def get_place_from_device(device):
  """ Get from database course assigned to a device assigned to a location
  """
  data = frappe.db.sql("""
		SELECT * FROM `tabPlace Item` AS t1 INNER JOIN `tabTraining Course` AS t2 ON t1.parent = t2.name WHERE t2.status != 'Completed' AND t1.device = %s AND t1.docstatus < 2
""",(device), True)
  return data
  
@frappe.whitelist()
def get_places(allow_guest=True):
  """ Get from database places  """
  device = ''
  data = frappe.db.sql("""SELECT t1.parent, t1.place, t1.device FROM `tabPlace Item` AS t1 INNER JOIN `tabTraining Course` AS t2 ON t1.parent = t2.name WHERE t2.status != 'Completed' AND t1.docstatus < 2 and t1.device != %s""", device, True)
  return data

def check_connected_devices():
  devices = frappe.get_list(
    doctype = "Device",
    fields = ['name'],
    filters = [['docstatus', '<', 2], ['disabled', '=', 0], ['is_atvirtual', '=', 1]]
  )
  if devices:
    for device in devices:
      doc = frappe.get_doc("Device", device.name)
      last_seen = doc.last_seen
      now = datetime.datetime.now()
      if last_seen:
        time_minutes = (now - last_seen).total_seconds()/60
      else:
        time_minutes = 6
        
      if time_minutes >= 6:
        if doc.is_connected:
          doc.is_connected = False
          doc.last_seen = None
          doc.ip = None
          doc.wifi_ssid = None
          doc.save()

def check_located_devices():
  devices = frappe.get_list(
    doctype = "Device",
    fields = ['name'],
    filters = [['docstatus', '<', 2], ['disabled', '=', 0], ['is_atvirtual', '=', 1]]
  )
  if devices:
    for device in devices:
      doc = frappe.get_doc("Device", device.name)
      last_located = doc.last_located
      now = datetime.datetime.now()
      if last_located:
        time_minutes = (now - last_located).total_seconds()/60
      else:
        time_minutes = 3
        
      if time_minutes >= 3:
        if doc.is_located:
          doc.is_located = False
          doc.last_located = None
          doc.rssi = None
          doc.detected_by = None
          doc.training_place = None
          doc.save()