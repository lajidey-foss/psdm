// Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
// For license information, please see license.txt

frappe.ui.form.on("Logon Slip", {
    setup: (frm) => {
        frm.get_uom_qty_fig = function(frm){
            let total_qty = 0;
            frm.doc.slip_detail.forEach(elm => {
                total_qty += flt(elm.qty);
            });
            frm.set_value("total_qty", total_qty);
        },
        frm.get_tons_qty_fig = function(frm) {
            let total_tons = 0.0;
            frm.doc.slip_detail.forEach(elmt => {
                total_tons += flt (elmt.qty_in_tons);
            });
            frm.set_value("total_tons", total_tons);
        }

    },
    refresh: function(frm) {
		if(!frm.is_new()) {
			// Quotation or [Request for Quote]
			frm.add_custom_button(__('Allocate'),
				function() {
					frm.trigger("allocate_trip")
				}
            ).addClass('btn-danger');
            
            /*.css({
                'background-color': '#8A2BE2',
                'color': 'white'
            })*/
            // group
			//frm.add_custom_button(__('Project'), () => make_project(), __('Create'));
			
		}

	},
    allocate_trip: function(frm) {
		frappe.model.open_mapped_doc({
            method: "psdm.psd_manager.doctype.logon_slip.logon_slip.create_trip",
			frm: frm
		})
	},
});


frappe.ui.form.on("Logon Slip Detail", {
    qty: function(frm, cdt, cdn) {
        frm.get_uom_qty_fig(frm);
        frm.refresh_field(qty);
    },
    qty_in_tons: function (frm, cdt, cdn) {
        frm.get_tons_qty_fig(frm);
        frm.refresh_field(qty_in_tons);
    }
})
