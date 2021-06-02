# -*- coding: utf-8 -*-
# Copyright (c) 2021, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import datetime, time

from frappe.utils import cstr
from frappe import msgprint, _
import paho.mqtt.client as mqtt
import os, ssl, urllib, json
from frappe.utils.password import get_decrypted_password

class ActionMessage(Document):
  def before_save(self):
    std_message = frappe.get_doc("Standard Message", self.std_message)
    ## Prepare recipients list
    mqtt_list = []
    str_message = ""
    
    ## Send IoT messages
    if not self.disabled:
      ## Read main message
      dict_message = json.loads(self.message_text)
      if "message" in dict_message:
        str_message = dict_message["message"]["text"]
      ## Prepare device recipients
      if len(self.device_table) > 0:
        for dev in self.device_table:
          mqtt_list = append_actions(dev.device, mqtt_list)
     
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
            mqtt_topic = str(dev) + "/display/text"
            backend.publish(mqtt_topic, cstr(payload))
          backend.disconnect()
        except:
          frappe.msgprint(_("Error in MQTT Broker sending to ", str(mqtt_list)))
          pass
    
    ## Final Message
    frappe.msgprint(_("Actions Completed and Messages Sent"))

def append_actions(device, mqtt_list):
  doc = frappe.get_doc('Device', device)
  if not doc.disabled:
    if doc.is_connected and doc.alerts_active:
      if doc.device_name != '' and doc.by_mqtt and not doc.device_name in mqtt_list:
        mqtt_list.append(doc.device_name)
        #frappe.msgprint(_("Message by mqtt to ") + str(doc.device_name))  
  return mqtt_list