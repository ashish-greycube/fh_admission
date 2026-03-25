import json
import frappe
import requests
from frappe.auth import LoginManager

def get_context(context):
	pass

@frappe.whitelist()
def save_data_to_doc_on_change(mobile_no, fieldname, value):
	if mobile_no:
		frappe.errprint(f"{mobile_no, fieldname, value}")
		frappe.db.set_value("Inquiry Form FH", mobile_no, fieldname, value, update_modified=False)
		if fieldname in ['do_you_want_to_add_child_second', 'do_you_want_to_add_child_third', 'do_you_want_to_add_another_child_fourth', 'do_you_want_to_add_another_child_fifth']:
			count = frappe.db.get_value("Inquiry Form FH", mobile_no, 'no_of_added_children')
			print(fieldname, value, count, type(value))
			res = count+1 if int(value) == 1 else count - 1
			frappe.db.set_value("Inquiry Form FH", mobile_no, 'no_of_added_children', res, update_modified=False)
		if fieldname in ['first_child_date_of_birth', 'second_child_date_of_birth', 'third_child_childs_dob', 'fourth_child_childs_dob', 'fifth_child_childs_dob']:
			return True

@frappe.whitelist()
def set_school_and_grade_values_on_load(docname):
	result = {}
	keys = [
		'first_child_eligible_grades', 'first_child_eligible_schools',
		'second_child_eligible_grades', 'second_child_eligible_schools',
		'third_child_eligible_grades', 'third_child_eligible_schools',
		'fourth_child_eligible_grades', 'fourth_child_eligible_schools',
		'fifth_child_eligible_grades', 'fifth_child_eligible_schools'
	]
	if docname:
		doc = frappe.get_doc("Inquiry Form FH", docname)
		if doc:
			for key in keys:
				result.update({key: doc.get(key)})
	return result

@frappe.whitelist()
def change_status_of_doc_on_form_submit_and_send_message(docname):
	if docname:
		status = check_for_empty_fields_before_set_status_as_completed(docname)
		if status == "Completed":
			frappe.db.set_value("Inquiry Form FH", docname, 'status', "Completed", update_modified=False)

		# Send Success Message
		output = {"success": False, "message": "It seems there are some technical issue. Please Try again after some time.",}
		admission_settings = frappe.get_doc("FH Admission Settings")
		api_key = admission_settings.get_password(fieldname="interakt_api_key", raise_exception=False)
		country_code = frappe.db.get_value("Inquiry Form FH", docname, 'country_code')
		mobile_no = frappe.db.get_value("Inquiry Form FH", docname, 'mobile_no')

		if api_key and status == "Completed":
			URL = "https://api.interakt.ai/v1/public/message/"

			payload = json.dumps({
				"countryCode": country_code,
				"phoneNumber": mobile_no,
				"callbackData": "Message Sent!",
				"type": "Template",
				"template": {
					"name": "thanks_completed_admission_inquiry_form",
					"languageCode": "en",
					"bodyValues": [],
					"buttonValues": {}
				},
				"fallback": [
					{
						"channel": "sms",
						"sender_id": "sms_header",
						"pe_id": "sms_entity_id",
						"provider_name": "default",
						"content": {
							"message": "Dear Parents,\n\nThank you for completing the **Admission Inquiry Form** for your child.\nOur admissions team will review the details and get in touch with you shortly regarding the next steps.\n\nWe appreciate your interest in our school.\n\nThank you.\nTeam Fountainhead",
							"dlt_te_id": "sms_template_id",
							"variables": []
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
			print(res)
			if response.status_code in [200, 201] and res['result'] == True:
				output.update({
					"success": True,
					"message": "Success Message Sent To {0}".format(mobile_no),
				})
				frappe.local.login_manager = LoginManager()
				frappe.local.login_manager.logout("test@abc.com")
			return output
		else:
			output.update({
				"success": False,
				"message": "It seems there are some technical issue. Please Try again after some time.",
			})
		return output

def check_for_empty_fields_before_set_status_as_completed(docname):
	status = 'Completed'
	if docname:
		doc = frappe.get_doc("Inquiry Form FH", docname)
		if doc:
			if int(frappe.db.get_value("Inquiry Form FH", docname, 'no_of_added_children')) == 1:
				for field in ['first_child_eligible_grades', 'first_child_eligible_schools']:
					print(field, doc.get(field))
					if doc.get(field) == None:
						status = 'Incomplete'
			elif int(frappe.db.get_value("Inquiry Form FH", docname, 'no_of_added_children')) == 2:
				for field in ['first_child_eligible_grades', 'first_child_eligible_schools', 'second_child_eligible_grades', 'second_child_eligible_schools']:
					print(field, doc.get(field), "2")
					if doc.get(field) == None:
						status = 'Incomplete'
			elif int(frappe.db.get_value("Inquiry Form FH", docname, 'no_of_added_children')) == 3:
				for field in ['first_child_eligible_grades', 'first_child_eligible_schools', 'second_child_eligible_grades', 'second_child_eligible_schools', 'third_child_eligible_grades', 'third_child_eligible_schools']:
					print(field, doc.get(field))
					if doc.get(field) == None:
						status = 'Incomplete'
			elif int(frappe.db.get_value("Inquiry Form FH", docname, 'no_of_added_children')) == 4:
				for field in ['first_child_eligible_grades', 'first_child_eligible_schools', 'second_child_eligible_grades', 'second_child_eligible_schools', 'third_child_eligible_grades', 'third_child_eligible_schools', 'fourth_child_eligible_grades', 'fourth_child_eligible_schools']:
					if doc.get(field) == None:
						status = 'Incomplete'
			elif int(frappe.db.get_value("Inquiry Form FH", docname, 'no_of_added_children')) == 5:
				for field in ['first_child_eligible_grades', 'first_child_eligible_schools', 'second_child_eligible_grades', 'second_child_eligible_schools', 'third_child_eligible_grades', 'third_child_eligible_schools', 'fourth_child_eligible_grades', 'fourth_child_eligible_schools', 'fifth_child_eligible_grades', 'fifth_child_eligible_schools']:
					if doc.get(field) == None:
						status = 'Incomplete'
	return status