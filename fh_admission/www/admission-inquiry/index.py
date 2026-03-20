import json
import frappe
import string
import random
import requests
from frappe.auth import LoginManager

REDIS_PREFIX = "OTP"
URL_SOURCE = frappe.form_dict["source"] if "source" in frappe.form_dict else ""

def get_context(context):
    return context

def random_string_generator(str_size, allowed_chars):
    return "".join(random.choice(allowed_chars) for x in range(str_size))

@frappe.whitelist(allow_guest = True)
def generate_otp_for_phone(country_code, phone):
    payload = {
        "success": False,
        "message": None,
        "otp": None
    }
    mobile_no = f"{country_code} {phone}"
    # otp = "123456"
    otp = random_string_generator(6, string.digits)

    frappe.cache().set(f"{REDIS_PREFIX}:{mobile_no}", otp)
    try:
        response = send_otp_to_user_whatsapp_using_interakt_api(country_code, phone, otp)
        if response and response['success'] == True:
            payload.update({
                "success": True,
                "message": "OTP(One time passowrd) is sent on No {0}".format(phone),
                "otp": otp
            })
        elif response and response['success'] == False:
            payload.update({
                "message": response['message']
            })
    except Exception as e:
        payload.update({
            "message": str(e)
        })
    return payload

@frappe.whitelist(allow_guest = True)
def verify_otp_for_phone(country_code, phone, otp):
    payload = {
        "success": False,
        "message": None,
    }
  
    phone = f"{country_code} {phone}"
    key = f"{REDIS_PREFIX}:{phone}"
    stored_otp = frappe.cache().get(key).decode("utf-8")
    if not stored_otp == otp:
        payload.update({
            "message": "The OTP you entered is incorrect. Kindly re-enter the correct code."
        })
        return payload
    else:
        payload.update({
            "message": "OTP Verfied Successfully.",
            "success": True,
        })

        # Delete stored OTP
        frappe.cache().delete_key(key)

        frappe.local.login_manager = LoginManager()
        frappe.local.login_manager.login_as("test@abc.com")

        return payload

@frappe.whitelist(allow_guest=True)
def generate_new_doc_on_otp_verification(primary_number, country_code):
    if frappe.db.exists("Inquiry Form FH", primary_number):
        doc = frappe.get_doc("Inquiry Form FH", primary_number)
    else:
        doc = frappe.new_doc("Inquiry Form FH")
        doc.country_code = country_code
        doc.mobile_no = primary_number
        doc.source = URL_SOURCE.replace("_", " ").title()
        doc.save()

    redirect_url = "/admission-inquiry/form/{0}/edit".format(doc.name)
    return redirect_url

def send_otp_to_user_whatsapp_using_interakt_api(country_code, phone, otp):
    output = {"success": False, "message": "It seems there are some technical issue. Please Try again after some time.",}
    admission_settings = frappe.get_doc("FH Admission Settings")
    api_key = admission_settings.get_password(fieldname="interakt_api_key", raise_exception=False)

    if api_key:
        URL = "https://api.interakt.ai/v1/public/message/"

        payload = json.dumps({
            "countryCode": country_code,
            "phoneNumber": phone,
            "callbackData": "Message Sent!",
            "type": "Template",
            "template": {
                "name": "inquiry_form_otp",
                "languageCode": "en",
                "bodyValues": [
                    otp
                ],
                "buttonValues": {
                    "0": [
                        otp
                    ]
                }
            },
            "fallback": [
                {
                    "channel": "sms",
                    "sender_id": "sms_header",
                    "pe_id": "sms_entity_id",
                    "provider_name": "default",
                    "content": {
                        "message": "Greetings from Protego Service LLP! Your verification code is {{1}}. Do not share this code with anyone.",
                        "dlt_te_id": "sms_template_id",
                        "variables": [
                            otp
                        ]
                    }
                }
            ]
        })

        headers = {
            'Authorization': 'Basic {0}'.format(api_key),
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", URL, headers=headers, data=payload)
        res = response.json()
        if res['result'] == True:
            output.update({
                "success": True,
                "message": "OTP(One time passowrd) is sent on No {0}".format(phone),
            })
        return output
    else:
        output.update({
            "success": False,
            "message": "It seems there are some technical issue. Please Try again after some time.",
        })
    return output