# -*- coding: utf-8 -*-
# Copyright (c) 2020, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Device(Document):
  def on_update(self):
    ## Update Training Course Is Connected, Is Located and related fields
    """ Get from database course assigned to a device not yet returned
    """
    course = frappe.db.sql("""
		  SELECT * FROM `tabSession Role Item` WHERE NOT assigned_date IS NULL AND returned_date IS NULL AND   device = %s AND docstatus < 2
      """,self.name, True)
    if course:  
      course_device = frappe.get_doc("Training Course", course[0].parent)
      ## Update existing child row
      for row in course_device.get('participants'):
        if row.name == course[0].name:
          row.is_connected =  self.is_connected
          row.is_located = self.is_located
          row.training_place = self.training_place
          row.rssi = self.rssi
          row.detected_by = self.detected_by
          row.save()  
          course_device.save()
          frappe.db.commit()
    
    """ Get from database course assigned to a device for a location
    """
    place = frappe.db.sql("""
		  SELECT * FROM `tabPlace Item` WHERE device = %s AND docstatus < 2
      """,self.name, True)
    if place:
      place_device = frappe.get_doc("Training Course", place[0].parent)  
      ## Update existing child item
      for item in place_device.get('items'):
        if item.name == place[0].name:
          item.is_connected = self.is_connected
          item.save()
          place_device.save()
          frappe.db.commit()