# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

@frappe.whitelist()
def generate_form_url_with_source(source):
	URL = ""
	if source:
		valid_source = source.replace(" ", "_").lower()
		URL = "{0}/admission-inquiry?source={1}".format(frappe.utils.get_url(), valid_source)
	return URL 

@frappe.whitelist()
def generate_html_of_source_urls():
	html = ""
	urls = frappe.db.get_value("FH Admission Settings", "FH Admission Settings", "urls")
	if urls != "" or urls != None:
		html = '''
			<table class="table table-bordered">
			<thead>
				<tr>
				<th scope="col">No</th>
				<th scope="col">URL</th>
				</tr>
			</thead>
			<tbody>
		'''
		urls_list = urls.split("\n")
		counter = 1
		for u in urls_list:
			if u != "":
				html = html + "<tr><td>{1}</td><td><a href={0}>{2}</a></td></tr>".format(u,counter,  u )
				counter += 1
		html = html + '''
			</tbody>
			</table>
		'''
	return html

class FHAdmissionSettings(Document):
	pass
