# -*- coding: utf-8 -*-
# Copyright (c) 2020, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe import _

class TrainingCourse(WebsiteGenerator):
  def get_context(self, context):
    context.pibimessages = frappe.get_all("pibiMessage",
      fields=["*"],
      filters=[["course", "=", self.name], ["docstatus", "<", 2]],
      order_by="creation desc",
      limit_page_length=20)

    # check permissions
    if frappe.session.user == "Guest":
      frappe.throw(_("You need to be logged in to access this {0}.").format(self.doc_type), frappe.PermissionError)  

def get_timeline_data(doctype, name):
	'''Return timeline for messages'''
	return dict(frappe.db.sql('''select unix_timestamp(creation), count(*) from `tabpibiMessage` where course=%s and creation > date_sub(curdate(), interval 1 year) and docstatus < 2 group by date(creation)''', name))
 
