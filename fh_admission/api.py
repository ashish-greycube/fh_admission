# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from frappe.model.document import Document
import itertools
import json


recc_school_list = []
recc_grade_list = []
age_based_on_academic_year = ""
school_choice_html = ""
school_selection_html = ""

@frappe.whitelist(allow_guest=True)
def reccomedation_calculator(**kwargs):
	child_dob = kwargs["child_dob"] if "child_dob" in kwargs else ""
	city = kwargs["city"] if "city" in kwargs else ""
	academic_year = kwargs["academic_year"] if "academic_year" in kwargs else ""
	grade_type = kwargs["grade_type"] if "grade_type" in kwargs else ""

	if child_dob == "" or city == "" or academic_year == "":
		return

	age = age_calculator_based_on_ay(child_dob, academic_year)
	global age_based_on_academic_year
	age_based_on_academic_year = f"{age.years}Y, {age.months}M, {age.days}D"
	age_in_years = age.years

	global recc_grade_list
	recc_grade_list = grade_recc_new(academic_year, child_dob, city, grade_type)


	global recc_school_list
	recc_school_list = school_recc_new(city, age_in_years, recc_grade_list, grade_type)

	return {
		"html": html_output(age_based_on_academic_year, recc_grade_list, recc_school_list),
		"grade_list": recc_grade_list,
		"school_list": recc_school_list
	} 
	


def age_calculator_based_on_ay(child_dob, academic_year):
	ay_start_date = frappe.get_value("Academic Year FH", academic_year, "year_start_date")
	child_dob = datetime.strptime(child_dob, '%Y-%m-%d').date()

	delta = relativedelta(ay_start_date, child_dob)
	
	return delta
	

def grade_recc_new(academic_year_form, child_dob, city, grade_type):
	grades_list = []
	recc_grade_list = []

	child_dob = datetime.strptime(child_dob, '%Y-%m-%d').date()

	# Get list of all grades
	# grade_doc = frappe.get_all("Grade FH", fields=["base_ay", "age_criteria_start_date", "age_criteria_end_date", "grade"], filters={"grade_type": grade_type})

	# Get all schools of selected city
	all_school_list = frappe.get_all("School FH", fields=["name", "grade_type", "city"], filters={"city": city, "grade_type": grade_type})



	# by iterating over each school, we make unique grades list
	for school in all_school_list:
		school_doc = frappe.get_doc("School FH", school["name"]).as_dict()
		for row in school_doc["grade_details"]:
			if row["grade"] not in grades_list:
				grades_list.append(row["grade"])

	# for unique grade in grades list
	for grade_name in grades_list:
		# with grade's name get its doc
		grade = frappe.get_doc("Grade FH", grade_name)

		# get AY from Settings and Grade's base AY
		grade_base_ay = grade.get("base_ay")
		doc_grade_base_ay = frappe.get_doc("Academic Year FH", grade_base_ay)
		doc_form_ay = frappe.get_doc("Academic Year FH", academic_year_form)

		# criteria start & end date from Grade
		grade_start_date = (grade.get("age_criteria_start_date"))
		grade_end_date = (grade.get("age_criteria_end_date"))

		# Case in which selected AY is in future
		if doc_form_ay.year_start_date > doc_grade_base_ay.year_start_date or doc_form_ay.year_start_date < doc_grade_base_ay.year_start_date:
			# difference btw. base AY & Selected AY in years
			date_diff = relativedelta(doc_form_ay.year_start_date, doc_grade_base_ay.year_start_date)
			date_diff_years = date_diff.years

			# Incerement criteria date by difference in years
			grade_start_date = grade_start_date + relativedelta(years=date_diff_years)
			grade_end_date = grade_end_date + relativedelta(years=date_diff_years)

			# append the grade to Recc. list if eligible
			if child_dob>=grade_start_date and child_dob<=grade_end_date:
				recc_grade_list.append(grade.get("grade"))
		
		# Case where selected AY == Base AY in Grade
		elif doc_form_ay.year_start_date == doc_grade_base_ay.year_start_date:
			if child_dob>=grade_start_date and child_dob<=grade_end_date:
				recc_grade_list.append(grade.get("grade"))

	# print(recc_grade_list)
	return recc_grade_list

def school_recc_new(city, age_in_years, recc_grade_list, grade_type):
	# list out all school with city filter
	school_list = frappe.get_all("School FH", filters={"city": city, "grade_type": grade_type}, fields=["name"])

	recc_school_list = []
	unique_school_list = []

	# Iterate through all schools
	for school in school_list:
		# get school doc for getting all grades of a school
		school = frappe.get_doc("School FH", school)

		# Iterate through all rows of grade of a school
		for row in school.grade_details:
			# checking if selected grade is in recommended list or not
			if row.grade_name in recc_grade_list:
				# group by school and store grades in their respective schools
				if school.name not in unique_school_list:
					unique_school_list.append(school.name)
					recc_school_list.append({
						"school": school.name,
						"grade": [row.grade_name]
					})
				else:
					for recc_school in recc_school_list:
						if recc_school["school"] == school.name:
							recc_school["grade"].append(row.grade_name)

		
	# print(recc_school_list)
	return recc_school_list


def get_ordinal(n):
    """Helper function to return the ordinal string of a number (1st, 2nd, 3rd, etc.)"""
    if 11 <= (n % 100) <= 13:
        return str(n) + 'th'
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')

