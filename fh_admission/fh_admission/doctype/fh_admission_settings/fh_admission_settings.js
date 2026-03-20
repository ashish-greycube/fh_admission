// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("FH Admission Settings", {
    generate_url(frm) {
        if (frm.doc.enter_source_name != null) {
            frappe.call({
                method: 'fh_admission.fh_admission.doctype.fh_admission_settings.fh_admission_settings.generate_form_url_with_source',
                args: {
                    'source': frm.doc.enter_source_name
                },
                callback: function (res) {
                    const URL = res.message;
                    if (URL != "") {
                        frappe.db.get_single_value("FH Admission Settings", "urls").then((r) => {
                            let updated_urls = r + "\n" + URL
                            frappe.db.set_value("FH Admission Settings", "FH Admission Settings", "urls", updated_urls).then((r) => { console.log(r) })
                        })
                    }
                }
            })
        }
    },

    onload: function (frm) {
        frappe.call({
            method: 'fh_admission.fh_admission.doctype.fh_admission_settings.fh_admission_settings.generate_html_of_source_urls',
            callback: function (res) {
                console.log(res)
                frm.set_df_property('source_wise_urls', 'options', res.message)
            }
        })
    }
});
