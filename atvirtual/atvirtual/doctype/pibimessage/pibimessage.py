# -*- coding: utf-8 -*-
# Copyright (c) 2020, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import datetime, time

from frappe.utils import cstr
from frappe import msgprint, _
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from atvirtual.atvirtual.doctype.telegram_settings.telegram_settings import send_telegram
import paho.mqtt.client as mqtt
import os, ssl, urllib, json
from frappe.utils.password import get_decrypted_password

class pibiMessage(Document):
  def validate(self):
    if self.message_type == "IoT" and not self.std_message:
      frappe.throw(_("Please fill the message content"))
    
  def before_save(self):
    if self.message_type == "IoT":
      std_message = frappe.get_doc("Standard Message", self.std_message)
    
  def before_submit(self):
    ## Prepare recipients list
    sms_list = []
    telegram_list = []
    mqtt_list = []
    str_attach = ''
    recipients = []
    
    ## Send E-mails
    if self.message_type == "E-mail":
      ## Read message body
      message = self.email_body
      ## Read Recipients Table
      recipient_list = self.recipient_item
      if len(recipient_list) > 0:
        for item in recipient_list:
          recipients.append(item.participant_email_id)
      ## Read and prepare message with Attachments
      if len(self.message_item) > 0:
        for idx, row in enumerate(self.message_item):
          if "http" in row.attachment:
            str_attach = str_attach + '<a href="' + row.attachment + '">Anexo ' +str(idx+1) + ': ' + row.description + '</a><br>'
          else:   
            str_attach = str_attach + '<a href="' + frappe.utils.get_url() + urllib.parse.quote(row.attachment) + '">Anexo ' +str(idx+1) + ': ' + row.description + '</a><br>'
        message = message + "<p>Con archivos anexos:</p><p>" + str_attach + "</p>"
      ## Finally Send message by Email
      email_args = {
        "sender": self.from_email_account,
        "recipients": recipients,
        "message": message,
        "subject": self.subject,
        "reference_doctype": self.doctype,
        "reference_name": self.name
      }
      frappe.sendmail(**email_args)
      frappe.msgprint(_("Email sent to ") + str(recipients))
    
    ## Send IoT messages
    if self.message_type == "IoT":
      ## Read main message
      dict_message = json.loads(self.message_text)
      str_message = dict_message["message"]["text"]
      ## Read and prepare message with attachments 
      if len(self.message_item) > 0:
        for idx, row in enumerate(self.message_item):
          if "http" in row.attachment:
            str_attach = str_attach + 'Anexo ' + str(idx+1) + ': ' + row.description + ' @ ' + row.attachment + '\n' 
          else:   
            str_attach = str_attach + 'Anexo ' + str(idx+1) + ': ' + row.description + ' @ ' + frappe.utils.get_url() + urllib.parse.quote(row.attachment) + '\n'
        str_message = str_message + "\nCon archivos anexos:\n" + str_attach
        dict_message["message"]["text"] = str_message
      ## Prepare location recipients
      if len(self.location_table) > 0:
        for loc in self.location_table:
          sms_list, mqtt_list, telegram_list = append_recipients(loc.device, sms_list, mqtt_list, telegram_list)
      ## Prepare device recipients
      if len(self.device_table) > 0:
        for dev in self.device_table:
          sms_list, mqtt_list, telegram_list = append_recipients(dev.device, sms_list, mqtt_list, telegram_list)
      ## Prepare role recipients    
      if len(self.recipient_table) > 0:
        for rol in self.recipient_table:
          frappe.msgprint(rol.participant_role)
          """ Get from database devices ported in session """
          roldev = frappe.db.sql("""SELECT device FROM `tabSession Role Item` WHERE parent=%s AND participant_role=%s and docstatus < 2""", (self.course, rol.participant_role), True)
          if len(roldev) > 0:
            for itm in roldev:
              sms_list, mqtt_list, telegram_list = append_recipients(itm.device, sms_list, mqtt_list, telegram_list)
      ## Prepare participants           
      if len(self.participant_table) > 0:
        for per in self.participant_table:
          frappe.msgprint(per.participant)
          """ Get from database devices ported in session """
          perdev = frappe.db.sql("""SELECT device FROM `tabSession Role Item` WHERE parent=%s AND participant=%s and docstatus < 2""", (self.course, per.participant), True)
          if len(perdev) > 0:
            for per in perdev: 
              sms_list, mqtt_list, telegram_list = append_recipients(per.device, sms_list, mqtt_list, telegram_list) 
     
      ## Send message by MQTT
      if len(mqtt_list) > 0:
        path = frappe.utils.get_bench_path()
        site_name = frappe.utils.get_url().replace("http://","").replace("https://","")
        if ":" in site_name:
          pos = site_name.find(":")
          site_name = site_name[:pos]

        client = frappe.get_doc('MQTT Settings', 'MQTT Settings')
        server = client.broker_gateway
        port = client.port
        user = client.user
        client.secret = get_decrypted_password('MQTT Settings', 'MQTT Settings', 'secret', False)
        secret = client.secret
        do_ssl = client.is_ssl
        # connect to MQTT Broker to Publish Message
        pid = os.getpid()
        client_id = '{}:{}'.format('client', str(pid))
        try:
          backend = mqtt.Client(client_id=client_id, clean_session=True)
          backend.username_pw_set(user, password=secret)
          if do_ssl == True:
            ca = os.path.join(path, "sites", site_name, frappe.get_site_path('private', 'files', client.ca)[1:])
            client_crt = os.path.join(path, "sites", site_name, frappe.get_site_path('private', 'files', client.client_crt)[1:])
            client_key = os.path.join(path, "sites", site_name, frappe.get_site_path('private', 'files', client.client_key)[1:])
            port_ssl = client.ssl_port
            ## Prepare mqtt    
            backend.tls_set(ca_certs=ca, certfile=client_crt, keyfile=client_key, cert_reqs=ssl.CERT_REQUIRED, ciphers=None)
            backend.tls_insecure_set(False)
            time.sleep(.5)
            backend.connect(server, port_ssl)
          else:  
            backend.connect(server, port)

          payload = frappe.safe_decode(json.dumps(dict_message)).encode('utf-8')
          for dev in mqtt_list:
            mqtt_topic = str(dev) + "/mqtt"
            backend.publish(mqtt_topic, cstr(payload))
          backend.disconnect()
        except:
          frappe.msgprint(_("Error in MQTT Broker sending to ", str(mqtt_list)))
          pass
      ## Send message by Telegram
      if len(telegram_list) > 0:
        try:
          send_telegram(telegram_list, cstr(str_message))
        except:
          pass 
      ## Send message by SMS
      if len(sms_list) > 0  and self.message_type == "IoT":
        try:
          send_sms(sms_list, cstr(str_message))
        except:
          pass
      ## Final Message
      frappe.msgprint(_("Actions Completed and Messages Sent"))

def append_recipients(device, sms_list, mqtt_list, telegram_list):
  doc = frappe.get_doc('Device', device)
  if not doc.disabled:
    if doc.is_connected and doc.alerts_active:
      if doc.by_sms:
        if doc.sms_number != '':
          if not doc.sms_number in sms_list:
            sms_list.append(doc.sms_number)
            #frappe.msgprint(_("Message by sms to ") + str(doc.sms_number))
      if doc.by_text:
        if doc.device_name != '' and doc.by_mqtt and not doc.device_name in mqtt_list:
          mqtt_list.append(doc.device_name)
          #frappe.msgprint(_("Message by mqtt to ") + str(doc.device_name))
        elif not doc.by_mqtt:
          if doc.sms_number != '' and not doc.sms_number in sms_list:
            sms_list.append(doc.sms_number)  
            #frappe.msgprint(_("Message by sms to ") + str(doc.sms_number))  
      if doc.by_telegram:
        if doc.telegram_number != '':
          if not doc.telegram_number in telegram_list:
            telegram_list.append(doc.telegram_number)
            #frappe.msgprint(_("Message by sms to ") + str(doc.telegram_number))
  return sms_list, mqtt_list, telegram_list