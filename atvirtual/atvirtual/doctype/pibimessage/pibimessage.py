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
import os, ssl
from frappe.utils.password import get_decrypted_password

class pibiMessage(Document):
  def autoname(self):
    """ Naming Messages from Current DateTime and Role """
    self.name = datetime.datetime.strftime(datetime.datetime.now(), "%y%m%d %H%M") + "_" + self.participant_role
 
  def before_save(self):
    sms_list = []
    telegram_list = []
    mqtt_list = []
    if self.device == '':
      if self.participant_role != "" and self.course != "":
        """ Get from database devices ported by user in session """
        devices = frappe.db.sql("""SELECT device FROM `tabSession Role Item` WHERE parent=%s AND participant_role=%s and docstatus < 2""", (self.course, self.participant_role), True) 
        for item in devices:
          doc = frappe.get_doc('Device', item.device)
          if not doc.disabled:
            if doc.is_connected and not doc.is_scanner and doc.alerts_active:
              if doc.by_sms:
                if doc.sms_number != '':
                  sms_list.append(doc.sms_number)
                  #frappe.msgprint(_("Message by sms to ") + str(doc.sms_number))
              if doc.by_text:
                if doc.device_name != '' and doc.by_mqtt:
                  mqtt_list.append(doc.device_name)
                  #frappe.msgprint(_("Message by mqtt to ") + str(doc.device_name))
                elif not doc.by_mqtt:
                  if doc.sms_number != '' and not doc.sms_number in sms_list:
                    sms_list.append(doc.sms_number)  
                    #frappe.msgprint(_("Message by sms to ") + str(doc.sms_number))
              if doc.by_telegram:
                if doc.telegram_number != '':
                  telegram_list.append(doc.telegram_number)
                  #frappe.msgprint(_("Message by sms to ") + str(doc.telegram_number))
    else:
      doc = frappe.get_doc('Device', self.device)
      if not doc.disabled:
        if doc.is_connected and not doc.is_scanner and doc.alerts_active:
          if doc.by_sms:
            if doc.sms_number != '':
              if not doc.sms_number in sms_list:
                sms_list.append(doc.sms_number)
                #frappe.msgprint(_("Message by sms to ") + str(doc.sms_number))
          if doc.by_text:
            if doc.device_name != '' and doc.by_mqtt:
              mqtt_list.append({"name": doc.device_name})
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
      
    if self.message_type == "Text":
      message = "From AT Virtual: " + self.message_text
    elif self.message_type == "Photo":
      message = "Photo from AT Virtual \n" + frappe.utils.get_url() + ":8080" + self.message_photo
    elif self.message_type == "Video":
      message = "Video from AT Virtual \n" + frappe.utils.get_url() + ":8080" + self.message_video

    if len(sms_list) > 0:
      try:
        send_sms(sms_list, cstr(message))
        #frappe.msgprint(_("Message by sms to: " + str(sms_list) + " " + message))
      except:
        pass
    if len(mqtt_list) > 0:
      path = "/home/erpnext/erpnext-prd/sites/" 
      client = frappe.get_doc('MQTT Settings', 'MQTT Settings')
      server = client.broker_gateway
      port = client.port
      user = client.user
      client.secret = get_decrypted_password('MQTT Settings', 'MQTT Settings', 'secret', False)
      secret = client.secret
      do_ssl = client.is_ssl
      ca = path + frappe.utils.get_url().replace("http://","") + client.ca
      client_crt = path + frappe.utils.get_url().replace("http://","") + client.client_crt
      client_key = path + frappe.utils.get_url().replace("http://","") + client.client_key
      port_ssl = client.ssl_port
      #frappe.msgprint(frappe.get_site_path('private', 'files', 'ca.crt').replace("./","/")
      # connect to MQTT Broker to Publish Message
      pid = os.getpid()
      client_id = '{}:{}'.format('client', str(pid))
      try:
        backend = mqtt.Client(client_id=client_id, clean_session=True)
        backend.username_pw_set(user, password=secret)
        if do_ssl == True:
          backend.tls_set(ca_certs=ca, certfile=client_crt, keyfile=client_key, cert_reqs=ssl.CERT_REQUIRED, ciphers=None)
          backend.tls_insecure_set(False)
          time.sleep(.5)
          backend.connect(server, port_ssl)
        else:  
          backend.connect(server, port)

        payload = cstr(message)
        for dev in mqtt_list:
          mqtt_topic = dev['name'] + "/mqtt"
          backend.publish(mqtt_topic, payload)
        backend.disconnect()
        #frappe.msgprint(_("Message by mqtt to: " + str(mqtt_list)))
      except:
        frappe.msgprint(_("Error in MQTT Broker", str(mqtt_list)))
        #raise
        pass
    if len(telegram_list) > 0:
      try:
        send_telegram(telegram_list, cstr(message))
        #frappe.msgprint(_("Message by telegram to: " + str(telegram_list) + " " + message))
      except:
        pass 