@frappe.whitelist(allow_guest=True)
def generate_school_choice_list(*args):
    items = list(args)
    if not items:
        return []
        
    results = []
    
    # 1. Generate "Only [Item]" for every input
    for item in items:
        results.append(f"Only {item}")

    # --- STOP HERE IF ONLY ONE INPUT ---
    if len(items) == 1:
        return results
        
    # 2. Add "EITHER" or "ANY" (Only for 2+ inputs)
    results.append("EITHER" if len(items) == 2 else "ANY") 
        
    # 3. All full-length permutations (Only for 2+ inputs)
    for perm in itertools.permutations(items):
        ordered_parts = [f"{get_ordinal(i + 1)} {val}" for i, val in enumerate(perm)]
        results.append(" , ".join(ordered_parts))
        
    return results


@frappe.whitelist(allow_guest=True)
def generate_school_choice_rows_html(selected_grade):

	args = []
	global school_choice_html
	school_choice_html = ""

	for recc_school in recc_school_list:
		if selected_grade in recc_school["grade"]:
			args.append(recc_school["school"])
	# frappe.errprint(args)

	if args:
		school_choice_html = "".join(f"""
			<tr><td>{line}</td></tr>
		""" for line in generate_school_choice_list(*args))
	elif not args:
		school_choice_html = "".join(f"""
			<tr><td>No School Applicable for {selected_grade}.</td></tr>
		""")
	# frappe.errprint(school_choice_html)

	global school_selection_html
	school_selection_html = ""
	school_selection_html = f"""
		<div class="school-choice" style='width: 50%'>
			<table class='table table-striped' style='border: 1px solid black; text-align: center; width: 50%'>
				<tr style='border: 1px solid black; text-align: center; width: 50%'><th style='border: 1px solid black; text-align: center; width: 50%'>School Selection</th></tr>
				{school_choice_html}
			</table>
		</div>
	"""

	return {
		"html": school_selection_html,
		"school_list": generate_school_choice_list(*args) if args else "No School Applicable"
	}


@frappe.whitelist()
# def html_output(city, child_dob, academic_year):	
def html_output(age_based_on_academic_year, recc_grade_list, recc_school_list):
	# making Recc. grade list to => "FPA": "G1, G2"
	school_grade_dict = {}
	unique_school_name_list = []
	for recc_school in recc_school_list:
		# school_grade_dict[recc_school["school"]] = recc_school["grade"]
		school_grade_dict[recc_school["school"]] = ", ".join(recc_school["grade"])

		# making a unique list of recommended schools
		if recc_school["school"] not in unique_school_name_list:
			unique_school_name_list.append(recc_school["school"])

	# print(school_grade_dict, unique_school_name_list)

	school_recc_row_for_html = " | ".join(f"{school}: {school_grade_dict[school]}" for school in unique_school_name_list)

	# print(school_recc_row_for_html)

	all_grades =  " | ".join(f"{grade}" for grade in recc_grade_list)
	# all_schools = " | ".join(f"{school["school"]}: {grades_of_recc_schools}" for school in recc_school_list)

	grade_choice_checks_html = "<br>".join(f"""
		<input class='grade-choice' name='grade-choice-radio' id='{grade.replace(' ', '_')}' type='radio' value='{grade}'>
		<label for='{grade.replace(' ', '_')}'>{grade}</label>
	""" for grade in recc_grade_list)

	

	return (f"""
		 	<h3>Age: {age_based_on_academic_year}</h3>
			<table class="table table-striped" style='border: 1px solid black; text-align: center; width: 50%'>
		 		<tr style='border: 1px solid black; text-align: center; width: 50%'><th style='border: 1px solid black; text-align: center; width: 50%'><center>Grade Recommendation</center></th></tr>
		 		<tr style='border: 1px solid black; text-align: center; width: 50%'><td>{all_grades or "Not Applicable"}</td></tr>
			</table>
			<table class="table table-striped" style='border: 1px solid black; text-align: center; width: 50%'>
		 		<tr style='border: 1px solid black; text-align: center; width: 50%'><th style='border: 1px solid black; text-align: center; width: 50%'><center>School Recommendation</center></th></tr>
		 		<tr style='border: 1px solid black; text-align: center; width: 50%'><td style='border: 1px solid black; text-align: center; width: 50%'>{school_recc_row_for_html or "Not Applicable"}</td></tr>
			</table>

		""")


@frappe.whitelist(allow_guest=True)
def add_child_details_to_table_when_btn_clicked(doc):
	doc = json.loads(doc)
	inquiry_doc = frappe.get_doc("Inquiry Form FH", doc["name"])
	child_details_doc = frappe.new_doc("Child Details FH").as_dict()

	excluded_fields = ["parent", "parentfield", "parenttype", "__islocal", "__unsaved","name"]

	for child_field in child_details_doc:
		if child_field not in excluded_fields:
			child_details_doc[child_field] = inquiry_doc.get(child_field)

	# inquiry_doc.all_child_details.append(child_details_doc)
	inquiry_doc.append("all_child_details", child_details_doc)

	inquiry_doc.save()
	
	# frappe.errprint(child_details_doc)


@frappe.whitelist(allow_guest=True)
def get_grade_type_from_city(city):
	schools_list = frappe.get_all("School FH", fields=["grade_type"], filters={"city":city})
	unique_grade_type_list = []

	for grade_type in schools_list:
		if grade_type["grade_type"] not in unique_grade_type_list:
			unique_grade_type_list.append(grade_type["grade_type"] )

	# frappe.errprint(unique_grade_type_list)

	if len(unique_grade_type_list) == 1:
		return {
			"status": 1,
			"types": unique_grade_type_list
		}
	else:
		return {
			"status": "more",
			"types": unique_grade_type_list
		}
