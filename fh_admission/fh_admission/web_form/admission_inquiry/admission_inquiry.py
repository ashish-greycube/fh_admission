import json
import frappe
import requests
from frappe.auth import LoginManager
import random

def get_context(context):
	pass

@frappe.whitelist()
def save_data_to_doc_on_change(mobile_no, fieldname, value):
	if mobile_no:
		# Save value of field in inquiry document.
		frappe.errprint(f"{mobile_no, fieldname, value}")
		frappe.db.set_value("Inquiry Form FH", mobile_no, fieldname, value, update_modified=False)

		# If field is checkbox then update no of children added in inquiry form.
		if fieldname == 'do_you_want_to_add_child_second': 
			frappe.db.set_value("Inquiry Form FH", mobile_no, 'no_of_added_children', 2 if int(value) == 1 else 1, update_modified=False)
		
		if fieldname == 'do_you_want_to_add_child_third':
			frappe.db.set_value("Inquiry Form FH", mobile_no, 'no_of_added_children', 3 if int(value) == 1 else 2, update_modified=False)

		if fieldname == 'do_you_want_to_add_another_child_fourth':
			frappe.db.set_value("Inquiry Form FH", mobile_no, 'no_of_added_children', 4 if int(value) == 1 else 3, update_modified=False)

		if fieldname == 'do_you_want_to_add_another_child_fifth':
			frappe.db.set_value("Inquiry Form FH", mobile_no, 'no_of_added_children', 5 if int(value) == 1 else 4, update_modified=False)

		# To verify that children's date of birth is changed return true.
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

		no_of_added_children = doc.no_of_added_children
	return result, no_of_added_children

def send_confirmation_notification_on_success(docname, api_key):
		country_code = frappe.db.get_value("Inquiry Form FH", docname, 'country_code')
		mobile_no = frappe.db.get_value("Inquiry Form FH", docname, 'mobile_no')

		output = {
			"success": False, 
			"message": "It seems there are some technical issue. Please Try again after some time."
		}

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
		if response.status_code in [200, 201] and res['result'] == True:
			output.update({
				"success": True,
				"message": "Success Message Sent To {0}".format(mobile_no),
			})
			frappe.local.login_manager = LoginManager()
			frappe.local.login_manager.logout("test@abc.com")
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
					if doc.get(field) == None or doc.get(field) == '':
						status = 'Incomplete'
			elif int(frappe.db.get_value("Inquiry Form FH", docname, 'no_of_added_children')) == 2:
				for field in ['first_child_eligible_grades', 'first_child_eligible_schools', 'second_child_eligible_grades', 'second_child_eligible_schools']:
					print(field, doc.get(field), "2")
					if doc.get(field) == None or doc.get(field) == '':
						status = 'Incomplete'
			elif int(frappe.db.get_value("Inquiry Form FH", docname, 'no_of_added_children')) == 3:
				for field in ['first_child_eligible_grades', 'first_child_eligible_schools', 'second_child_eligible_grades', 'second_child_eligible_schools', 'third_child_eligible_grades', 'third_child_eligible_schools']:
					print(field, doc.get(field))
					if doc.get(field) == None or doc.get(field) == '':
						status = 'Incomplete'
			elif int(frappe.db.get_value("Inquiry Form FH", docname, 'no_of_added_children')) == 4:
				for field in ['first_child_eligible_grades', 'first_child_eligible_schools', 'second_child_eligible_grades', 'second_child_eligible_schools', 'third_child_eligible_grades', 'third_child_eligible_schools', 'fourth_child_eligible_grades', 'fourth_child_eligible_schools']:
					print(field, doc.get(field), "4")
					if doc.get(field) == None or doc.get(field) == '':
						status = 'Incomplete'
			elif int(frappe.db.get_value("Inquiry Form FH", docname, 'no_of_added_children')) == 5:
				for field in ['first_child_eligible_grades', 'first_child_eligible_schools', 'second_child_eligible_grades', 'second_child_eligible_schools', 'third_child_eligible_grades', 'third_child_eligible_schools', 'fourth_child_eligible_grades', 'fourth_child_eligible_schools', 'fifth_child_eligible_grades', 'fifth_child_eligible_schools']:
					if doc.get(field) == None or doc.get(field) == '':
						status = 'Incomplete'
	return status

