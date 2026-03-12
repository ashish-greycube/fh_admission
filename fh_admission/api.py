import json
import frappe
import itertools
from collections import defaultdict

@frappe.whitelist()
def get_eligible_grades(child_dob, child_academic_year, city):
    if not child_dob or not child_academic_year:
        frappe.throw(_("Please provide both Date of Birth and Target Academic Year"))

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
    results.append("EITHER" if len(items) == 2 else "ANY") 
        
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
        return "<div>No data available</div>", "<div>No data available</div>"

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
            <td>{info['code']}</td>
            <td>{school}</td>
            <td>{grades}</td>
        </tr>
        """

    table1 = f"""
		<table class="table table-bordered table-sm" style="border:1px solid black;">
			<thead class="table-light">
				<tr>
					<th>Code</th>
					<th>School Name</th>
					<th>Grades Available</th>
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
		<table class="table table-bordered table-sm" style="border:1px solid black;">
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
          school_rows = "".join([f"<tr><td>{s.school_name} ({s.name})</td></tr>" for s in all_schools])

    table2 = f"""
		<table class="table table-bordered table-sm" style="border:1px solid black;">
			<tbody>
                
				    {school_rows}
                
			</tbody>
		</table>
		"""

    return table1 + table2
