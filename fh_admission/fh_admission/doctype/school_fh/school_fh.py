# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SchoolFH(Document):
	@frappe.whitelist()
	def append_grades_in_table(self):
		all_filtered_grades = frappe.get_all("Grade FH", filters={"grade_type": self.grade_type}, fields=[])

		for grade in all_filtered_grades:
			child_grade_doc = frappe.new_doc("Grade Details FH")

			child_grade_doc.grade = grade.name

			self.grade_details.append(child_grade_doc)
			self.save()
