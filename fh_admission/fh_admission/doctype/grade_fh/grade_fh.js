// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Grade FH", {
    validate(frm) {
        frm.set_value("naming_convention", `${frm.doc.grade}-${frm.doc.board_type}-${frm.doc.school_type}`)
    },
});
