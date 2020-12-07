# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe import _, throw, msgprint
from frappe.utils import nowdate

from frappe.model.document import Document
import six
from six import string_types

class TelegramSettings(Document):
	pass

def validate_receiver_nos(receiver_list):
	validated_receiver_list = []
	for d in receiver_list:
		# remove invalid character
		for x in [' ','-', '(', ')']:
			d = d.replace(x, '')

		validated_receiver_list.append(d)

	if not validated_receiver_list:
		throw(_("Please enter valid mobile nos"))

	return validated_receiver_list

@frappe.whitelist()
def send_telegram(receiver_list, msg, sender_name = '', success_msg = True):

	import json
	if isinstance(receiver_list, string_types):
		receiver_list = json.loads(receiver_list)
		if not isinstance(receiver_list, list):
			receiver_list = [receiver_list]

	receiver_list = validate_receiver_nos(receiver_list)

	arg = {
		'receiver_list' : receiver_list,
		'message'		: frappe.safe_decode(msg).encode('utf-8'),
		'success_msg'	: success_msg
	}

	if frappe.db.get_value('Telegram Settings', None, 'telegram_gateway_url'):
		send_via_gateway(arg)
	else:
		msgprint(_("Please Update Telegram Settings"))

def send_via_gateway(arg):
	ss = frappe.get_doc('Telegram Settings', 'Telegram Settings')
	headers = get_headers(ss)

	args = {ss.message_parameter: arg.get('message')}
	for d in ss.get("parameters"):
		if not d.header:
			args[d.parameter] = d.value

	success_list = []
	for d in arg.get('receiver_list'):
		args[ss.receiver_parameter] = d
		status = send_request(ss.telegram_gateway_url, args, headers, ss.use_post)

		if 200 <= status < 300:
			success_list.append(d)

	if len(success_list) > 0:
		args.update(arg)
		create_telegram_log(args, success_list)
		if arg.get('success_msg'):
			frappe.msgprint(_("Telegram sent to following numbers: {0}").format("\n" + "\n".join(success_list)))

def get_headers(telegram_settings=None):
	if not telegram_settings:
		telegram_settings = frappe.get_doc('Telegram Settings', 'Telegram Settings')

	headers={'Accept': "text/plain, text/html, */*"}
	for d in telegram_settings.get("parameters"):
		if d.header == 1:
			headers.update({d.parameter: d.value})

	return headers

def send_request(gateway_url, params, headers=None, use_post=False):
	import requests

	if not headers:
		headers = get_headers()

	if use_post:
		response = requests.post(gateway_url, headers=headers, data=params)
	else:
		response = requests.get(gateway_url, headers=headers, params=params)
	response.raise_for_status()
	return response.status_code


# Create Telegram Log
# =========================================================
def create_telegram_log(args, sent_to):
	sl = frappe.new_doc('Telegram Log')
	sl.sent_on = nowdate()
	sl.message = args['message'].decode('utf-8')
	sl.no_of_requested_telegram = len(args['receiver_list'])
	sl.requested_numbers = "\n".join(args['receiver_list'])
	sl.no_of_sent_telegram = len(sent_to)
	sl.sent_to = "\n".join(sent_to)
	sl.flags.ignore_permissions = True
	sl.save()