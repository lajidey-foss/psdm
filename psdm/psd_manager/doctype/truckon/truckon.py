# Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt
from frappe import _


class Truckon(Document):
	def on_submit(self):
		if not self.items:
			frappe.throw(_("Add items before submitting"))

		self.db_set("status", "Scheduled")
		self.reload()

		self.create_purchase_invoice()

	def on_cancel(self):
		self.status = "Cancelled"
		frappe.db.set_value(
			self.doctype,
			self.name,
			"status",
			"Cancellec",
			update_modified=True
		)

	def create_purchase_invoice(self):
		""" work here"""
		ps_settings = frappe.get_doc('Pipeline Settings')

		new_pi = frappe.new_doc("Purchase Invoice")
		new_pi.supplier = ps_settings.default_supplier # or "LAFARGE"
		new_pi.company = self.company or frappe.defaults.get_user_default("company")
		new_pi.update_stock = True
		new_pi.set_warehouse = ps_settings.lifting_warehouse

		for row in self.get("items") :
			new_pi.append("items", {
				"item_code": row.item,
				"qty": row.qty,
				"rate": row.rate
			})

		new_pi.insert()

		frappe.msgprint(f"Purchase Invoice {new_pi.name} has been generated.")

		

@frappe.whitelist()
def create_trip(source_doc, target_doc=None):
	def update_item(source_doc, target_doc, source_parent):
		def get_billed_qty(lt_item):
			from frappe.query_builder.functions import Sum

			table = frappe.qb.DocType("Allocation Detail")
			query = (
				frappe.qb.from_(table)
				.select(Sum(table.accepted_qty).as_("qty"))
				.where( (table.lo_detail == lt_item))
			)
			return query.run(pluck="qty")[0]

		already_allocated = get_billed_qty(source_doc.name) or 0

		pending_qty = flt(source_doc.qty) - flt(already_allocated)

		if pending_qty > 0:
			target_doc.accepted_qty = pending_qty
		else:
			frappe.throw(_("Cannot allocate more quantity"))
		
	doclist = get_mapped_doc(
		"Truckon",
		source_doc,
		{
			"Truckon": {
				"doctype": "Allocation", 
				"validation": {"docstatus": ["=", 1]}
			},
			"Truckon Detail": {
				"doctype": "Allocation Detail",
				"field_map": {
					"name": "lo_detail",
					"parent": "logon_slip",
				},
				"postprocess": update_item,
			},
		},
		target_doc,
	)
	return doclist
