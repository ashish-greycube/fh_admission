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
			"fieldname" : "campus",
			"fieldtype" : "Data",
			"label" : "Campus",
		},
		{
			"fieldname" : "total_inquiries",
			"fieldtype" : "Int",
			"label" : "Total Inquiries",
		},
		{
			"fieldname" : "qualified_leads",
			"fieldtype" : "IntS",
			"label" : "Number of Leads Qualified",
		},
		{
			"fieldname" : "admissions_confirmed",
			"fieldtype" : "Int",
			"label" : "Admissions Confirmed",
		},
		{
			"fieldname" : "drop_off_rate",
			"fieldtype" : "Data",
			"label" : "Drop-Off Rate",
		},
		{
			"fieldname" : "stage_coversion",
			"fieldtype" : "Data",
			"label" : "Stage Conversion %",
		},
	]

def get_data(filters):

	conditions = {}

	if filters.get("from_date") and filters.get("to_date"):
		conditions["date"] = "AND DATE(l.creation) BETWEEN '{0}' AND '{1}'".format(filters["from_date"], filters["to_date"])
	if filters.get("campus"):
		conditions["campus"] =  "AND s.name = '{0}'".format(filters["campus"])

	data = frappe.db.sql("""
		SELECT
			IFNULL(lead.total_inquiries, 0) AS total_inquiries,
			IFNULL(lead.qualified_leads, 0) AS qualified_leads,
			IFNULL(lead.admissions_confirmed, 0) AS admissions_confirmed,
			IFNULL(lead.drop_off_rate, 0) AS drop_off_rate,
			IFNULL((lead.admissions_confirmed / lead.total_inquiries), 0) AS stage_coversion,
			s.name AS campus
		FROM
			`tabSchool FH` s
		LEFT JOIN
			(
				SELECT
					l.custom_eligible_school AS school,
					COUNT(l.name) AS total_inquiries,
					SUM(CASE WHEN (l.status IN ("Replied", "Lead", "Coverted", "Admitted", "Admission Form Fee Paid", "Contacted", "To Follow-up", "Waitlist")) THEN 1 ELSE 0 END) AS qualified_leads,
					SUM(CASE WHEN l.status IN ("Admitted", "Converted", "Admission Form Fee Paid") THEN 1 ELSE 0 END) AS admissions_confirmed,
					(SUM(CASE WHEN (l.status IN ("Do Not Contact", "Not Interested", "Parent Refusal", "Admission Withdrawal")) THEN 1 ELSE 0 END))/COUNT(l.name) AS drop_off_rate
				FROM
					`tabLead` l
				WHERE
					1=1
					{0}
				GROUP BY
					l.custom_eligible_school
			) lead
		ON
			lead.school = s.name
		WHERE
			1=1
			{1}
		GROUP BY
			s.name
	""".format(conditions.get("date") or "", conditions.get("campus") or ""), as_dict=1, debug=1)
	
	for row in data:
		row["drop_off_rate"] = f"{round(row['drop_off_rate'] * 100)}%"
		row["stage_coversion"] = f"{round(row['stage_coversion'] * 100)}%"

	return data
