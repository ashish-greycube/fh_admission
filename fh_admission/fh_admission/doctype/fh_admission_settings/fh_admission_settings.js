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
                    const valid_source = res.message;
                    if (valid_source) {
                        let exists = (frm.doc.url_sources || []).some(row => row.source === valid_source);
                        if (!exists) {
                            let row = frm.add_child("url_sources", {
                                "source": valid_source
                            });
                            frm.refresh_field("url_sources");
                        }
                        frm.save()
                        frm.reload_doc();
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
