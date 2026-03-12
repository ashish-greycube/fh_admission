// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

let data = []
frappe.ui.form.on("FH Grade Calculator", {
    refresh: function (frm) {
        $(".primary-action").remove();
    },

    calculate: function (frm) {
        frm.save()
    },

    clear_form(frm) {
        frm.set_value("dob", "")
        frm.set_value("ay", "")
        frm.set_value("city", "")
        frm.set_value("board", "")
        frm.set_value("school_type", "");
        frm.set_value("select_grade", "")
        frm.set_value("select_school", "")
        frm.set_df_property("html_output", "options", "")
        frm.set_df_property("school_choice_list_html", "options", "")
        frm.fields_dict.html_output.wrapper.innerHTML = "";
        frm.fields_dict.school_choice_list_html.wrapper.innerHTML = "";
        frm.refresh_field("school_choice_list_html")
        frm.refresh_field("html_output")

        frm.set_df_property("select_grade", "hidden", 1)
        frm.set_df_property("select_school", "hidden", 1)
        frm.set_df_property("school_type", "hidden", 1)
        frm.save()
    },

    validate: function (frm) {
        if (frm.doc.dob && frm.doc.ay && frm.doc.city) {
            frappe.call({
                method: "fh_admission.api.get_eligible_grades",
                args: {
                    'child_dob': frm.doc.dob,
                    'child_academic_year': frm.doc.ay,
                    'city': frm.doc.city,
                },
                callback: function (res) {
                    data = res.message;
                    get_html(data).then((res) => {
                        if (res.message) {
                            frm.set_df_property('html_output', 'options', res.message)
                            frm.set_df_property('html_output', 'hidden', 0)
                        }
                    })

                    get_unique_grades(data).then((res) => {
                        var grade_options = "\n" + res.message.join('\n');
                        frm.set_df_property('select_grade', 'options', grade_options);
                        frm.set_df_property('select_grade', 'hidden', 0);
                        frm.set_value('select_grade', '');
                    })
                }
            })
        }
    },

    select_grade: function (frm) {
        if (frm.doc.select_grade != '') {
            frappe.call({
                method: "fh_admission.api.get_unique_schools_based_on_grade",
                args: {
                    'query_results': data,
                    'grade': frm.doc.select_grade,
                },
                callback: function (res) {
                    var school_options = "\n" + res.message.join('\n');
                    frm.set_df_property('select_school', 'options', school_options);
                    frm.set_df_property('select_school', 'hidden', 0);
                    frm.set_value('select_school', '');
                }
            })
        }
    }
})

function get_unique_grades(data) {
    return frappe.call({
        method: "fh_admission.api.get_unique_grades",
        args: {
            'query_results': data,
        },
    })
}

function get_html(data) {
    return frappe.call({
        method: "fh_admission.api.generate_eligibility_html_tables",
        args: {
            'data': data,
        },
    })
}