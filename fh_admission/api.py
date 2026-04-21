import json
import frappe
import itertools
from collections import defaultdict
from frappe import _
import random

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
               frappe.db.set_value("Lead", self.reference_name, "lead_owner", self.allocated_to)
     
def on_change_of_lead_owner_assign_lead_to_that_user(self, method=None):
    if self.has_value_changed("lead_owner") and self.name and self.lead_owner:
        # Assign This Lead To The New Lead Owner
        isAssigned = False
        isShared = False
        todo = frappe.db.get_value("ToDo", {
            'reference_type' : 'Lead',
            'reference_name' : self.name,
            'assignment_rule' : '{0} - PRO Auto Assign'.format(self.custom_campus)
        }, 'name')
        if todo:
            doc = frappe.get_doc("ToDo", todo)
            doc.allocated_to = self.lead_owner
            isAssigned = True

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
            isShared = True
             
        doc.save(ignore_permissions=True)
        if isAssigned:
            frappe.msgprint("Lead is assigned to User {0}".format(self.lead_owner), alert=True, indicator="green")
        if isShared:
            frappe.msgprint("Lead is shared with User {0}".format(self.lead_owner), alert=True, indicator="green")

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