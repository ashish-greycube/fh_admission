var data = [];

// Function To Save Data Of WebForm Fields In Doctype.
function save_data_to_doc_on_change(fieldname, value) {
	if (value == "") {
		frappe.throw("Please select or enter valid value.")
	}
	frappe.call({
		method: "fh_admission.fh_admission.web_form.admission_inquiry.admission_inquiry.save_data_to_doc_on_change",
		args: {
			"mobile_no": frappe.web_form.doc.mobile_no,
			"fieldname": fieldname,
			"value": value
		},
		callback: function (res) {
			if (res && res.message == true) {
				if (fieldname.startsWith("first")) {
					frappe.web_form.set_value('first_child_eligible_grades', null)
					frappe.web_form.set_value('first_child_eligible_schools', null)
					frappe.web_form.set_value("first_child_options", null)
					frappe.web_form.set_value("first_child_school_options", null)
				} else if (fieldname.startsWith("second")) {
					frappe.web_form.set_value('second_child_eligible_grades', null)
					frappe.web_form.set_value('second_child_eligible_schools', null)
					frappe.web_form.set_value("second_child_options", null)
					frappe.web_form.set_value("second_child_school_options", null)
				} else if (fieldname.startsWith("third")) {
					frappe.web_form.set_value('third_child_eligible_grades', null)
					frappe.web_form.set_value('third_child_eligible_schools', null)
					frappe.web_form.set_value("third_child_options", null)
					frappe.web_form.set_value("third_child_school_options", null)
				} else if (fieldname.startsWith("fourth")) {
					frappe.web_form.set_value('fourth_child_eligible_grades', null)
					frappe.web_form.set_value('fourth_child_eligible_schools', null)
					frappe.web_form.set_value("fourth_child_options", null)
					frappe.web_form.set_value("fourth_child_school_options", null)
				} else if (fieldname.startsWith("fifth")) {
					frappe.web_form.set_value('fifth_child_eligible_grades', null)
					frappe.web_form.set_value('fifth_child_eligible_schools', null)
					frappe.web_form.set_value("fifth_child_options", null)
					frappe.web_form.set_value("fifth_child_school_options", null)
				}
			}
		}
	})

	bindEligibilityButtonEventOnLoad();
}


// Function To Get Unique Grades From Server Side.
function get_unique_grades(data) {
	return frappe.call({
		method: "fh_admission.api.get_unique_grades",
		args: {
			'query_results': data,
		},
	})
}


// Function To Get HTML Of Eligibile Schools and All Schools In City From Server Side.
function get_html(data) {
	return frappe.call({
		method: "fh_admission.api.generate_eligibility_html_tables",
		args: {
			'data': data,
		},
	})
}


