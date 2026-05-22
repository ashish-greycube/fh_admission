// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Funnel Analysis Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "campus",
			"label": "Campus",
			"fieldtype": "Link",
			"options": "School FH"
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		// Use the default formatter first
		value = default_formatter(value, row, column, data);

		// Apply custom logic based on column ID
		if (column.fieldname === "stage_coversion") {
			if (parseFloat(value) > 50) {
				value = `<span style="color:green;">${value}</span>`;
			} else if (parseFloat(value) <= 50) {
				value = `<span style="color:red;">${value}</span>`;
			}
		}
		return value;
	}
};
