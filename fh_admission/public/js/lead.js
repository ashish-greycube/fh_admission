frappe.ui.form.on("Lead", {
    refresh: function (frm) {
        frappe.call({
            method: "fh_admission.api.check_logged_in_user_role",
            callback: function (res) {
                if (res) {
                    if (res.message == "PRO User") {
                        frm.set_df_property("lead_owner", "read_only", 1)
                    } else {
                        frm.set_df_property("lead_owner", "read_only", 0)
                    }
                }
            }
        })
        frm.trigger("assigned_to_filter_for_new_task");
        frm.trigger("assigned_to_filter_for_new_event");
    },

    onload_post_render: function (frm) {
        if (frm.doc.custom_campus) {
            frm.set_query("lead_owner", function (frm) {
                console.log("Inside set query")
                return {
                    query: "fh_admission.api.filter_lead_owner_based_on_campus_for_campus_admin_role",
                    filters: {
                        "campus": cur_frm.doc.custom_campus
                    }
                }
            })
        }
        frm.trigger("assigned_to_filter_for_new_task");
        frm.trigger("assigned_to_filter_for_new_event");
    },

    assigned_to_filter_for_new_task: function (frm) {
        $(document).off("click", ".new-task-btn");
        $(document).on("click", ".new-task-btn", function () {
            if (!frm.doc.custom_campus) { return }
            setTimeout(() => {
                let dialog = frappe.ui.open_dialogs[0];
                if (dialog && dialog.fields_dict) {
                    let assigned_to_field = dialog.fields_dict.assigned_to;
                    if (assigned_to_field) {
                        frappe.call({
                            method: "fh_admission.api.check_logged_in_user_role",
                            callback: function (res) {
                                if (res) {
                                    if (res.message == "PRO User") {
                                        assigned_to_field.set_value(frappe.session.user_email)
                                        assigned_to_field.df.read_only = 1
                                        assigned_to_field.refresh();
                                    } else {
                                        assigned_to_field.get_query = function () {
                                            console.log("Inside Query")
                                            return {
                                                query: "fh_admission.api.filter_lead_owner_based_on_campus_for_campus_admin_role",
                                                filters: {
                                                    "campus": frm.doc.custom_campus
                                                }
                                            };
                                        };
                                    }
                                }
                            }
                        })
                        assigned_to_field.refresh();
                    }
                }
            }, 500);
        })
    },

    assigned_to_filter_for_new_event: function (frm) {
        $(document).off("click", ".new-event-btn");
        $(document).on("click", ".new-event-btn", function () {
            if (!frm.doc.custom_campus) { return }
            setTimeout(() => {
                let dialog = frappe.ui.open_dialogs[0];
                if (dialog && dialog.fields_dict) {
                    let assigned_to_field = dialog.fields_dict.assigned_to;
                    if (assigned_to_field) {
                        frappe.call({
                            method: "fh_admission.api.check_logged_in_user_role",
                            callback: function (res) {
                                if (res) {
                                    if (res.message == "PRO User") {
                                        assigned_to_field.set_value(frappe.session.user_email)
                                        assigned_to_field.df.read_only = 1
                                        assigned_to_field.refresh();
                                    } else {
                                        assigned_to_field.get_query = function () {
                                            console.log("Inside Query")
                                            return {
                                                query: "fh_admission.api.filter_lead_owner_based_on_campus_for_campus_admin_role",
                                                filters: {
                                                    "campus": frm.doc.custom_campus
                                                }
                                            };
                                        };
                                    }
                                }
                            }
                        })
                        assigned_to_field.refresh();
                    }
                }
            }, 500);
        })
    }
})