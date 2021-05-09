# -*- coding: utf-8 -*-
# Copyright (c) 2021, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe import _

class ControlPanel(WebsiteGenerator):
  def get_context(self, context):
    context.devices = frappe.get_all("Device",
      fields=["*"],
      filters=[["control_panel", "=", self.name], ["docstatus", "<", 2]],
      order_by="creation desc",
      limit_page_length=20)

    # check permissions
    if frappe.session.user == "Guest":
      frappe.throw(_("You need to be logged in to access this {0}.").format(self.doc_type), frappe.PermissionError)
