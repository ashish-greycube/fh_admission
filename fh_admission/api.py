import json
import frappe
import itertools
from collections import defaultdict
from frappe import _
import random
import requests
from frappe.auth import LoginManager

@frappe.whitelist()
def get_eligible_grades(child_dob, child_academic_year, city):
    # if not child_dob or not child_academic_year:
    #     frappe.throw(_("Please provide both Date of Birth and Target Academic Year"))

    # Extract target year once in Python for efficiency
    try:
        target_year = int(child_academic_year[:4])
    except ValueError:
        frappe.throw(_("Invalid Academic Year format. Expected YYYY-YY (e.g., 2027-28)"))

    query = """
        WITH AdjustedCriteria AS (
            SELECT 
				school.name,
                school.school_name,
				school.city,
				grade.school_type,
                grade.grade_name,
                grade.base_academic_year,	
                /* Task 1: Dynamically calculate offset for EACH row */
                DATE_ADD(
                    grade.age_criteria_start_date, 
                    INTERVAL (%s - CAST(SUBSTRING(grade.base_academic_year, 1, 4) AS SIGNED)) YEAR
                ) AS adjusted_start_date,
                DATE_ADD(
                    grade.age_criteria_end_date, 
                    INTERVAL (%s - CAST(SUBSTRING(grade.base_academic_year, 1, 4) AS SIGNED)) YEAR
                ) AS adjusted_end_date
            FROM 
                `tabSchool FH` school
            INNER JOIN 
                `tabGrade Details FH` grade ON grade.parent = school.name
            WHERE 
                grade.base_academic_year LIKE '20%%' /* Safety: only rows with YYYY format */
        )
        SELECT 
			name,	
			school_type,
            school_name, 
			grade_name, 
			base_academic_year, 
            adjusted_start_date, 
			adjusted_end_date,
            city
        FROM 
            AdjustedCriteria
        WHERE 
            %s BETWEEN adjusted_start_date AND adjusted_end_date AND city = %s
    """

    # We pass target_year twice (for start and end date calculation) 
    # and child_dob for the final filter
    return frappe.db.sql(query, (target_year, target_year, child_dob, city), as_dict=True)

@frappe.whitelist()
def get_unique_grades(query_results):
	query_results = json.loads(query_results)
	unique_grades = []
	if query_results:
		for res in query_results:
			# if res.get('school_type') == school_type:
				if res.get('grade_name') not in unique_grades:
					unique_grades.append(res.get('grade_name'))
	return sorted(unique_grades)

def get_ordinal(n):
    """Helper function to return the ordinal string of a number (1st, 2nd, 3rd, etc.)"""
    if 11 <= (n % 100) <= 13:
        return str(n) + 'th'
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')

def get_possible_options_for_school(items):
    if not items:
        return []
        
    results = []
    
    # 1. Generate "Only [Item]" for every input
    for item in items:
        results.append(f"{item}")

    # --- STOP HERE IF ONLY ONE INPUT ---
    if len(items) == 1:
        return results
        
    # 2. Add "EITHER" or "ANY" (Only for 2+ inputs)
    # results.append("EITHER" if len(items) == 2 else "ANY") 
        
    # 3. All full-length permutations (Only for 2+ inputs)
    for perm in itertools.permutations(items):
        ordered_parts = [f"{get_ordinal(i + 1)} Preference {val}" for i, val in enumerate(perm)]
        results.append(" , ".join(ordered_parts))
        
    return results

@frappe.whitelist()
def get_unique_schools_based_on_grade(query_results, grade):
	query_results = json.loads(query_results)
	unique_schools = []
	schools = []
	if query_results and grade: 
		for res in query_results:
			if res.get('grade_name') == grade:
				if res.get('name') not in unique_schools:
					unique_schools.append(res.get('name'))

	if unique_schools != []:
		schools = get_possible_options_for_school(unique_schools)
	return schools


