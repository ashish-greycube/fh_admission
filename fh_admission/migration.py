from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.desk.page.setup_wizard.setup_wizard import make_records

def after_migrations():
    custom_fields = {
        "Lead": [
            {
                "insert_after": "custom_campus",
                "fieldtype" : "Link",
                "fieldname": "custom_campus_admin",
                "label": "Campus Admin",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "options": "User",
                "fetch_from": "custom_campus.campus_admin"
            },
            {
                "insert_after": "request_type",
                "fieldtype" : "Data",
                "fieldname": "custom_selected_school",
                "label": "Selected School",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "read_only": 1,
                "hidden": 1
            },
            {
                "insert_after": "custom_selected_school",
                "fieldtype" : "Link",
                "fieldname": "custom_inquiry_form_reference",
                "label": "Inquiry Form Reference",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "options": "Inquiry Form FH",
                "read_only": 1,
            },
            {
                "insert_after": "response_by",
                "fieldtype" : "Select",
                "fieldname": "custom_sla_status",
                "label": "SLA Status",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "options": "\nResponded\nFailed to Respond",
                "read_only": 1,
            },
            {
                "insert_after": "blog_subscriber",
                "fieldtype" : "Tab Break",
                "fieldname": "custom_student_tab",
                "label": "Inquiry Form",
                "is_system_generated": 0,
                "is_custom_field": 1,
            },
            {
                "insert_after": "custom_student_tab",
                "fieldtype" : "Select",
                "fieldname": "custom_city_you_are_seeking_admission",
                "label": "City you are seeking admission in?",
                "options": "\nSurat\nVapi\nAurangabad (CSN)",
                "is_system_generated": 0,
                "is_custom_field": 1,
            },
            {
                "insert_after": "custom_city_you_are_seeking_admission",
                "fieldtype" : "Select",
                "fieldname": "custom_where_are_you_from",
                "label": "Where are you from?",
                "options": "\nIndia\nOutside India",
                "is_system_generated": 0,
                "is_custom_field": 1,
            },
            {
                "insert_after": "custom_where_are_you_from",
                "fieldtype" : "Column Break",
                "fieldname": "custom_col_break_basic",
                "is_system_generated": 0,
                "is_custom_field": 1,
            },
            {
                "insert_after": "custom_col_break_basic",
                "fieldtype" : "Select",
                "fieldname": "custom_select_state",
                "label": "Where are you from?",
                "options": "\nGujarat\nMaharashtra\nNone of the above",
                "is_system_generated": 0,
                "is_custom_field": 1,
            },
            {
                "insert_after": "custom_select_state",
                "fieldtype" : "Data",
                "fieldname": "custom_gujarat_city",
                "label": "Select City",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "depends_on": "eval:doc.custom_select_state=='Gujarat'"
            },
             {
                "insert_after": "custom_gujarat_city",
                "fieldtype" : "Data",
                "fieldname": "custom_maharashtra_city",
                "label": "Select City",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "depends_on": "eval:doc.custom_select_state=='Maharashtra'"
            },
            {
                "fieldname": "custom_parents_details_section",
                "fieldtype": "Section Break",
                "label": "Parents Details",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_maharashtra_city"
            },
            {
                "fieldname": "custom_fathers_first_name",
                "fieldtype": "Data",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_parents_details_section",
                "label": "Father's First Name"
            },
            {
                "fieldname": "custom_fathers_last_name",
                "fieldtype": "Data",
                "label": "Father's Last Name",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_fathers_first_name"
            },
            {
                "fieldname": "custom_fathers_mobile_no",
                "fieldtype": "Data",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_fathers_last_name",
                "label": "Father's Mobile No.",
                "options": "Phone"
            },
            {
                "fieldname": "custom_father_email",
                "fieldtype": "Data",
                "label": "Father Email",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_fathers_mobile_no"
            },
            {
                "fieldname": "custom_column_break_parents",
                "fieldtype": "Column Break",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_father_email"
            },
            {
                "fieldname": "custom_mothers_first_name",
                "fieldtype": "Data",
                "label": "Mother's First Name",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_column_break_parents"
            },
            {
                "fieldname": "custom_mothers_last_name",
                "fieldtype": "Data",
                "label": "Mother's Last Name ",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_mothers_first_name"
            },
            {
                "fieldname": "custom_mothers_mobile_no",
                "fieldtype": "Data",
                "label": "Mother's Mobile No.",
                "options": "Phone",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_mothers_last_name"
            },
            {
                "fieldname": "custom_mothers_email",
                "fieldtype": "Data",
                "label": "Mother's Email",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_mothers_mobile_no"
            },
            {
                "fieldname": "custom_section_break_ref",
                "fieldtype": "Section Break",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_mothers_email"
            },
            {
                "fieldname": "custom_fountain_staff_parent_id",
                "fieldtype": "Data",
                "label": "If You Are A Fountainhead Staff Member, Please Enter Your Staff ID",
                "placeholder": "e.g. FET1370",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_section_break_ref"
            },
            {
                "fieldname": "custom_column_break_ref",
                "fieldtype": "Column Break",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_fountain_staff_parent_id"
            },
            {
                "fieldname": "custom_sibling_student_id",
                "fieldtype": "Data",
                "label": "If The Child's Real Brother Or Sister Is Studying At Fountainhead School(Any Campus), Please Enter The Child's Student ID",
                "placeholder": "e.g. FSK2012001",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_column_break_ref"
            },
             {
                "fieldname": "custom_child_section",
                "fieldtype": "Section Break",
                "label": "Child Details",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_sibling_student_id"
            },
            {
                "fieldname": "custom_child_dob",
                "fieldtype": "Date",
                "label": "Child's DOB",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_child_section"
            },
            {
                "fieldname": "custom_academic_year_applying_for",
                "fieldtype": "Data",
                "label": "Which Academic Year are you applying for?",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_child_dob"
            },
            {
                "fieldname": "custom_current_school_name",
                "fieldtype": "Data",
                "label": "Current School Name (If Applicable)",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_academic_year_applying_for"
            },
            {
                "fieldname": "custom_column_break_child",
                "fieldtype": "Column Break",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_current_school_name"
            },
            {
                "fieldname": "custom_eligible_grade",
                "fieldtype": "Data",
                "label": "Eligible Grade",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_column_break_child"
            },
            {
                "fieldname": "custom_eligible_school",
                "fieldtype": "Data",
                "label": "Eligible School",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "custom_eligible_grade"
            }
        ],    

        "Event": [
            {
                "fieldname": "custom_campus_admin",
                "fieldtype": "Link",
                "label": "Campus Admin",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "insert_after": "reference_doctype",
                "options": "User"
            }
        ]    
    }

    print('Creating Custom Fields For Lead...')
    for dt, fields in custom_fields.items():
        print("**********\n %s: "% dt, [field.get('fieldname') for field in fields])
    create_custom_fields(custom_fields)