# -*- coding: utf-8 -*-
# Copyright (c) 2020, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
import datetime, json

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

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def query_location(doctype, txt, searchfield, start, page_len, filters):
  return frappe.db.sql("""select name, place_id, training_place from `tabTraining Place`
    where
      docstatus < 2 and
      name in (select place from `tabPlace Item` where parent = %s and docstatus < 2)
  """, txt)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def query_role(doctype, txt, searchfield, start, page_len, filters):
  return frappe.db.sql("""select name, participant_role_name from `tabParticipant Role`
    where
      docstatus < 2 and
      name in (select participant_role from `tabSession Role Item` where parent = %s and docstatus < 2)
  """, txt)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def query_participant(doctype, txt, searchfield, start, page_len, filters):
  return frappe.db.sql("""select name, first_name, participant_email_id from `tabParticipant`
    where
      docstatus < 2 and
      name in (select participant from `tabSession Role Item` where parent = %s and docstatus < 2)
  """, txt)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def query_device(doctype, txt, searchfield, start, page_len, filters):
  return frappe.db.sql("""select name, alias from `tabDevice`
    where
      docstatus < 2 and
      name in (select device from `tabSession Role Item` where parent = %s and docstatus < 2)
  """, txt)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def query_recipient(doctype, txt, searchfield, start, page_len, filters):
  return frappe.db.sql("""select t1.name, t1.first_name, t1.participant_email_id, t2.participant_role from `tabParticipant` t1 left join `tabSession Role Item` t2 on t1.name=t2.participant where t1.docstatus<2 and t2.docstatus<2 and t2.parent=%s
  """, txt)

@frappe.whitelist()
def submit_pibimessage(doc):
  data = frappe.get_doc("pibiMessage", doc)
  msg = ''
  if data.docstatus == 0:
    msg = frappe.get_doc("pibiMessage", data.name).submit()
    course = frappe.get_doc("Training Course", data.course).save()
    
  return msg

@frappe.whitelist()
def save_actionmessage(doc):
  data = frappe.get_doc("Action Message", doc)
  if data.docstatus < 2:
    data.disabled = 0
    data.save()
  
@frappe.whitelist()
def pause_msg(course, ctable, idn):
  #try:
    print(course, ctable, idn)
    data = frappe.get_doc("Training Course", course)
  
    if ctable == 'schedule':
      for item in data.sch_messages:
        if str(item.idx) == idn:
          print(item.idx, item.sch_message, item.paused)
          if item.paused:
            item.paused = 0
          else:
            item.paused = 1
          break  
           
    elif ctable == 'action':
      for item in data.action_messages:
        if str(item.idx) == idn:
          print(item.idx, item.action_message, item.paused)
          if item.paused:
            item.paused = 0
          else:
            item.paused = 1
          break  
  
    data.save()
    frappe.msgprint(_("Pause Action Settled on Message"))
  #except:
    #pass  
    
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
        time_minutes = 3
        
      if time_minutes >= 2:
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
        time_minutes = 2
        
      if time_minutes >= 1:
        if doc.is_located:
          doc.is_located = False
          doc.last_located = None
          doc.rssi = None
          doc.detected_by = None
          doc.training_place = None
          doc.save()

def update_ongoing_course():
  courses = frappe.get_list(
    doctype = "Training Course",
    fields = ['name'],
    filters = [['docstatus', '<', 2], ['status', '=', "Ongoing"]]
  )
  if courses:
    for course in courses:
      session = frappe.get_doc("Training Course", course).save()

def submit_scheduled_messages():
  """ Get from database on ongoing courses scheduled messages to submit  """
  data = frappe.db.sql("""select t1.sch_message, t1.start_when, timestampdiff(second, now(), t1.start_when) as age, now() from `tabDestination Item` t1 where t1.parent in (select t2.name from `tabTraining Course` t2 where t2.status = 'Ongoing' and t2.docstatus < 2) and t1.docstatus = 0 and t1.paused = 0 and not t1.start_when is NULL and timestampdiff(second, now(), t1.start_when) < 120 and timestampdiff(second, now(), t1.start_when) > -120""", as_dict=True)
  if data:
    for item in data:
      #print(item['sch_message'], item['start_when'], item['age'])
      #doc = frappe.get_doc("pibiMessage", item['sch_message']).submit()
      submit_pibimessage(item['sch_message'])
      #print(doc)       
      
def sync_now():
    from frappe.utils.background_jobs import enqueue
    enqueue('atvirtual.atvirtual.custom.submit_scheduled_messages', timeout=2000, queue="long")