@frappe.whitelist()
def generate_eligibility_html_tables(data):
    # Load JSON string if passed as string
    if isinstance(data, str):
        data = json.loads(data)

    if not data:
        return "<div class='eligibility-criteria'>Based on the entered date of birth, no applicable grade is available</div>"

    # -------- Table 1 : School -> Grades --------
    school_map = defaultdict(lambda: {"code": "", "grades": set()})

    for item in data:
        school = item["school_name"]
        school_map[school]["code"] = item["name"]
        school_map[school]["grades"].add(item["grade_name"])

    table1_rows = ""
    for school, info in school_map.items():
        grades = ", ".join(sorted(info["grades"]))
        table1_rows += f"""
        <tr>
            <td style='border:1px solid black;'>{info['code']}</td>
            <td style='border:1px solid black;'>{school}</td>
            <td style='border:1px solid black;'>{grades}</td>
        </tr>
        """

    table1 = f"""
		<table class="table table-sm" style="border:1px solid black; margin-top:1rem;">
			<thead class="table-light">
				<tr>
					<th style='border:1px solid black;'>Code</th>
					<th style='border:1px solid black;'>Eligible School(s)</th>
					<th style='border:1px solid black;'>Eligible Grade(s)</th>
				</tr>
			</thead>
			<tbody>
			{table1_rows}
			</tbody>
		</table>
		"""

    # -------- Table 2 : School Types --------
    school_types = defaultdict(list)

    for item in data:
        school_types[item["school_type"]].append((item["school_name"], item["name"]))

    # remove duplicates
    for k in school_types:
        school_types[k] = list(set(school_types[k]))

    headers = list(school_types.keys())
    max_rows = max(len(v) for v in school_types.values())

    header_html = "".join([f"<th>{h}</th>" for h in headers])

    rows_html = ""
    for i in range(max_rows):
        rows_html += "<tr>"
        for h in headers:
            if i < len(school_types[h]):
                school, code = school_types[h][i]
                rows_html += f"<td>{school} ({code})</td>"
            else:
                rows_html += "<td></td>"
        rows_html += "</tr>"

    table2 = f"""
		<table class="table table-sm" style="border:1px solid black;">
			<thead class="table-light">
				<tr>
					{header_html}
				</tr>
			</thead>
			<tbody>
				{rows_html}
			</tbody>
		</table>
		"""

    city = data[0].get('city')
    all_schools = frappe.db.get_all("School FH", {"city": city}, ['name', 'school_name'], order_by="name")
    if all_schools:
          school_rows = "".join([f"<tr><td style='border:1px solid black;'>{s.school_name} ({s.name})</td></tr>" for s in all_schools])

    table2 = f"""
		<table class="table table-sm" style="border:1px solid black;">
            <thead class="table-light">
				<tr>
					<th style="border:1px solid black;">Schools In City {city}</th>
				</tr>
			</thead>
			<tbody>
                
				    {school_rows}
                
			</tbody>
		</table>
		"""

    final_html = f"""
        <div class="eligibility-criteria">
            {table1}
        </div>
    """
    return final_html


# --------------- Lead Customizations -------------------------
def change_sla_status_in_lead(lead_name, sla_status):
    if lead_name and sla_status:
        lead_doc = frappe.get_doc("Lead", lead_name)
        lead_doc.custom_sla_status  = sla_status
        lead_doc.save(ignore_permissions=True)

def update_sla_status_for_eligible_leads_at_every_hour():
    leads = frappe.db.get_all(
        "Lead",
        filters = {
            "creation": ["<=", frappe.utils.add_to_date(frappe.utils.now(), hours=-1)],
            "custom_sla_status": ''
        },
        fields = ["name"]
    )
    if leads:
        for lead in leads:
            lead_doc = frappe.get_doc("Lead", lead.name)
            if lead_doc.response_by and frappe.utils.now_datetime() > frappe.utils.get_datetime(lead_doc.response_by) and lead_doc.first_responded_on == None:
                change_sla_status_in_lead(lead.name, "Failed to Respond")
            else:
                change_sla_status_in_lead(lead.name, "Responded")

