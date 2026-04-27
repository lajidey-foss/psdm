// Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
// For license information, please see license.txt

frappe.ui.form.on("Logon Closing", {
	onload: function (frm) {
        frm.set_query("logon", function (doc) {
            return { filters: { status: "Scheduled"}};
        });
    },
    refresh: function(frm) {
		if(!frm.is_new()) {
			// Quotation or [Request for Quote]
			frm.add_custom_button(__('Process Rejects'),
				function() {
					frm.trigger("allocate_trip")
				}
            ).addClass('btn-danger');/*.css({
                'background-color': '#f0ad4e',
                'color': 'white'
            });*/
            /*.addClass('btn-danger');*/
            // btn-primary
			
		}

	},
    allocate_trip: function(frm) {
		frappe.call({
                    method: 'psdm.psd_manager.doctype.logon_closing.logon_closing.process_rejects',
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
