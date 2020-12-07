# -*- coding: utf-8 -*-
# Copyright (c) 2020, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

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