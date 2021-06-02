from __future__ import unicode_literals
from frappe import _

def get_data():
  return [
    {
      "label": _("AT-Virtual Project"),
      "icon": "fa fa-star",
      "items": [
        {
          "type": "doctype",
          "name": "Training Course",
          "description": _("Training Course"),
          "onboard": 1,
        },    
        {
          "type": "doctype",
          "name": "pibiMessage",
          "description": _("Intelligent Message"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Action Message",
          "description": _("Action Message"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Standard Message",
          "description": _("Standard Message"),
          "onboard": 1,
        }          
      ]
    },
    {
      "label": _("AT-Virtual People"),
      "icon": "fa fa-star",
      "items": [
        {
          "type": "doctype",
          "name": "Participant",
          "description": _("Participant"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Participant Role",
          "description": _("Participant Role"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Session Type",
          "description": _("Session Type"),
          "onboard": 1,
        }         
      ]
    },
    {
      "label": _("AT-Virtual Equipment"),
      "icon": "fa fa-star",
      "items": [
        {
          "type": "doctype",
          "name": "Device",
          "description": _("Message Device"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Device Type",
          "description": _("Device Type"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Training Place",
          "description": _("Training Places"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Control Panel",
          "description": _("Control Panel"),
          "onboard": 1,
        }    
      ]
    },
    {
      "label": _("AT-Virtual Channels"),
      "icon": "fa fa-star",
      "items": [
        {
          "type": "doctype",
          "name": "Email Account",
          "description": _("Email Account"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "SMS Settings",
          "description": _("SMS Settings"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Telegram Settings",
          "description": _("Telegram Settings"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "MQTT Settings",
          "description": _("MQTT Settings"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Light RGB",
          "description": _("Light Colour"),
          "onboard": 1,
        },
        {
          "type": "doctype",
          "name": "Sound WAV",
          "description": _("Audio Files"),
          "onboard": 1,
        }         
      ]
    }
  ]