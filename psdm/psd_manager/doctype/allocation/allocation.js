// Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
// For license information, please see license.txt

frappe.ui.form.on("Allocation", {
	onload: function (frm) {
        frm.set_query("truckon", function (doc) {
            return { filters: { status: "Scheduled"}};
        });
    },
    setup: (frm) => {
        frm.get_uom_qty_fig = function(frm){
            let total_qty = 0.0;
            frm.doc.allocation_detail.forEach(elm => {
                total_qty += flt(elm.accepted_qty);
            });
            frm.set_value("total_accepted_qty", total_qty);
        },
        frm.get_tons_qty_fig = function(frm) {
            let total_tons = 0.0;
            frm.doc.allocation_detail.forEach(elmt => {
                total_tons += flt (elmt.qty_in_tons);
            });
            frm.set_value("total_qty_tons", total_tons);
        },
        frm.get_rejected_qty = function(frm) {
            let total_rejected_qty = 0;
            frm.doc.allocation_detail.forEach(elt => {
                total_rejected_qty += flt(elt.rejected_qty);
            });
            frm.set_value("total_rejected_qty", total_rejected_qty);
        }

    },
    refresh: function(frm) {
        if(frm.is_new() ){
			frm.set_value('status', "Draft");
		}
        if (!(frm.is_new()) && (frm.doc.is_recieved) && (frm.doc.status == "Recieved")) {
            frm.disable_save();
        }
    },
    is_recieved: function(frm) {
        if (!(frm.doc.status == "Recieved")) {
            frm.set_value('status', "Recieved");
        }
        //frm.set_value('status', "Recieved");
    }
});

frappe.ui.form.on("Allocation Detail", {
    accepted_qty: function(frm, cdt, cdn) {
        frm.get_uom_qty_fig(frm);
        frm.refresh_field(accepted_qty);
    },
    qty_in_tons: function (frm, cdt, cdn) {
        frm.get_tons_qty_fig(frm);
        frm.refresh_field(qty_in_tons);
    },
    rejected_qty: function (frm, cdt, cdn) {
        frm.get_rejected_qty(frm);
        frm.refresh_field(rejected_qty)
    }
})