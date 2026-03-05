// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Academic Year FH", {
    onload: function (frm) {

        let current_year_start_date = frappe.datetime.year_start()
        let academic_year_start_date = frappe.datetime.add_months(current_year_start_date, 5)

        if (frm.doc.__islocal) {
            frm.set_value("year_start_date", academic_year_start_date);
        }
    },
    year_start_date: function (frm) {
        if (!frm.doc.is_short_year) {
            let year_end_date = frappe.datetime.add_days(
                frappe.datetime.add_months(frm.doc.year_start_date, 12),
                -1
            );
            frm.set_value("year_end_date", year_end_date);
        }
    },
});
