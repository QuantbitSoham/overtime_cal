// Copyright (c) 2023, erpdata and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee OT Calculation', {
    refresh: function(frm) {
		$('.layout-side-section').hide();
		$('.layout-main-section-wrapper').css('margin-left', '0');
	},
    to_date: function(frm) {
		frm.clear_table("supervisor_list");
		frm.refresh_field('supervisor_list');
        frm.clear_table("employee_overtime_amount");
		frm.refresh_field('employee_overtime_amount');
        frm.clear_table("employee_overtime");
		frm.refresh_field('employee_overtime');
		frm.call({
			method:"get_month_dates",
			doc:frm.doc,
			args:{
				"input_date":frm.doc.from_date
			}
		})
	},
    from_date: function(frm) {
		frm.clear_table("supervisor_list");
		frm.refresh_field('supervisor_list');
        frm.clear_table("employee_overtime_amount");
		frm.refresh_field('employee_overtime_amount');
        frm.clear_table("employee_overtime");
		frm.refresh_field('employee_overtime');
		frm.call({
			method:"get_month_dates",
			doc:frm.doc,
			args:{
				"input_date":frm.doc.from_date
			}
		})
	},
    select_all: function(frm) {
		frm.call({
			method:'checkall',
			doc:frm.doc
		})
	}
});


frappe.ui.form.on('Employee OT Calculation', {
	get_overtime: function(frm) {
		frm.clear_table("employee_overtime");
		frm.refresh_field('employee_overtime');
        frm.clear_table("employee_overtime_amount");
		frm.refresh_field('employee_overtime_amount');
		frm.call({
			method:'get_overtime',
			doc:frm.doc
		})
	}
});




frappe.ui.form.on('Employee OT Calculation', {
    download_file: function(frm) {
        // Check if the form is saved
        if (!frm.doc.__islocal) {
            frappe.call({
                method: 'download_file',
                doc: frm.doc,
                callback: function(r) {
                    if (r.message) {
                        // var file_path = "https://migratesugar.erpdata.in/files/output.csv";
                        window.open(r.message);
                    }
                }
            });
        } else {
            frappe.msgprint(__("Please save the form before downloading."));
        }
    }
});



frappe.ui.form.on('Employee OT Calculation', {
    download: function(frm) {
        // Check if the form is saved
        if (!frm.doc.__islocal) {
            frappe.call({
                method: 'download',
                doc: frm.doc,
                callback: function(r) {
                    if (r.message) {
                        
                        // var file_path = "https://migratesugar.erpdata.in/files/output.csv";
                        window.open(r.message);
                    }
                }
            });
        } else {
            frappe.msgprint(__("Please save the form before downloading."));
        }
    }
});




frappe.ui.form.on('Employee OT Calculation', {
    refresh: function(frm) {
        // Style fields in the main table
           frm.fields_dict['from_date'].$input.css('background-color', '#D2E9FB');
            frm.fields_dict['to_date'].$input.css('background-color', '#D2E9FB');
        

        // Style fields in a child table (assuming a table named "child_table")
   
    }
});
frappe.ui.form.on('EOC Employee LIst', {
    to_date: function(frm) {
        // Style fields in the main table
        frm.fields_dict['supervisor_name'].$input.css('background-color', '#D2E9FB');
        frm.fields_dict['supervisor_id'].$input.css('background-color', '#D2E9FB');
    }
});
