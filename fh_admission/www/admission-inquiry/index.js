const inputs = document.querySelectorAll(".otp_input_box")
const button = document.querySelector("button")
const mobile = document.getElementById("mobile")
const expire = document.getElementById("expire")

inputs[0].focus()

// send OTP button will be disabled until 10 digit are enetered
mobile.addEventListener("keyup", function (e) {
    if (mobile.value.length == 10) {
        $("#send-otp").prop("disabled", false)
    }
})

for (let i = 0; i < inputs.length; i++) {
    const input = inputs[i];
    input.addEventListener("input", function () {
        // handling normal input
        if (input.value.length == 1 && i + 1 < inputs.length) {
            inputs[i + 1].focus();
        }

        // if a value is pasted, put each character to each of the next input
        if (input.value.length > 1) {
            // sanitise input
            if (isNaN(input.value)) {
                input.value = "";
                return;
            }

            // split characters to array
            const chars = input.value.split('');

            for (let pos = 0; pos < chars.length; pos++) {
                // if length exceeded the number of inputs, stop
                if (pos + i >= inputs.length) break;

                // paste value
                let targetInput = inputs[pos + i];
                targetInput.value = chars[pos];
            }

            // focus the input next to the last pasted character
            let focus_index = Math.min(inputs.length - 1, i + chars.length);
            inputs[focus_index].focus();
        }
    });

    input.addEventListener("keydown", function (e) {
        // left button
        if (e.keyCode == 37) {
            if (i > 0) {
                e.preventDefault();
                inputs[i - 1].focus();
                inputs[i - 1].select();
            }
            return;
        }

        // right button
        if (e.keyCode == 39) {
            if (i + 1 < inputs.length) {
                e.preventDefault();
                inputs[i + 1].focus();
                inputs[i + 1].select();
            }
            return;
        }

        // backspace button
        if (e.keyCode == 8 && input.value == '' && i != 0) {
            // shift next values towards the left
            for (let pos = i; pos < inputs.length - 1; pos++) {
                inputs[pos].value = inputs[pos + 1].value;
            }

            // clear previous box and focus on it
            inputs[i - 1].value = '';
            inputs[i - 1].focus();
            return;
        }

        // delete button
        if (e.keyCode == 46 && i != inputs.length - 1) {
            // shift next values towards the left
            for (let pos = i; pos < inputs.length - 1; pos++) {
                inputs[pos].value = inputs[pos + 1].value;
            }

            // clear the last box
            inputs[inputs.length - 1].value = '';

            // select current input
            input.select();

            // disallow the event delete the new value
            e.preventDefault();
            return;
        }
    })
}

frappe.ready(function () {
    // Generate OTP and send it to Mobile no.
    $(".send-otp").on("click", () => {
        let country_code = $("#country_code").val()
        let mobile_no = $("#mobile").val()
        generate_otp(country_code, mobile_no).then((r) => {
            console.log(r.message)
            if (r.message["success"]) {
                frappe.show_alert({
                    message: r.message["message"],
                    indicator: "green"
                })
            } else {
                frappe.show_alert({
                    message: r.message['message'],
                    indicator: "red",
                    title: "Technical Issue"
                })
            }
        })

        $('.otp_class').each(function (index) {
            $(this).css("display", "flex")
        });
        $(".send-otp").css("display", "none")
    })

    // Verify the OTP
    $(".verify-otp").on("click", () => {
        let country_code = $("#country_code").val()
        let mobile_no = $("#mobile").val()

        let OTP = ""
        $('.otp_input_box').each(function (index) {
            OTP += $(this).val()
        });

        verify_otp(country_code, mobile_no, OTP).then((r) => {
            if (r.message["success"]) {
                frappe.show_alert(r.message['message'], indicator = "green")
                generate_new_doc_on_otp_verification(mobile_no, country_code).then((r) => {
                    console.log(r)
                    window.location.href = r.message
                })
            } else {
                $(".error-msg").empty()
                $(".verify-otp").after(`<p style="color:red; font-weight:bold; font-size:14px; text-align:left !important; margin-top:10px;" class="error-msg">${r.message['message']}</p>`)
                // frappe.throw({
                //     message: r.message['message'],
                //     indicator: "red",
                //     title: "Invalid OTP"
                // })
            }
        })
    })

    $("a#request_otp_again").on("click", () => {
        let country_code = $("#country_code").val();
        let mobile_no = $("#mobile").val()
        generate_otp(country_code, mobile_no).then((r) => {
            console.log(r.message["otp"])
            if (r.message["success"]) {
                frappe.show_alert({
                    message: r.message["message"],
                    indicator: "green"
                })
            }
        })

        $('.otp_class').each(function (index) {
            $(this).css("display", "flex")
            $(".otp_input_box").val('')
        });
        $(".send-otp").css("display", "none")
    });
})

// OTP Generation and sending function
function generate_otp(country_code, mobile_no) {
    $("p#not_receive_code").css("display", "");
    $("a#request_otp_again").css("display", "");
    return frappe.call({
        method: "fh_admission.www.admission-inquiry.index.generate_otp_for_phone",
        args: {
            "country_code": country_code,
            "phone": mobile_no
        },
        callback: (r) => {
            return r.message
        }
    })

}

// OTP verification function
function verify_otp(country_code, mobile_no, otp) {
    return frappe.call({
        method: "fh_admission.www.admission-inquiry.index.verify_otp_for_phone",
        args: {
            "country_code": country_code,
            "phone": mobile_no,
            "otp": otp
        },
        callback: (r) => {
            return r.message
        }
    })
}

// generates new doctype from mobile number
function generate_new_doc_on_otp_verification(mobile_no, country_code) {
    return frappe.call({
        method: "fh_admission.www.admission-inquiry.index.generate_new_doc_on_otp_verification",
        args: {
            "primary_number": mobile_no,
            "country_code": country_code
        },
        callback: function (r) {
            console.log(r.message)
            return r.message
        },
    })
}