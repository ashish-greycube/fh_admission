// Copyright (c) 2026, GreyCube Technologies and contributors
// For license information, please see license.txt

let custom_html_output = ""
let selectedValue = ""

frappe.ui.form.on("FH Grade Calculator", {
    validate(frm) {
        call_get_grade_type_from_city(frm.doc.city).then((r) => {
            if (r.message["status"] == 1) {
                let board_value = r.message["types"][0]
                frm.set_value("board", board_value).then((r) => {
                    console.log(frm, frm.doc.board)
                    call_reccomedation_calculator(frm.doc.dob, frm.doc.city, frm.doc.ay, board_value).then((r) => {
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
                        frm.set_df_property("select_grade_choice_list", "options", grade_list_string)
                    })
                })

            } else {
                if (frm.fields_dict.board.has_input) {
                    // Calling the Fn which calls PY calculator function
                    call_reccomedation_calculator(frm.doc.dob, frm.doc.city, frm.doc.ay, frm.doc.board).then((r) => {

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
                        frm.set_df_property("select_grade_choice_list", "options", grade_list_string)
                    })
                } else {
                    let grade_types_list = r.message["types"].join("\n")
                    frm.set_df_property("board", "options", grade_types_list)
                    if (frm.fields_dict.board.df.options != "") {
                        frm.set_df_property("board", "hidden", 0)
                    }
                }

            }
        })

        if (frm.doc.select_school_choice_list == "No School Applicable") {
            frappe.throw("Choose a valid School!")
        }


    },
    select_grade_choice_list(frm) {
        console.log(frm, frm.doc.board)
        selected_grade_value = frm.doc.select_grade_choice_list
        frm.set_df_property("select_school_choice_list", "options", "")

        if (!selected_grade_value) {
            // frm.set_df_property("school_choice_list_html", "options", "Please Select a valid Grade")
            frm.set_df_property("select_school_choice_list", "hidden", 1)
            return
        }

        call_generate_school_choice_rows_html(selected_grade_value, frm.doc.dob, frm.doc.city, frm.doc.ay, frm.doc.board).then((r) => {
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
                frm.set_df_property("select_school_choice_list", "hidden", 1)
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
        frm.fields_dict.html_output.wrapper.innerHTML = "";
        frm.fields_dict.school_choice_list_html.wrapper.innerHTML = "";
        frm.refresh_field("school_choice_list_html")
        frm.refresh_field("html_output")

        frm.set_df_property("select_grade_choice_list", "hidden", 1)
        frm.save()
    },

    refresh: function (frm) {
        $(".primary-action").remove()
        if (frm.doc.city) {
            call_get_grade_type_from_city(city = frm.doc.city).then((r) => {
                if (r.message["status"] == 1) {
                    let board_value = r.message["types"][0]
                    frm.set_value("board", board_value)
                    frm.refresh_field("board")
                } else {
                    let grade_types_list = r.message["types"].join("\n")
                    frm.set_df_property("board", "options", grade_types_list)
                    if (frm.fields_dict.board.df.options != "") {
                        frm.set_df_property("board", "hidden", 0)
                    }
                }
            })
        }
    },
})


function call_reccomedation_calculator(dob, city, ay, board) {
    console.log(dob, city, ay, board)
    return frappe.call({
        method: "fh_admission.api.reccomedation_calculator",
        args: {
            "child_dob": dob,
            "city": city,
            "academic_year": ay,
            "grade_type": board
        }
    })
}

function call_generate_school_choice_rows_html(grade, dob, city, ay, board) {
    console.log(grade, dob, city, ay, board)
    return frappe.call({
        method: "fh_admission.api.generate_school_choice_rows_html",
        args: {
            "selected_grade": grade,
            "academic_year_form": ay,
            "child_dob": dob,
            "city": city,
            "grade_type": board
        }
    })
}


function call_get_grade_type_from_city(city) {
    return frappe.call({
        method: "fh_admission.api.get_grade_type_from_city",
        args: {
            "city": city
        }
    })
}
