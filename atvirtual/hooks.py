# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "atvirtual"
app_title = "Atvirtual"
app_publisher = "PibiCo"
app_description = "AT Virtual Project"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "pibico.sl@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/atvirtual/css/atvirtual.css"
# app_include_js = "/assets/atvirtual/js/atvirtual.js"

# include js, css files in header of web template
# web_include_css = "/assets/atvirtual/css/atvirtual.css"
# web_include_js = "/assets/atvirtual/js/atvirtual.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "atvirtual.utils.get_home_page"

brand_html = '<div><img width="27px" src="/assets/atvirtual/assets/images/logo-icon.png"> pib<small><strong>INSTRUCTOR</strong></small></div>'

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "atvirtual.install.before_install"
# after_install = "atvirtual.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "atvirtual.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"atvirtual.tasks.all"
# 	],
# 	"daily": [
# 		"atvirtual.tasks.daily"
# 	],
# 	"hourly": [
# 		"atvirtual.tasks.hourly"
# 	],
# 	"weekly": [
# 		"atvirtual.tasks.weekly"
# 	]
# 	"monthly": [
# 		"atvirtual.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "atvirtual.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "atvirtual.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "atvirtual.task.get_dashboard_data"
# }

fixtures = ['Report', 'Role Profile', 'Role', 'Custom Field', 'Custom Script', 'Property Setter', 'Workflow', 'Workflow State', 'Workflow Action', 'Translation', 'Website Settings']