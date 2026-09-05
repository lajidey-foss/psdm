// Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
// For license information, please see license.txt

frappe.ui.form.on("Truckon", {
	setup: (frm) => {
        frm.get_uom_qty_fig = function(frm){
            let total_qty = 0;
            frm.doc.items.forEach(elm => {
                total_qty += flt(elm.quantity);
            });
            frm.set_value("total_qty", total_qty);
        },
        frm.get_tons_qty_fig = function(frm) {
            let total_tons = 0.0;
            frm.doc.items.forEach(elmt => {
                total_tons += flt (elmt.qty_in_tons);
            });
            frm.set_value("total_tons", total_tons);
        },
        frm.get_total_amount = function(frm) {
            let total_amount = 0.0;
            frm.doc.items.forEach(elmt => {
                total_amount += flt(elmt.quantity) * flt(elmt.rate) ;
            });
            frm.set_value("total_amount", total_amount);
        }

    },
    refresh(frm) {
        if(frm.doc.docstatus == 1) {
			// Quotation or [Request for Quote]
			frm.add_custom_button(__('Allocate'),
				function() {
					frm.trigger("allocate_trip")
				}
            ).addClass('btn-danger');
			
		}
	},
    allocate_trip: function(frm) {
		frappe.model.open_mapped_doc({
            method: "psdm.psd_manager.doctype.truckon.truckon.create_trip",
			frm: frm
		})
	},
});

frappe.ui.form.on("Truckon Detail", {
    quantity: function(frm, cdt, cdn) {
        frm.get_uom_qty_fig(frm);
        frm.refresh_field(qty);
    },
    qty_in_tons: function (frm, cdt, cdn) {
        frm.get_tons_qty_fig(frm);
        frm.refresh_field(qty_in_tons);
    },
    rate: function (frm, cdt, cdn) {
        frm.get_total_amount(frm);
        //frm.refresh_field(rate);
        updateLine(frm, cdt, cdn);
    }
});

var updateLine = function(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (!row.rate) return;
    //console.table(row);
    
    
    let amount = (row.quantity || 0) * (row.rate || 0);

    // Use frappe.model.set_value to ensure the UI updates and the form is marked 'Dirty'
    frappe.model.set_value(cdt, cdn, 'amount', amount);
    
    // Refresh the table field to show changes
    frm.refresh_field('items');
};
