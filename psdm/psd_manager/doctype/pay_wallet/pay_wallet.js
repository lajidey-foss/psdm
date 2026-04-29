// Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
// For license information, please see license.txt

frappe.ui.form.on("Pay Wallet", {
	refresh(frm) {
        if(!frm.is_new()) {
			// Quotation or [Request for Quote]
			frm.add_custom_button(__('Logon'),
				function() {
					frm.trigger("make_logons")
				}, __('Create'));	
			
		}

	},
    make_logons: function(frm) {
		frappe.model.open_mapped_doc({
			method: "psdm.psd_manager.doctype.pay_wallet.pay_wallet.create_logon",
			frm: frm
		})
	},
});
