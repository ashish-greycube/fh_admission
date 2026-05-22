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
			"fieldname" : "task_id",
			"fieldtype" : "Link",
			"label" : "Task ID",
			"options" : "ToDo",
		},
		{
			"fieldname" : "task_type",
			"fieldtype" : "Data",
			"label" : "Task Type",
		},
		{
			"fieldname" : "associated_lead",
			"fieldtype" : "Data",
			"label" : "Associated Lead",
		},
		{
			"fieldname" : "task_creation",
			"fieldtype" : "Data",
			"label" : "Task Creation Date",
		},
		{
			"fieldname" : "task_due",
			"fieldtype" : "Data",
			"label" : "Task Due Date",
		},
		{
			"fieldname" : "task_owner",
			"fieldtype" : "Data",
			"label" : "Task Owner",
		},
		{
			"fieldname" : "task_status",
			"fieldtype" : "data",
			"label" : "Task Status",
		},
		{
			"fieldname" : "overdue_task",
			"fieldtype" : "Data",
			"label" : "Overdue Task",
		},
	]

def get_data(filters):

	conditions = ""

	if filters.get("from_date") and filters.get("to_date"):
		conditions += "AND DATE(t.creation) BETWEEN '{0}' AND '{1}'".format(filters["from_date"], filters["to_date"])
	if filters.get("user"):
		conditions += "AND t.allocated_to = '{0}'".format(filters["user"])

	data = frappe.db.sql("""
		SELECT
			t.name AS task_id,
			t.description AS task_type,
			t.reference_name AS associated_lead,
			DATE(t.creation) AS task_creation,
			t.date AS task_due,
			t.allocated_to AS task_owner,
			t.status AS task_status
		FROM
			`tabToDo` t
		WHERE
			1=1
			{0}
	""".format(conditions), as_dict=1, debug=1)

	today_date = frappe.utils.getdate()

	for d in data:
		frappe.errprint(f"{type(d.get("task_due"))} - {type(today_date)}")
		if d.get("task_status") == "Open" and d.get("task_due") < today_date:
			d["overdue_task"] = "Yes"
		else:
			d["overdue_task"] = "No"

	return data
