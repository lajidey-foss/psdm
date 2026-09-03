// Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
// For license information, please see license.txt

frappe.ui.form.on("Truckon Closing", {
    onload: function (frm) {
        frm.set_query("truckon", function (doc) {
            return { filters: { status: "Scheduled"}};
        });
    },
	refresh(frm) {
        if(!frm.is_new()) {
			frm.add_custom_button(__('Process Rejects'),
				function() {
					frm.trigger("allocate_trip")
				}
            ).addClass('btn-danger');
		}
	},
     allocate_trip: function(frm) {
		frappe.call({
            method: 'psdm.psd_manager.doctype.truckon_closing.truckon_closing.process_rejects',
            args: {
                self: frm.doc
            },
            callback: (r) => {
                if (r.message) {
                    frappe.msgprint(__('Stock Entry created, awaiting review before submission'));
                }
            }
            });
	},
});
