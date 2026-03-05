// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("School FH", {
    add_grades(frm) {
        if (!frm.doc.grade_type) {
            frappe.throw("Grade Type can't be empty for fetching Grades.")

        }
        frm.call("append_grades_in_table")
    },
    school_name(frm) {
        // for setting abbrevetion automatically based on school name
        if (frm.doc.__islocal) {
            let parts = frm.doc.school_name.split(" ");
            let abbr = $.map(parts, function (p) {
                return p ? p.substr(0, 1) : null;
            }).join("");
            frm.set_value("abbrevetion", abbr);
        }
    }
});
