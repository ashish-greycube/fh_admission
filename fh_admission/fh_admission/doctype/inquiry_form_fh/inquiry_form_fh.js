// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Inquiry Form FH", {
    refresh(frm) {
        const child_fields = [
            {
                grade: 'first_child_eligible_grades',
                school: 'first_child_eligible_schools',
                dob: 'first_child_date_of_birth',
            },
            {
                grade: 'second_child_eligible_grades',
                school: 'second_child_eligible_schools',
                dob: 'second_child_date_of_birth',
            },
            {
                grade: 'third_child_eligible_grades',
                school: 'third_child_eligible_schools',
                dob: 'third_child_childs_dob',
            },
            {
                grade: 'fourth_child_eligible_grades',
                school: 'fourth_child_eligible_schools',
                dob: 'fourth_child_childs_dob',
            },
            {
                grade: 'fifth_child_eligible_grades',
                school: 'fifth_child_eligible_schools',
                dob: 'fifth_child_childs_dob',
            }
        ]
        let showButton = false;

        if (frm.doc.city_for_admission && frm.doc.academic_year) {
            child_fields.forEach((child) => {
                if (frm.doc[child.dob] && (!frm.doc[child.grade] || !frm.doc[child.school])) {
                    showButton = true;
                    return
                }
            })
        }

        if (showButton == true) {
            frm.add_custom_button("Send Reminder Message", function () {
                frappe.call({
                    method: "fh_admission.fh_admission.doctype.inquiry_form_fh.inquiry_form_fh.send_reminder_notification",
                    args: {
                        'country_code': frm.doc.country_code,
                        'mobile_no': frm.doc.mobile_no
                    },
                    callback: function (res) {
                        if (res.message) {
                            frappe.msgprint(res.message['message'])
                        }
                    }
                })
            })
        }
    },

    status: function (frm) {
        console.log(frm.doc.status);
    }
});