// Function To Run On Every Child's Check Eligibility Call.
function check_eligibility_criteria_and_set_field_options(child_dob, child_academic_year, city, grade_fieldname, school_fieldname, html_fieldname) {
	frappe.web_form.set_value(grade_fieldname, '');
	frappe.web_form.set_value(school_fieldname, '');
	frappe.call({
		method: "fh_admission.api.get_eligible_grades",
		args: {
			'child_dob': child_dob,
			'child_academic_year': child_academic_year,
			'city': city,
		},
		callback: function (res) {
			data = res.message;
			get_html(data).then((res) => {
				if (res.message) {
					$(".eligibility-criteria").empty()
					$(html_fieldname).after(res.message)
				}
			})

			get_unique_grades(data).then((res) => {
				if (res.message.length > 0) {
					var grade_options = "\n" + res.message.join('\n');
					store_grade_and_school_options_for_future_ref(grade_fieldname, grade_options)
					frappe.web_form.set_df_property(grade_fieldname, 'options', grade_options);
					frappe.web_form.set_df_property(grade_fieldname, 'hidden', 0);
					frappe.web_form.set_df_property(grade_fieldname, 'depends_on', `eval:doc.${grade_fieldname}==''||doc.${grade_fieldname}!='';`);
					frappe.web_form.set_df_property(school_fieldname, 'depends_on', `eval:doc.${school_fieldname}==''||doc.${school_fieldname}!='';`);
					if (res.message.length == 1) {
						frappe.web_form.set_value(grade_fieldname, res.message[0])
						save_data_to_doc_on_change(grade_fieldname, res.message[0])
					}
				} else {
					frappe.web_form.set_df_property(grade_fieldname, 'hidden', 1);
				}
			})
		}
	})

	frappe.web_form.on(grade_fieldname, (field, value) => {
		frappe.call({
			method: "fh_admission.api.get_unique_schools_based_on_grade",
			args: {
				'query_results': data,
				'grade': frappe.web_form.get_value(grade_fieldname),
			},
			callback: function (res) {
				var school_options = "\n" + res.message.join('\n');
				store_grade_and_school_options_for_future_ref(grade_fieldname, null, school_options);
				frappe.web_form.set_df_property(school_fieldname, 'options', school_options);
				frappe.web_form.set_df_property(school_fieldname, 'hidden', 0);

				if (res.message.length == 1) {
					frappe.web_form.set_value(school_fieldname, res.message[0])
					save_data_to_doc_on_change(school_fieldname, res.message[0])
				} else {
					frappe.web_form.set_value(school_fieldname, '');
				}
			}
		})
	});
}


// Function To Store Grade & School Options Locally
function store_grade_and_school_options_for_future_ref(grade_fieldname, grade_options = null, school_options = null) {
	if (grade_fieldname.startsWith("first")) {
		if (grade_options != null) frappe.web_form.set_value("first_child_options", grade_options)
		if (school_options != null) frappe.web_form.set_value("first_child_school_options", school_options)
	} else if (grade_fieldname.startsWith("second")) {
		if (grade_options != null) frappe.web_form.set_value("second_child_options", grade_options)
		if (school_options != null) frappe.web_form.set_value("second_child_school_options", school_options)
	} else if (grade_fieldname.startsWith("third")) {
		if (grade_options != null) frappe.web_form.set_value("third_child_options", grade_options)
		if (school_options != null) frappe.web_form.set_value("third_child_school_options", school_options)
	} else if (grade_fieldname.startsWith("fourth")) {
		if (grade_options != null) frappe.web_form.set_value("fourth_child_options", grade_options)
		if (school_options != null) frappe.web_form.set_value("fourth_child_school_options", school_options)
	} else if (grade_fieldname.startsWith("fifth")) {
		if (grade_options != null) frappe.web_form.set_value("fifth_child_options", grade_options)
		if (school_options != null) frappe.web_form.set_value("fifth_child_school_options", school_options)
	}
}


// Function to set Eligible Grade & School Values On Load
function set_school_and_grade_values_on_load() {
	let keys = [
		'first_child_eligible_grades', 'first_child_eligible_schools',
		'second_child_eligible_grades', 'second_child_eligible_schools',
		'third_child_eligible_grades', 'third_child_eligible_schools',
		'fourth_child_eligible_grades', 'fourth_child_eligible_schools',
		'fifth_child_eligible_grades', 'fifth_child_eligible_schools'
	]
	let options_keys = [
		'first_child_options', 'first_child_school_options',
		'second_child_options', 'second_child_school_options',
		'third_child_options', 'third_child_school_options',
		'fourth_child_options', 'fourth_child_school_options',
		'fifth_child_options', 'fifth_child_school_options'
	]


	options_keys.forEach((value, index) => {
		if (frappe.web_form.get_value(value) != null) {
			frappe.web_form.set_df_property(keys[index], "options", frappe.web_form.get_value(value))
		}
	})

	let docname = frappe.web_form.doc.mobile_no;
	frappe.call({
		method: "fh_admission.fh_admission.web_form.admission_inquiry.admission_inquiry.set_school_and_grade_values_on_load",
		args: {
			"docname": docname
		},
		callback: function (res) {
			if (res.message && res.message != {}) {
				console.log(res.message)
				for (let key in keys) {
					frappe.web_form.set_value(key, res.message[0][key])
				}

				if (res.message[1] == 2) {
					frappe.web_form.set_value("do_you_want_to_add_child_second", 1)
				} else if (res.message[1] == 3) {
					frappe.web_form.set_value("do_you_want_to_add_child_second", 1)
					frappe.web_form.set_value("do_you_want_to_add_child_third", 1)
				} else if (res.message[1] == 4) {
					frappe.web_form.set_value("do_you_want_to_add_child_second", 1)
					frappe.web_form.set_value("do_you_want_to_add_child_third", 1)
					frappe.web_form.set_value("do_you_want_to_add_another_child_fourth", 1)
				} else if (res.message[1] == 5) {
					frappe.web_form.set_value("do_you_want_to_add_child_second", 1)
					frappe.web_form.set_value("do_you_want_to_add_child_third", 1)
					frappe.web_form.set_value("do_you_want_to_add_another_child_fourth", 1)
					frappe.web_form.set_value("do_you_want_to_add_another_child_fifth", 1)
				}
			}
		}
	})
}