def create_lead_per_child_on_submit_of_inquiry_form(webform):
    data = frappe.parse_json(webform)
    if data:
        if data.first_child_eligible_grades != "" and data.first_child_eligible_schools != "":
             create_new_lead(
				 data.first_child_first_name, data.first_child_middle_name, data.first_child_last_name, data.first_child_gender, data.source, data.fathers_mobile_no, "Lead", data.mobile_no
			 )

        if data.do_you_want_to_add_child_second == 1 and data.second_child_eligible_grades != "" and data.second_child_eligible_schools != "":
             create_new_lead(
				data.second_child_first_name, data.second_child_middle_name, data.second_child_last_name, data.second_child_gender, data.source, data.fathers_mobile_no, "Lead", data.mobile_no
			 )

        if data.do_you_want_to_add_child_third == 1 and data.third_child_eligible_grades != "" and data.third_child_eligible_schools != "":
             create_new_lead(
                data.third_child_first_name, data.third_child_middle_name, data.third_child_last_name, data.third_child_gender, data.source, data.fathers_mobile_no, "Lead", data.mobile_no
             )

        if data.do_you_want_to_add_another_child_fourth == 1 and data.fourth_child_eligible_grades != "" and data.fourth_child_eligible_schools != "":
             create_new_lead(
                data.fourth_child_first_name, data.fourth_child_middle_name, data.fourth_child_last_name, data.fourth_child_gender, data.source, data.fathers_mobile_no, "Lead", data.mobile_no
             )

        if data.do_you_want_to_add_another_child_fifth == 1 and data.fifth_child_eligible_grades != "" and data.fifth_child_eligible_schools != "":
             create_new_lead(
                data.fifth_child_first_name, data.fifth_child_middle_name, data.fifth_child_last_name, data.fifth_child_gender, data.source, data.fathers_mobile_no, "Lead", data.mobile_no
             )
        
def create_new_lead(first_name, middle_name, last_name, gender, source, phone, status, reference):
	isLeadExist = frappe.db.get_value("Lead", {
		"first_name" : first_name,
		"mobile_no": phone,
		"custom_inquiry_form_reference" : reference
	})
	if isLeadExist == None:
		doc = frappe.new_doc("Lead")
		doc.first_name = first_name 
		doc.middle_name = middle_name
		doc.last_name = last_name
		doc.gender = gender
		doc.source = source
		doc.mobile_no = phone
		doc.status = status
		doc.custom_inquiry_form_reference = reference

		doc.save(ignore_permissions=True)

@frappe.whitelist()
def change_status_of_doc_on_form_submit_and_send_message(docname, webform_data):
	output = {}
	if docname:
		# Validate Empty Fields Before Submitting Form & Update Status
		status = check_for_empty_fields_before_set_status_as_completed(docname)
		print(status)
		if status == "Completed":
			frappe.db.set_value("Inquiry Form FH", docname, 'status', "Completed", update_modified=False)
			frappe.db.commit()

		# Create Lead & Send Confirmation Message On Whatsapp
		admission_settings = frappe.get_doc("FH Admission Settings")
		api_key = admission_settings.get_password(fieldname="interakt_api_key", raise_exception=False)
		if api_key and status == "Completed":
			print("Yes Completed---------------")
			create_lead_per_child_on_submit_of_inquiry_form(webform_data)
			output = send_confirmation_notification_on_success(docname, api_key)
		return output
	
@frappe.whitelist()
def get_html_of_all_schools():
    colors = ['#2e8fbf', '#d74660']
    all_schools = frappe.db.get_all("School FH" ,['name', 'school_name', 'city'], order_by="city")
	
    school_rows = ""
    previous_idx = 0
    if all_schools:
        for s in all_schools:
            idx, previous_idx = get_unique_random_idx(0, 1, previous_idx)
            school_rows = school_rows + f"<tr><td style='border:1px solid black; background-color:{colors[idx]}; color:white;'>{s.school_name}</td><td style='border:1px solid black; background-color:{colors[idx]}; color:white;'>{s.name}</td><td style='border:1px solid black; background-color:{colors[idx]}; color:white;'>{s.city}</td></tr>"
        #  = "".join([f"<tr><td style='border:1px solid black; background-color:{colors[]};'>{s.school_name}</td><td style='border:1px solid black; background-color:{colors[]};'>{s.name}</td><td style='border:1px solid black; background-color:{colors[]};'>{s.city}</td></tr>" ])
    
    template = f"""
        <table class="table table-sm" style="border:1px solid black;">
            <thead class="table-light">
                <tr>
                    <th style="border:1px solid black; background-color:#ebebeb; font-size:15px;">School Name</th>
                    <th style="border:1px solid black; background-color:#ebebeb; font-size:15px;">Code</th>
                    <th style="border:1px solid black; background-color:#ebebeb; font-size:15px;">City</th>
                </tr>
            </thead>
            <tbody>
                {school_rows}
            </tbody>
        </table>
        """
    return template

def get_unique_random_idx(min_idx, max_idx, previous_idx):
	idx = random.randint(min_idx, max_idx)
	if previous_idx == idx:
		while previous_idx == idx:
			idx = random.randint(min_idx, max_idx)
	previous_idx = idx
	return idx, previous_idx