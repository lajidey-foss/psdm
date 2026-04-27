# Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt
from frappe import _


class LogonSlip(Document):
	def on_submit(self):
		if not self.slip_detail:
			frappe.throw(_("Add items before submitting"))
		#self.status = "Scheduled"
		""" frappe.db.set_value(
			self.doctype,
			self.name,
			"status",
			"Scheduled",
			update_modified=True
		) """
		self.db_set("status", "Scheduled")
		self.reload()

		self.create_purchase_invoice()
		#pass
	def on_cancel(self):
		self.status = "Cancelled"
		frappe.db.set_value(
			self.doctype,
			self.name,
			"status",
			"Cancelled",
			update_modified=True
		)

	""" def on_update(self):
		self.create_purchase_invoice() """
	
	def create_purchase_invoice(self):
		ps_settings = frappe.get_doc('Pipeline Settings')

		new_pi = frappe.new_doc("Purchase Invoice")
		new_pi.supplier = ps_settings.default_supplier # or "LAFARGE"
		new_pi.company = self.company or frappe.defaults.get_user_default("company")
		new_pi.update_stock = True
		new_pi.set_warehouse = self.lifting_warehouse

		for row in self.get("slip_detail") :
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
				.where( (table.lo_detail == lt_item ) )
			)
			# (table.status != "Rejected") &
			return query.run(pluck="qty")[0] 

		already_allocated = get_billed_qty(source_doc.name) or 0
		# it is returning None
		#print(f"==================> \n already_allocated :{already_allocated} \n ")
		pending_qty = flt(source_doc.qty) - flt(already_allocated)
		
		if pending_qty > 0:
			target_doc.accepted_qty = pending_qty
		else:
			# target_doc.accepted_qty = 0
			frappe.throw(_("Cannot allocate more quantity"))
		#target_doc.accepted_qty = flt(source_doc.qty) - flt(already_allocated) 

	doclist = get_mapped_doc(
		"Logon Slip",
		source_doc,
		{
			"Logon Slip": {
				"doctype": "Allocation", 
				"validation": {"docstatus": ["=", 1]}
				},
			"Logon Slip Detail": {
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