frappe.ready(function () {
	let form_initialized = false;

	// Change Status To Completed On Web Form Submission
	$(".submit-btn").on("click", () => {
		frappe.call({
			method: "fh_admission.fh_admission.web_form.admission_inquiry.admission_inquiry.change_status_of_doc_on_form_submit_and_send_message",
			args: {
				"docname": frappe.web_form.doc.mobile_no,
				"webform_data": frappe.web_form.doc
			}
		})
	})

	setTimeout(() => {
		set_school_and_grade_values_on_load()
		form_initialized = true;
	}, 2000);

	// Save Field Data On Change Of Field Value
	frappe.web_form.on('email_id', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));

	frappe.web_form.on('where_are_you_from', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('state', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('select_gujarat_city', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('select_maharashtra_city', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('city_for_admission', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));

	frappe.web_form.on('fathers_first_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fathers_last_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fathers_mobile_no', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('father_email', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('mothers_first_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('mothers_last_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('mothers_mobile_no', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('mothers_email', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fountain_staff_parent_id', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('sibling_student_id', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));

	frappe.web_form.on('academic_year', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('first_child_first_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('first_child_middle_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('first_child_last_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('first_child_gender', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('first_child_date_of_birth', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('first_child_current_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('first_child_eligible_schools', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('first_child_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('do_you_want_to_add_child_second', (field, value) => { if (form_initialized == true) { save_data_to_doc_on_change(field.df.fieldname, value) } });

	frappe.web_form.on('second_child_academic_year', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_first_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_middle_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_last_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_gender', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_date_of_birth', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_current_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_eligible_schools', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('do_you_want_to_add_child_third', (field, value) => { if (form_initialized == true) { save_data_to_doc_on_change(field.df.fieldname, value) } });
	frappe.web_form.on('second_child_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));

	frappe.web_form.on('third_child_academic_year', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_first_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_middle_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_last_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_gender', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_childs_dob', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_current_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_eligible_schools', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('do_you_want_to_add_another_child_fourth', (field, value) => { if (form_initialized == true) { save_data_to_doc_on_change(field.df.fieldname, value) } });
	frappe.web_form.on('third_child_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));

	frappe.web_form.on('fourth_child_academic_year', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_first_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_middle_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_last_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_gender', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_childs_dob', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_current_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_eligible_schools', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('do_you_want_to_add_another_child_fifth', (field, value) => { if (form_initialized == true) { save_data_to_doc_on_change(field.df.fieldname, value) } });
	frappe.web_form.on('fourth_child_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));

	frappe.web_form.on('fifth_child_academic_year', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fifth_child_first_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fifth_child_middle_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fifth_child_last_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fifth_child_gender', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fifth_child_childs_dob', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fifth_child_current_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fifth_child_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fifth_child_eligible_schools', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));

	frappe.web_form.on('first_child_options', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('first_child_school_options', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_options', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_school_options', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_options', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_school_options', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_options', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_school_options', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fifth_child_options', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fifth_child_school_options', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));

	$('select[data-fieldname="first_child_eligible_grades"]').on("change", () => save_data_to_doc_on_change("first_child_eligible_grades", frappe.web_form.get_value("first_child_eligible_grades")));
	$('select[data-fieldname="second_child_eligible_grades"]').on("change", () => save_data_to_doc_on_change("second_child_eligible_grades", frappe.web_form.get_value("second_child_eligible_grades")));
	$('select[data-fieldname="third_child_eligible_grades"]').on("change", () => save_data_to_doc_on_change("third_child_eligible_grades", frappe.web_form.get_value("third_child_eligible_grades")));
	$('select[data-fieldname="fourth_child_eligible_grades"]').on("change", () => save_data_to_doc_on_change("fourth_child_eligible_grades", frappe.web_form.get_value("fourth_child_eligible_grades")));
	$('select[data-fieldname="fifth_child_eligible_grades"]').on("change", () => save_data_to_doc_on_change("fifth_child_eligible_grades", frappe.web_form.get_value("fifth_child_eligible_grades")));

	// Bind Event OnLoad
	bindEligibilityButtonEventOnLoad();

	// Set All Schools On Load
	setAllSchoolsOnLoad();
});

function bindEligibilityButtonEventOnLoad() {
	$(document).find("#first_child_check_eligibility").on("click", () => {
		if (frappe.web_form.get_value("first_child_date_of_birth") == undefined || frappe.web_form.get_value("academic_year") == '' || frappe.web_form.get_value("city_for_admission") == '') {
			let message = ""
			if (frappe.web_form.get_value("first_child_date_of_birth") == undefined) message += "<li><b>Child's DOB</b></li>"
			if (frappe.web_form.get_value("academic_year") == '') message += "<li><b>Which Acadamic Year are you applying for?</b></li>"
			if (frappe.web_form.get_value("city_for_admission") == '') message += "<li><b>City you are seeking admission in?</b></li>"
			frappe.throw({
				message: `Following fields have missing values:<br><br> <ul>${message}</ul>`,
				title: "Missing Values Required",
			})
		} else {
			check_eligibility_criteria_and_set_field_options(
				frappe.web_form.get_value("first_child_date_of_birth"),
				frappe.web_form.get_value("academic_year"),
				frappe.web_form.get_value("city_for_admission"),
				'first_child_eligible_grades',
				'first_child_eligible_schools',
				'#first_child_check_eligibility'
			)
		}
	})

	$(document).find("#second_child_check_eligibility").on("click", () => {
		console.log("Checking Second Child Eligibility.....")
		if (frappe.web_form.get_value("second_child_date_of_birth") == undefined || frappe.web_form.get_value("second_child_academic_year") == '' || frappe.web_form.get_value("city_for_admission") == '') {
			let message = ""
			if (frappe.web_form.get_value("second_child_date_of_birth") == undefined) message += "<li><b>Child's DOB</b></li>"
			if (frappe.web_form.get_value("second_child_academic_year") == '') message += "<li><b>Which Acadamic Year are you applying for?</b></li>"
			if (frappe.web_form.get_value("city_for_admission") == '') message += "<li><b>City you are seeking admission in?</b></li>"
			frappe.throw({
				message: `Following fields have missing values:<br><br> <ul>${message}</ul>`,
				title: "Missing Values Required",
			})
		} else {
			check_eligibility_criteria_and_set_field_options(
				frappe.web_form.get_value("second_child_date_of_birth"),
				frappe.web_form.get_value("second_child_academic_year"),
				frappe.web_form.get_value("city_for_admission"),
				'second_child_eligible_grades',
				'second_child_eligible_schools',
				"#second_child_check_eligibility"
			)
		}
	})

	$(document).find("#third_child_check_eligibility").on("click", () => {
		if (frappe.web_form.get_value("third_child_childs_dob") == undefined || frappe.web_form.get_value("third_child_academic_year") == '' || frappe.web_form.get_value("city_for_admission") == '') {
			let message = ""
			if (frappe.web_form.get_value("third_child_childs_dob") == undefined) message += "<li><b>Child's DOB</b></li>"
			if (frappe.web_form.get_value("third_child_academic_year") == '') message += "<li><b>Which Acadamic Year are you applying for?</b></li>"
			if (frappe.web_form.get_value("city_for_admission") == '') message += "<li><b>City you are seeking admission in?</b></li>"
			frappe.throw({
				message: `Following fields have missing values:<br><br> <ul>${message}</ul>`,
				title: "Missing Values Required",
			})
		} else {
			check_eligibility_criteria_and_set_field_options(
				frappe.web_form.get_value("third_child_childs_dob"),
				frappe.web_form.get_value("third_child_academic_year"),
				frappe.web_form.get_value("city_for_admission"),
				'third_child_eligible_grades',
				'third_child_eligible_schools',
				"#third_child_check_eligibility"
			)
		}
	})

	$(document).find("#fourth_child_check_eligibility").on("click", () => {
		if (frappe.web_form.get_value("fourth_child_childs_dob") == undefined || frappe.web_form.get_value("fourth_child_academic_year") == '' || frappe.web_form.get_value("city_for_admission") == '') {
			let message = ""
			if (frappe.web_form.get_value("fourth_child_childs_dob") == undefined) message += "<li><b>Child's DOB</b></li>"
			if (frappe.web_form.get_value("fourth_child_academic_year") == '') message += "<li><b>Which Acadamic Year are you applying for?</b></li>"
			if (frappe.web_form.get_value("city_for_admission") == '') message += "<li><b>City you are seeking admission in?</b></li>"
			frappe.throw({
				message: `Following fields have missing values:<br><br> <ul>${message}</ul>`,
				title: "Missing Values Required",
			})
		} else {
			check_eligibility_criteria_and_set_field_options(
				frappe.web_form.get_value("fourth_child_childs_dob"),
				frappe.web_form.get_value("fourth_child_academic_year"),
				frappe.web_form.get_value("city_for_admission"),
				'fourth_child_eligible_grades',
				'fourth_child_eligible_schools',
				"#fourth_child_check_eligibility"
			)
		}
	})

	$(document).find("#fifth_child_check_eligibility").on("click", () => {
		if (frappe.web_form.get_value("fifth_child_childs_dob") == undefined || frappe.web_form.get_value("fifth_child_academic_year") == '' || frappe.web_form.get_value("city_for_admission") == '') {
			let message = ""
			if (frappe.web_form.get_value("fifth_child_childs_dob") == undefined) message += "<li><b>Child's DOB</b></li>"
			if (frappe.web_form.get_value("fifth_child_academic_year") == '') message += "<li><b>Which Acadamic Year are you applying for?</b></li>"
			if (frappe.web_form.get_value("city_for_admission") == '') message += "<li><b>City you are seeking admission in?</b></li>"
			frappe.throw({
				message: `Following fields have missing values:<br><br> <ul>${message}</ul>`,
				title: "Missing Values Required",
			})
		} else {
			check_eligibility_criteria_and_set_field_options(
				frappe.web_form.get_value("fifth_child_childs_dob"),
				frappe.web_form.get_value("fifth_child_academic_year"),
				frappe.web_form.get_value("city_for_admission"),
				'fifth_child_eligible_grades',
				'fifth_child_eligible_schools',
				"#fifth_child_check_eligibility"
			)
		}
	})
}

function setAllSchoolsOnLoad() {
	frappe.call({
		method: "fh_admission.fh_admission.web_form.admission_inquiry.admission_inquiry.get_html_of_all_schools",
		args: {},
		callback: function (res) {
			if (res) {
				$(".all-schools").after(res.message)
			}
		}
	})
}