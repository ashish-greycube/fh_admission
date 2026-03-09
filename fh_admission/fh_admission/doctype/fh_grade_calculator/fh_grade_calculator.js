// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

let custom_html_output = ""
let selectedValue = ""

frappe.ui.form.on("FH Grade Calculator", {
    validate(frm) {
        // frm.set_df_property("select_school_choice_list", "options", "")
        // frm.set_df_property("school_choice_list_html", "options", "")
        // frm.set_df_property("select_grade_choice_list", "options", "")
        call_get_grade_type_from_city(frm).then((r) => {
            if (r.message["status"] == 1) {
                // console.log("grade_type value", r.message["types"][0])
                frm.set_value("board", r.message["types"][0]).then(() => {
                    // Calling the Fn which calls PY calculator function
                    call_reccomedation_calculator(frm.doc).then((r) => {

                        console.log(r.message["grade_list"], r.message["school_list"], r.message["unique_school_list"])

                        if (typeof (r.message) != "object") {

                        }

                        // Once the call is executed, we set the HTML Options as r.message
                        frm.set_df_property("html_output", "options", r.message["html"])

                        // we make a grade_list string and add it as options in grade Select
                        let grade_list = r.message["grade_list"]

                        if (grade_list.length == 0) {
                            return
                        }

                        let grade_list_string = ""

                        grade_list_string = "\n" + grade_list.join("\n")
                        frm.set_df_property("select_grade_choice_list", "hidden", 0)
                        // frm.set_df_property("select_grade_choice_list", "reqd", 1)
                        frm.set_df_property("select_grade_choice_list", "options", grade_list_string)
                    })
                })

            } else {
                if (frm.fields_dict.board.has_input) {
                    // Calling the Fn which calls PY calculator function
                    call_reccomedation_calculator(frm.doc).then((r) => {

                        if (typeof (r.message) != "object") {

                        }

                        // Once the call is executed, we set the HTML Options as r.message
                        frm.set_df_property("html_output", "options", r.message["html"])

                        // we make a grade_list string and add it as options in grade Select
                        let grade_list = r.message["grade_list"]

                        if (grade_list.length == 0) {
                            return
                        }

                        let grade_list_string = ""

                        grade_list_string = "\n" + grade_list.join("\n")
                        frm.set_df_property("select_grade_choice_list", "hidden", 0)
                        // frm.set_df_property("select_grade_choice_list", "reqd", 1)
                        frm.set_df_property("select_grade_choice_list", "options", grade_list_string)
                    })
                } else {
                    // frappe.msgprint("Multiple grade types found in city, Select any one")
                    frm.set_df_property("board", "hidden", 0)
                    // frm.set_df_property("board", "reqd", 1)
                    let grade_types_list = r.message["types"].join("\n")
                    // console.log(grade_types_list)
                    frm.set_df_property("board", "options", grade_types_list)
                }

            }
        })

        if (frm.doc.select_school_choice_list == "No School Applicable") {
            frappe.throw("Choose a valid School!")
        }


    },
    select_grade_choice_list(frm) {
        selected_grade_value = frm.doc.select_grade_choice_list
        frm.set_df_property("select_school_choice_list", "options", "")

        if (!selected_grade_value) {
            frm.set_df_property("school_choice_list_html", "options", "Please Select a valid Grade")
            frm.set_df_property("select_school_choice_list", "hidden", "1")
            return
        }

        call_generate_school_choice_rows_html(selected_grade_value, frm).then((r) => {
            frm.set_df_property("select_school_choice_list", "hidden", 0)
            frm.set_df_property("school_choice_list_html", "options", r.message.html)

            // we make a school_list string and add it as options in grade Select
            let school_list = r.message["school_list"]
            let school_list_string = ""
            if (typeof (school_list) == "object") {
                school_list_string = school_list.join("\n")
                frm.set_df_property("select_school_choice_list", "options", school_list_string)
            } else {
                frm.set_df_property("select_school_choice_list", "options", "No School Applicable")
                frm.set_df_property("select_school_choice_list", "hidden", "1")
            }
        })
    },
    calculate(frm) {
        frm.save()
    },
    clear_form(frm) {
        frm.set_value("dob", "")
        frm.set_value("ay", "")
        frm.set_value("city", "")
        frm.set_value("board", "")
        frm.set_value("select_grade_choice_list", "")
        frm.set_value("select_school_choice_list", "")
        frm.set_df_property("html_output", "options", "")
        frm.set_df_property("school_choice_list_html", "options", "")
        // frm.set_df_property("board", "hidden", 1)

        frm.save().then(() => { frm.reload_doc() })

    }
    // refresh(frm) {
    //     frm.set_df_property("select_school_choice_list", "options", "")
    //     frm.set_df_property("school_choice_list_html", "options", "")
    //     frm.set_df_property("select_grade_choice_list", "options", "")
    // }
})


function call_reccomedation_calculator(doc) {
    return frappe.call({
        method: "fh_admission.api.reccomedation_calculator",
        args: {
            "child_dob": doc.dob,
            "city": doc.city,
            "academic_year": doc.ay,
            "grade_type": doc.board
        }
    })
}

function call_generate_school_choice_rows_html(grade, frm) {
    return frappe.call({
        method: "fh_admission.api.generate_school_choice_rows_html",
        args: {
            "selected_grade": grade,
            "academic_year_form": frm.doc.ay,
            "child_dob": frm.doc.dob,
            "city": frm.doc.city,
            "grade_type": frm.doc.board
        }
    })
}


function call_get_grade_type_from_city(frm) {
    return frappe.call({
        method: "fh_admission.api.get_grade_type_from_city",
        args: {
            "city": frm.doc.city
        }
    })
}
