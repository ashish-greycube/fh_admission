# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    if not filters : filters = {}
    columns, data = [], []
 
    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "fieldname" : "child_name",
            "fieldtype" : "Data",
            "label" : "Child Name",
        },
        {
            "fieldname" : "grade",
            "fieldtype" : "Data",
            "label" : "Grade",
        },
        {
            "fieldname" : "lead_status",
            "fieldtype" : "Data",
            "label" : "Lead Status",
        },
        {
            "fieldname" : "parent_mobile",
            "fieldtype" : "Data",
            "label" : "Parent Mobile Number",
        },
        {
            "fieldname" : "parent_name",
            "fieldtype" : "Data",
            "label" : "Parent Name",
        },
        {
            "fieldname" : "email",
            "fieldtype" : "data",
            "label" : "Email ID",
        },
        {
            "fieldname" : "school",
            "fieldtype" : "Data",
            "label" : "Selected School",
        },
        {
            "fieldname" : "city",
            "fieldtype" : "Data",
            "label" : "City",
        },
        {
            "fieldname" : "inquiry_date",
            "fieldtype" : "Data",
            "label" : "Inquiry Date",
        },
		{
            "fieldname" : "lead_source",
            "fieldtype" : "Data",
            "label" : "Lead Source",
        },
        {
            "fieldname" : "lead_id",
            "fieldtype" : "Link",
            "label" : "Lead ID",
            "options" : "Lead",
        },
        {
            "fieldname" : "last_interaction",
            "fieldtype" : "Data",
            "label" : "Last Interaction Date",
        },
    ]

def get_data(filters):

    conditions = ""

    if filters.get("source"):
        conditions += "AND l.source = '{0}'".format(filters["source"])
    if filters.get("campus"):
        conditions += "AND l.custom_eligible_school = '{0}'".format(filters["campus"])
    if filters.get("city"):
        conditions += "AND l.custom_city_you_are_seeking_admission = '{0}'".format(filters["city"])
    if filters.get("status"):
        conditions += "AND l.status = '{0}'".format(filters["status"])
	
	# We compare Date of Creation to Filter's Date => Filter's date is converted from DD-MM-YYYY -> to -> YYYY-MM-DD for SQL comparision
    if filters.get("date"):
        filter_date = frappe.utils.getdate(filters["date"])
        conditions += "AND DATE(l.creation) = '{0}'".format(filter_date)

    if filters.get("grade"):
        # grade = filters["grade"].split("-")[0]
        conditions += "AND l.custom_eligible_grade = '{0}'".format(filters["grade"])

    return frappe.db.sql("""
		SELECT 
			l.name AS lead_id,
			l.source AS lead_source,
			l.status AS lead_status,
			CONCAT(IFNULL(l.custom_fathers_first_name, ''), ' ', IFNULL(l.custom_fathers_last_name, '')) AS parent_name,
			l.lead_name AS child_name,
			l.mobile_no AS parent_mobile,
			l.custom_father_email AS email,
			l.custom_city_you_are_seeking_admission AS city,
			l.custom_campus AS school,
			l.custom_eligible_grade AS grade,
			DATE(l.creation) AS inquiry_date,
			IFNULL(DATE(event.latest_date), "-") AS last_interaction
		FROM
			`tabLead` l
		LEFT JOIN (
			SELECT 
				ep.reference_docname AS lead_id,
				MAX(e.starts_on) AS latest_date
			FROM
				`tabEvent` e
			JOIN 
				`tabEvent Participants` ep
			ON
				ep.parent = e.name
			WHERE 
				ep.reference_doctype = 'Lead'
				AND e.docstatus != 2
                AND (e.status = "Completed" OR e.status = "Closed")
			GROUP BY 
				ep.reference_docname
		) event
		ON
			l.name = event.lead_id
		WHERE
			l.docstatus != 2
			{0}
    """.format(conditions), as_dict=1, debug=1)
