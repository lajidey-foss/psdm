# Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt


class LogonSlip(Document):
	#def
	def on_update(self):
		self.create_purchase_invoice()
		""" if self.status == "Submit" :
			self.create_purchase_invoice() """
	
	def create_purchase_invoice(self):
		new_pi = frappe.new_doc("Purchase Invoice")
		new_pi.supplier = "LAFARGE"
		new_pi.company = self.company or frappe.defaults.get_user_default("company")
		new_pi.update_stock = True
		new_pi.set_warehouse = self.default_warehouse

		for row in self.get("slip_detail") :
			new_pi.append("items", {
				"item_code": row.item,
				"qty": row.qty
			})
		new_pi.insert()

		frappe.msgprint(f"Purchase Invoice {new_pi.name} has been generated.")
		


@frappe.whitelist()
def xcreate_trip (source_name, target_doc=None):

	def postprocess(source, doc):
		# doc.idea = source.name
		doc.logon = source.name,
	
	doc = get_mapped_doc(
		"Logon Slip",
		source_name,
		{
			"Logon Slip": {
				"doctype": "Trip Allocation",
				"field_map": {
					"name": "logon"
				},
			},
		},
		target_doc,
		postprocess,
	)
	return doc

@frappe.whitelist()
def create_trip(source_doc, target_doc=None):

	def update_item(source_doc, target_doc, source_parent):
		def get_billed_qty(lt_item):
			from frappe.query_builder.functions import Sum
			
			table = frappe.qb.DocType("Allocation Detail")
			query = (
				frappe.qb.from_(table)
				.select(Sum(table.accepted_qty).as_("qty"))
				.where((table.docstatus == 0) & (table.lo_detail == lt_item ) )
			)
			return query.run(pluck="qty")[0] 

		already_allocated = get_billed_qty(source_doc.name) or 0
		# it is returning None
		print(f"==================> \n already_allocated :{already_allocated} \n ")
		pending_qty = flt(source_doc.qty) - flt(already_allocated)
		if pending_qty > 0:
			target_doc.accepted_qty = pending_qty
		else:
			target_doc.accepted_qty = 0
		#target_doc.accepted_qty = flt(source_doc.qty) - flt(already_allocated) 

	doclist = get_mapped_doc(
		"Logon Slip",
		source_doc,
		{
			"Logon Slip": {"doctype": "Allocation", "validation": {"docstatus": ["=", 0]}},
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