# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

@frappe.whitelist()
def generate_form_url_with_source(source):
	valid_source = None
	if source:
		valid_source = source.replace(" ", "_").lower()
		# URL = "{0}/admission-inquiry?source={1}".format(frappe.utils.get_url(), valid_source)
	return valid_source

@frappe.whitelist()
def generate_html_of_source_urls():
    # Fetch the settings document
    settings = frappe.get_doc("FH Admission Settings", "FH Admission Settings")
    base_url = frappe.utils.get_url()
    
    # Return early if child table is empty
    if not settings.url_sources:
        return "<div class='text-muted'>No URLs generated yet.</div>"

    # Start HTML string
    html = '''
        <table class="table table-bordered">
        <thead>
            <tr>
                <th scope="col" style="width: 50px;">No</th>
                <th scope="col">URL</th>
            </tr>
        </thead>
        <tbody>
    '''

    counter = 1
    for row in settings.url_sources:
        # Construct the URL as requested: {base}/admission-inquiry?source={source}
        full_url = "{0}/admission-inquiry?source={1}".format(base_url, row.source)
        
        html += """
            <tr>
                <td>{0}</td>
                <td><a href="{1}" target="_blank" style="word-break: break-all;">{1}</a></td>
            </tr>
        """.format(counter, full_url)
        
        counter += 1

    html += '''
        </tbody>
        </table>
    '''
    
    return html

class FHAdmissionSettings(Document):
	pass
