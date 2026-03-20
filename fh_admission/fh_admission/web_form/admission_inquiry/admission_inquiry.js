var data = [];

// Function To Save Data Of WebForm Fields In Doctype.
function save_data_to_doc_on_change(fieldname, value) {
	frappe.call({
		method: "fh_admission.fh_admission.web_form.admission_inquiry.admission_inquiry.save_data_to_doc_on_change",
		args: {
			"mobile_no": frappe.web_form.doc.mobile_no,
			"fieldname": fieldname,
			"value": value
		}
	})
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
				var grade_options = "\n" + res.message.join('\n');
				store_grade_and_school_options_for_future_ref(grade_fieldname, grade_options)
				frappe.web_form.set_df_property(grade_fieldname, 'options', grade_options);
				frappe.web_form.set_df_property(grade_fieldname, 'hidden', 0);
				frappe.web_form.set_df_property(grade_fieldname, 'depends_on', `eval:doc.${grade_fieldname}==''||doc.${grade_fieldname}!='';`);
				if (res.message.length == 1) {
					frappe.web_form.set_value(grade_fieldname, res.message[0])
					save_data_to_doc_on_change(grade_fieldname, res.message[0])
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
				frappe.web_form.set_df_property(school_fieldname, 'depends_on', `eval:doc.${school_fieldname}==''||doc.${school_fieldname}!='';`);
				if (res.message.length == 1) {
					frappe.web_form.set_value(school_fieldname, res.message[0])
					save_data_to_doc_on_change(school_fieldname, res.message[0])
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

	// setTimeout(() => {
	// 	keys.forEach((value, index) => {
	// 		if (frappe.web_form.get_value(value) == null) frappe.web_form.set_df_property(value, "hidden", 1)
	// 	})
	// }, 2000);

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
				for (let key in keys) {
					frappe.web_form.set_value(key, res.message[key])
				}
			}
		}
	})
}


frappe.ready(function () {
	// Change Status To Completed On Web Form Submission
	$(".submit-btn").on("click", () => {
		frappe.call({
			method: "fh_admission.fh_admission.web_form.admission_inquiry.admission_inquiry.change_status_of_doc_on_form_submit_and_send_message",
			args: {
				"docname": frappe.web_form.doc.mobile_no,
			}
		})
	})

	setTimeout(() => {
		set_school_and_grade_values_on_load()
	}, 2000);

	// Fetch Eligibility Criteria On Click Of Button
	$("#first_child_check_eligibility").on("click", () => {
		check_eligibility_criteria_and_set_field_options(
			frappe.web_form.get_value("first_child_date_of_birth"),
			frappe.web_form.get_value("academic_year"),
			frappe.web_form.get_value("city_for_admission"),
			'first_child_eligible_grades',
			'first_child_eligible_schools',
			'#first_child_check_eligibility'
		)
	})

	$("#second_child_check_eligibility").on("click", () => {
		check_eligibility_criteria_and_set_field_options(
			frappe.web_form.get_value("second_child_date_of_birth"),
			frappe.web_form.get_value("academic_year"),
			frappe.web_form.get_value("city_for_admission"),
			'second_child_eligible_grades',
			'second_child_eligible_schools',
			"#second_child_check_eligibility"
		)
	})

	$("#third_child_check_eligibility").on("click", () => {
		check_eligibility_criteria_and_set_field_options(
			frappe.web_form.get_value("third_child_childs_dob"),
			frappe.web_form.get_value("academic_year"),
			frappe.web_form.get_value("city_for_admission"),
			'third_child_eligible_grades',
			'third_child_eligible_schools',
			"#third_child_check_eligibility"
		)
	})

	$("#fourth_child_check_eligibility").on("click", () => {
		check_eligibility_criteria_and_set_field_options(
			frappe.web_form.get_value("fourth_child_childs_dob"),
			frappe.web_form.get_value("academic_year"),
			frappe.web_form.get_value("city_for_admission"),
			'fourth_child_eligible_grades',
			'fourth_child_eligible_schools',
			"#fourth_child_check_eligibility"
		)
	})

	$("#fifth_child_check_eligibility").on("click", () => {
		check_eligibility_criteria_and_set_field_options(
			frappe.web_form.get_value("fifth_child_childs_dob"),
			frappe.web_form.get_value("academic_year"),
			frappe.web_form.get_value("city_for_admission"),
			'fifth_child_eligible_grades',
			'fifth_child_eligible_schools',
			"#fifth_child_check_eligibility"
		)
	})

	// Save Field Data On Change Of Field Value
	frappe.web_form.on('email_id', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));

	frappe.web_form.on('where_are_you_from', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
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
	frappe.web_form.on('do_you_want_to_add_child_second', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));

	frappe.web_form.on('second_child_first_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_middle_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_last_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_gender', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_date_of_birth', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_current_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_eligible_schools', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('do_you_want_to_add_child_third', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('second_child_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));

	frappe.web_form.on('third_child_first_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_middle_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_last_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_gender', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_childs_dob', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_current_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_eligible_schools', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('do_you_want_to_add_another_child_fourth', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('third_child_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));

	frappe.web_form.on('fourth_child_first_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_middle_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_last_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_gender', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_childs_dob', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_current_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_eligible_schools', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('do_you_want_to_add_another_child_fifth', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));
	frappe.web_form.on('fourth_child_school_name', (field, value) => save_data_to_doc_on_change(field.df.fieldname, value));

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
});