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
			"fieldname" : "agent_name",
			"fieldtype" : "Link",
			"label" : "Agent Name",
			"options": "User"
		},
		{
			"fieldname" : "leads_assigned",
			"fieldtype" : "Int",
			"label" : "Number of Leads Assigned",
		},
		{
			"fieldname" : "leads_contacted",
			"fieldtype" : "Int",
			"label" : "Leads Contacted",
		},
		{
			"fieldname" : "not_contacted",
			"fieldtype" : "Int",
			"label" : "Not Contacted",
		},
		{
			"fieldname" : "followups_completed",
			"fieldtype" : "Int",
			"label" : "Followups Completed",
		},
		{
			"fieldname" : "pending_followups",
			"fieldtype" : "Int",
			"label" : "Pending Followups",
		},
		{
			"fieldname" : "conversion_rate",
			"fieldtype" : "Data",
			"label" : "Conversion Rate",
		},
		{
			"fieldname" : "missed_sla",
			"fieldtype" : "Int",
			"label" : "Missed SLAs",
		},
		{
			"fieldname" : "tasks_completed",
			"fieldtype" : "Int",
			"label" : "Total Tasks Completed",
		},
		{
			"fieldname" : "tasks_overdue",
			"fieldtype" : "Int",
			"label" : "Tasks Overdue Count",
		},
	]

def get_data(filters):

	conditions = {}

	if filters.get("from_date") and filters.get("to_date"):
		conditions["date"] = "AND DATE(l.creation) BETWEEN '{0}' AND '{1}'".format(filters["from_date"], filters["to_date"])
	if filters.get("campus"):
		conditions["campus"] =  "AND l.custom_eligible_school = '{0}'".format(filters["campus"])
	if filters.get("grade"):
		# grade = filters["grade"].split("-")[0]
		conditions["grade"] = "AND l.custom_eligible_grade = '{0}'".format(filters["grade"])
	if filters.get("user"):
		conditions["user"] =  "AND u.name = '{0}'".format(filters["user"])

	data = frappe.db.sql("""
		SELECT
			u.name AS agent_name,
			IFNULL(COUNT(DISTINCT lead.lead_name), 0) AS leads_assigned,
			IFNULL(SUM(CASE WHEN lead.lead_status IN ("Replied", "Converted", "Admitted", "Admission Form Fee Paid") THEN 1 ELSE 0 END), 0) AS leads_contacted,
			IFNULL((COUNT(DISTINCT lead.lead_name) - SUM(CASE WHEN lead.lead_status IN ("Replied", "Converted", "Admitted", "Admission Form Fee Paid") THEN 1 ELSE 0 END)), 0) AS not_contacted,
			IFNULL((SUM(CASE WHEN (lead.lead_status IN ("Converted", "Lead", "Admitted", "Admission Form Fee Paid")) THEN 1 ELSE 0 END)) / COUNT(DISTINCT lead.lead_name), 0) AS conversion_rate,
			IFNULL(SUM(CASE WHEN lead.sla_status="Failed to Respond" THEN 1 ELSE 0 END), 0) AS missed_sla,
			SUM(IFNULL(lead.tasks_completed, 0)) AS tasks_completed,
			SUM(IFNULL(lead.tasks_overdue, 0)) AS tasks_overdue,
			SUM(IFNULL(lead.followups_completed, 0)) AS followups_completed,
			SUM(IFNULL(lead.pending_followups, 0)) AS pending_followups
		FROM
			`tabUser` u
		LEFT JOIN
			(
				SELECT
					l.name AS lead_name,
					l.lead_owner AS lead_owner,
					l.status AS lead_status,
					event.lead_event_count AS lead_event_count,
					event.followups_completed AS followups_completed,
					event.pending_followups AS pending_followups,
					todo.tasks_completed,
					todo.total_tasks,
					todo.tasks_overdue,
					l.custom_sla_status AS sla_status
				FROM
					`tabLead` l
				LEFT JOIN
					(
						SELECT
							ep.reference_docname AS event_participant,
							COUNT(e.name) AS lead_event_count,
							SUM(CASE WHEN (e.status IN ("Completed", "Closed")) THEN 1 ELSE 0 END) AS followups_completed,
							SUM(CASE WHEN (e.status NOT IN ("Completed", "Closed")) THEN 1 ELSE 0 END) AS pending_followups
						FROM
							`tabEvent` e
						LEFT JOIN
							`tabEvent Participants` ep
						ON
							ep.parent = e.name
							AND ep.reference_doctype = "Lead"
						GROUP BY
							ep.reference_docname
					) event
				ON
					event.event_participant  = l.name
				LEFT JOIN
					(
						SELECT
							SUM(CASE WHEN (td.status="Closed") THEN 1 ELSE 0 END) AS tasks_completed,
							COUNT(td.name) AS total_tasks,
							td.reference_name,
							td.date AS task_due_date,
							td.status AS task_status,
							SUM(CASE WHEN (td.status="Open" AND td.date < CURDATE()) THEN 1 ELSE 0 END) AS tasks_overdue
						FROM
							`tabToDo` td
						GROUP BY
							td.reference_name
					) todo
				ON todo.reference_name = l.name
				WHERE
					1=1
					{0}
					{1}
					{2}
				GROUP BY
					l.name
			) lead
		ON
			lead.lead_owner = u.name
		WHERE
			1=1
			{3}
		GROUP BY
			u.name
		ORDER BY
			leads_assigned DESC 
	""".format(conditions.get("date") or "", conditions.get("campus") or "", conditions.get("grade") or "", conditions.get("user") or ""), as_dict=1, debug=1)

	for row in data:
		row["conversion_rate"] = f"{round(row['conversion_rate'] * 100)}%"

	return data