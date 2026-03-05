// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Inquiry Form FH", {
    refresh(frm) {

    },
    add_child_to_table(frm) {
        call_add_child_details_to_table_when_btn_clicked(frm)
    }
});



function call_add_child_details_to_table_when_btn_clicked(frm) {
    return frappe.call({
        method: "fh_admission.api.add_child_details_to_table_when_btn_clicked",
        args: {
            doc: frm.doc
        },
        callback: () => {

        }
    })
}


["academic_year", "first_name", "middle_name", "last_name", "gender", "childs_dob", "current_school_nameif_applicable", "school_name"]