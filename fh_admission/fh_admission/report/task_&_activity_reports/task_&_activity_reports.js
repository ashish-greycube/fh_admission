// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Task & Activity Reports"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -7)
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "user",
			"label": "PRO",
			"fieldtype": "Link",
			"options": "User"
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		// Use the default formatter first
		value = default_formatter(value, row, column, data);

		// Apply custom logic based on column ID
		if (column.fieldname === "overdue_task") {
			if (value == "Yes") {
				value = `<span style="color:red;">${value}</span>`;
			}
		}
		return value;
	}
};
