// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

let grades_list = [""]

frappe.query_reports["Lead Report"] = {
	"filters": [
		{
			"fieldname": "source",
			"label": "Source",
			"fieldtype": "Link",
			"options": "Lead Source"
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
			"fieldname": "city",
			"label": "City",
			"fieldtype": "Link",
			"options": "School City FH"
		},
		{
			"fieldname": "date",
			"label": "Date",
			"fieldtype": "Date",
		},
		{
			"fieldname": "status",
			"label": "Lead Status",
			"fieldtype": "Select",
			"options": ['', 'Lead', 'Open', 'Replied', 'Opportunity', 'Quotation', 'Lost Quotation', 'Interested', 'Converted', 'Do Not Contact', 'Not Interested', 'Hold', 'Refused', 'Admission Form Fee Paid', 'Admitted', 'Junk']
		},
	],
	onload: function (report) {
		frappe.db.get_list("Grade FH", {
			fields: ["grade"],
			limit: 0
		}).then((r) => {
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
