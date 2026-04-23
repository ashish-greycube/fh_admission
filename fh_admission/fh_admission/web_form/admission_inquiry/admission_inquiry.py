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
		if fieldname in ['fathers_mobile_no', 'mothers_mobile_no']:
			if value != "" and (not value.isdigit() or len(value) > 10):
				frappe.throw("Please enter a valid 10 digit mobile number.")

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
				data.first_child_first_name, data.first_child_middle_name, data.first_child_last_name, data.first_child_gender, data.source, data.fathers_mobile_no, "Lead", data.mobile_no, data.first_child_eligible_schools, data.first_child_eligible_grades, data.first_child_date_of_birth, data.academic_year, data.first_child_current_school_name, data
			 )

        if data.do_you_want_to_add_child_second == 1 and data.second_child_eligible_grades != "" and data.second_child_eligible_schools != "":
             create_new_lead(
        		data.second_child_first_name, data.second_child_middle_name, data.second_child_last_name, data.second_child_gender, data.source, data.fathers_mobile_no, "Lead", data.mobile_no, data.second_child_eligible_schools, data.second_child_eligible_grades, data.second_child_date_of_birth, data.second_child_academic_year, data.second_child_current_school_name, data
			 )

        if data.do_you_want_to_add_child_third == 1 and data.third_child_eligible_grades != "" and data.third_child_eligible_schools != "":
             create_new_lead(
                data.third_child_first_name, data.third_child_middle_name, data.third_child_last_name, data.third_child_gender, data.source, data.fathers_mobile_no, "Lead", data.mobile_no, data.third_child_eligible_schools, data.third_child_eligible_grades, data.third_child_childs_dob, data.third_child_academic_year, data.third_child_current_school_name, data
             )

        if data.do_you_want_to_add_another_child_fourth == 1 and data.fourth_child_eligible_grades != "" and data.fourth_child_eligible_schools != "":
             create_new_lead(
                data.fourth_child_first_name, data.fourth_child_middle_name, data.fourth_child_last_name, data.fourth_child_gender, data.source, data.fathers_mobile_no, "Lead", data.mobile_no, data.fourth_child_eligible_schools, data.fourth_child_eligible_grades, data.fourth_child_childs_dob, data.fourth_child_academic_year, data.fourth_child_current_school_name, data
             )

        if data.do_you_want_to_add_another_child_fifth == 1 and data.fifth_child_eligible_grades != "" and data.fifth_child_eligible_schools != "":
             create_new_lead(
                data.fifth_child_first_name, data.fifth_child_middle_name, data.fifth_child_last_name, data.fifth_child_gender, data.source, data.fathers_mobile_no, "Lead", data.mobile_no, data.fifth_child_eligible_schools, data.fifth_child_eligible_grades, data.fifth_child_childs_dob, data.fifth_child_academic_year, data.fifth_child_current_school_name, data
             )
        
def create_new_lead(first_name, middle_name, last_name, gender, source, phone, status, reference, eligible_school, eligible_grade, dob, academic_year, current_school_name, data):
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
		doc.custom_child_dob = dob
		doc.custom_academic_year_applying_for = academic_year
		doc.custom_current_school_name = current_school_name
		doc.custom_eligible_grade = eligible_grade
		doc.custom_eligible_school = eligible_school
		doc.custom_city_you_are_seeking_admission = data.city_for_admission
		doc.custom_where_are_you_from = data.where_are_you_from
		doc.custom_select_state = data.state
		doc.custom_gujarat_city = data.select_gujarat_city
		doc.custom_maharashtra_city = data.select_maharashtra_city
		doc.custom_fathers_first_name = data.fathers_first_name
		doc.custom_fathers_last_name = data.fathers_last_name
		doc.custom_fathers_mobile_no = data.fathers_mobile_no
		doc.custom_father_email = data.father_email
		doc.custom_mothers_first_name = data.mothers_first_name
		doc.custom_mothers_last_name = data.mothers_last_name
		doc.custom_mothers_mobile_no = data.mothers_mobile_no
		doc.custom_mothers_email = data.mothers_last_name
		doc.custom_fountain_staff_parent_id = data.fountain_staff_parent_id
		doc.custom_sibling_student_id = data.sibling_student_id
		

		if eligible_school.startswith("1st"):
			selected_school = eligible_school.split(',')[0].strip().split(' ')[-1]
			doc.custom_selected_school = eligible_school
			doc.custom_campus = selected_school
		else:
			selected_school = eligible_school
			doc.custom_selected_school = selected_school
			doc.custom_campus = selected_school

		doc.insert(ignore_permissions=True)

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
	all_schools = frappe.db.get_all("School FH" ,['name', 'school_name', 'city'], order_by="city")

	school_rows = ""
	if all_schools:
		counter = 0
		for s in all_schools:
			# We use a data-attribute or class for the alternating colors
			color_class = 'warning' if counter == 0 else 'info'
			
			school_rows += f"""
			<div class='school-card {color_class}'>
				<strong>{s.school_name}</strong><br>
				({s.name} - {s.city})
			</div>
			"""
			counter = 0 if counter == 1 else 1

	template = f"""
		<style>
		.school-grid {{
			display: grid;
			/* Desktop: 4 columns */
			grid-template-columns: repeat(4, 1fr);
			gap: 6px;
			width: 100%;
		}}

		.school-card {{
			padding: 0.6em 0.2em;
			text-align: center;
			border-radius: 4px;
			font-family: sans-serif;
			font-size: 0.7rem;
		}}

		/* Color States */
		.warning {{ background-color: #ffc107; color: #212529; }}
		.info {{ background-color: #0dcaf0; color: #fff; }}

		/* Tablet: 2 columns (max-width: 992px) */
		@media (max-width: 992px) {{
			.school-grid {{
				grid-template-columns: repeat(2, 1fr);
			}}
		}}

		/* Mobile: 1 column (max-width: 480px) */
		@media (max-width: 480px) {{
			.school-grid {{
				grid-template-columns: 1fr;
			}}
		}}
		</style>

		<div class="school-grid">
			{school_rows}
		</div>
		"""
	return template