// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

let grades_list = [""]

frappe.query_reports["Agent Performance Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": "Date",
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"label": "Date",
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "campus",
			"label": "Campus",
			"fieldtype": "Link",
			"options": "School FH"
		},
		{
			"fieldname": "grade",
			"label": "Grade",
			"fieldtype": "Select",
			"options": []
		},
		{
			"fieldname": "user",
			"label": "PRO",
			"fieldtype": "Link",
			"options": "User"
		},
	],
	onload: function (report) {
		frappe.db.get_list("Grade FH", {
			fields: ["grade"],
			limit: 0
		}).then((r) => {
			console.log(r)
			for (grade in r) {
				if (!grades_list.includes(r[grade]["grade"])) {
					grades_list.push(r[grade]["grade"])
				}
			}

			grades_list.sort()

			// Target the 'grade' filter and update its options array
			let grade_filter = report.get_filter('grade');
			grade_filter.df.options = grades_list;

			// Refresh the filter UI elements to display new values
			grade_filter.refresh();
		})
	}
};