@frappe.whitelist()
def change_lead_owner_on_assingment(self, method=None):
     print("Lead Owner Changed===================================================================================")
     if self.reference_type == "Lead" and self.reference_name and self.description.startswith("Automatic Assignment"):
          if self.allocated_to:
               doc = frappe.get_doc("Lead", self.reference_name,)
               doc.lead_owner = self.allocated_to
               doc.save(ignore_permissions=True)
     
def on_change_of_lead_owner_assign_lead_to_that_user(self, method=None):
    if self.has_value_changed("lead_owner") and self.name and self.lead_owner:
        # Assign This Lead To The New Lead Owner
        todo = frappe.db.get_value("ToDo", {
            'reference_type' : 'Lead',
            'reference_name' : self.name,
            'assignment_rule' : '{0} - PRO Auto Assign'.format(self.custom_campus)
        }, 'name')
        if todo:
            doc = frappe.get_doc("ToDo", todo)
            doc.allocated_to = self.lead_owner
            doc.save(ignore_permissions=True)
            # frappe.msgprint("Lead is assigned to User {0}".format(self.lead_owner), alert=True, indicator="green")
       

def on_change_of_lead_owner_share_lead_to_that_user(self, method=None):
    if self.has_value_changed("lead_owner") and self.name and self.lead_owner and self.lead_owner != frappe.db.get_value("User", {"full_name": "Parent User"}, "name"):
        # Share This Lead With The New Lead Owner If Not Shared
        is_shared = frappe.db.exists("DocShare", {
            "share_doctype": self.doctype,
            "share_name": self.name,
            "user": self.lead_owner
        })
        if is_shared == None:
            frappe.share.add_docshare(
                self.doctype, self.name, self.lead_owner, read=1, write=1, submit=0, share=0, flags={"ignore_share_permission": True}, notify=1
            )
            # frappe.msgprint("Lead is shared with User {0}".format(self.lead_owner), alert=True, indicator="green")

@frappe.whitelist()
def check_logged_in_user_role():
    roles = frappe.get_roles(frappe.session.user)
    current_user = "Other User"
    if roles and "PRO User" in roles:
         current_user = "PRO User"
    
    if roles and "Campus Admin" in roles:
         current_user = "Campus Admin"     
	
    return current_user

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def filter_lead_owner_based_on_campus_for_campus_admin_role(doctype, txt, searchfield, start, page_len, filters):
    if filters.get("campus"):
        assigned_pros_to_campus = frappe.db.sql(
            '''
            SELECT taru.user, tu.full_name 
            FROM `tabAssignment Rule User` AS taru
            INNER JOIN `tabAssignment Rule` AS tar
            ON taru.parent = tar.name
            INNER JOIN `tabUser` tu
            ON tu.name = taru.user
            WHERE taru.parenttype  = "Assignment Rule"
            AND taru.parent = "{0} - PRO Auto Assign"
            AND taru.user LIKE %(txt)s
            '''.format(filters.get('campus')), {"txt": "%%%s%%" % txt}
        )

        return assigned_pros_to_campus
    

def uncheck_sidebar_checkbox_for_pro_role(self, method=None):
    roles = frappe.get_roles(self.name)
    if roles and "Campus Admin" not in roles and "PRO User" in roles:
        self.form_sidebar = 0
        self.list_sidebar = 0

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
def change_status_on_validate_and_send_message(self, method=None):
	output = {}
	if self:
		# Validate Empty Fields Before Submitting Form & Update Status
		status = check_for_empty_fields_before_set_status_as_completed(self.name)
		print(status)
		if status == "Completed":
			self.status = "Completed"

		# Create Lead & Send Confirmation Message On Whatsapp
		admission_settings = frappe.get_doc("FH Admission Settings")
		api_key = admission_settings.get_password(fieldname="interakt_api_key", raise_exception=False)
		if api_key and status == "Completed":
			create_lead_per_child_on_submit_of_inquiry_form(self)
			output = send_confirmation_notification_on_success(self.name, api_key)
		return output