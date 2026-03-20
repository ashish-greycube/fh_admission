# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import json
import frappe
import requests
from frappe.model.document import Document
class InquiryFormFH(Document):
	pass

@frappe.whitelist()
def send_reminder_notification(country_code, mobile_no):
	output = {"success": False, "message": "It seems there are some technical issue. Please Try again after some time.",}
	admission_settings = frappe.get_doc("FH Admission Settings")
	api_key = admission_settings.get_password(fieldname="interakt_api_key", raise_exception=False)

	if api_key:
		URL = "https://api.interakt.ai/v1/public/message/"
		VARIABLE = "{0}/edit".format(mobile_no)
		payload = json.dumps({
			"countryCode": country_code,
			"phoneNumber": mobile_no,
			"callbackData": "Message Sent!",
			"type": "Template",
			"template": {
				"name": "incomplete_admission_1",
				"languageCode": "en",
				"bodyValues": [],
				"buttonValues": {
					"1": [
						VARIABLE
					]
				}
			},
			"fallback": [
				{
					"channel": "sms",
					"sender_id": "sms_header",
					"pe_id": "sms_entity_id",
					"provider_name": "default",
					"content": {
						"message": "Dear Parents,\n\nThank you for your interest in admission at our school. We noticed that your *Admission Inquiry Form is not yet fully completed*.\n\nKindly take a moment to complete the remaining details so we can process your inquiry. \n\nIf you need any assistance, please feel free to contact us.\n\nThank you.\nTeam Fountainhead",
						"dlt_te_id": "sms_template_id",
					}
				}
			]
		})
		headers = {
			'Authorization': 'Basic {0}'.format(api_key),
			'Content-Type': 'application/json'
		}

		response = requests.request("POST", URL, headers=headers, data=payload)

		res = response.json()

		if response.status_code in [200, 201] and res['result'] == True:
			output.update({
				"success": True,
				"message": "Reminder Message Sent To {0}".format(mobile_no),
			})
		return output
	else:
		output.update({
			"success": False,
			"message": "It seems there are some technical issue. Please Try again after some time.",
		})
	return output