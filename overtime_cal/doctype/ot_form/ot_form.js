// Copyright (c) 2023, erpdata and contributors
// For license information, please see license.txt

frappe.ui.form.on('OT Form', {
    refresh: function(frm) {
                     $('.layout-side-section').hide();
                     $('.layout-main-section-wrapper').css('margin-left', '0');
    }
});



frappe.ui.form.on('Child OT Form', {
    date: function(frm,cdt,cdn) {
        var r=locals[cdt][cdn];
        frm.call({
            method:'check_repeat_entry',
            doc:frm.doc,
            args:{
                "emp_id":r.worker_id,
                "dept":r.department,
                "idx":r.idx,
                "date":r.date
            }
        })
    }
});

