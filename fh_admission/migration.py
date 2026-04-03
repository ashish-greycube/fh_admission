from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.desk.page.setup_wizard.setup_wizard import make_records

def after_migrations():
    custom_fields = {
        "Lead": [
            {
                "insert_after": "fax",
                "fieldtype" : "Link",
                "fieldname": "custom_inquiry_form_reference",
                "label": "Inquiry Form Reference",
                "is_system_generated": 0,
                "is_custom_field": 1,
                "options": "Inquiry Form FH"
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
            }
        ]    
    }

    print('Creating Custom Fields For Lead...')
    for dt, fields in custom_fields.items():
        print("**********\n %s: "% dt, [field.get('fieldname') for field in fields])
    create_custom_fields(custom_fields)