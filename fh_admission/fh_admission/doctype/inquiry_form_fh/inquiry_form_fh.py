# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.website.website_generator import WebsiteGenerator
from frappe import _


class InquiryFormFH(Document):
	pass


# class InquiryFormFH(WebsiteGenerator):

# 	website = frappe._dict(
# 		template = "templates/generators/inquiry.html",
# 		condition_field = "is_published_field",
# 		page_title_field = "job_title",
# 	)

# 	def get_context(self, context):
# 		# show breadcrumbs
# 		context.parents = [{'name': 'inquiry_form_fh', 'title': _('All Jobs') }]
			
# 	def validate(self):
# 		self.route='inquiry/'+self.name
# 		# reccomedation_calculator(self)