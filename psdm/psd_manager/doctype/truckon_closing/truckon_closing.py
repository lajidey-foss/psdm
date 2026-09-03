# Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt


class TruckonClosing(Document):
	def on_submit(self):
		self.db_set("status", "Submitted")
		self.reload()

		update_truckon(self)
	pass
def update_truckon(self):
	open_truck = frappe.get_doc("Truckon", self.truckon)
	open_truck.truckon_closing = self.name
	open_truck.trunckon_close_date = self.logon_close_date
	open_truck.status = "Closed"
	open_truck.save()

@frappe.whitelist()
def close_truckon(end, truckon):
	try:
		items = frappe.get_all("Truckon Detail", filters={"parent": truckon}, fields=["name", "item", "quantity"] )
		truckon_reconcil = []
		for row in items:
			allotted_qty = frappe.db.sql(
				"""SELECT SUM(accepted_qty) FROM `tabAllocation Detail`
					WHERE lo_detail = %s""", row.name
			)[0][0] or 0
			truckon_reconcil.append({
				"item": row.item,
				"logon_qty": row.qty,
				"delivered_qty": allotted_qty,
				"difference": flt(row.qty) - flt(allotted_qty)
			})

			doc = frappe.get_doc({
				"doctype": "Truckon Closing",
				"truckon_close_date": end,
				"truckon": truckon,
				"truckon_reconciliation": truckon_reconcil
			})
			doc.insert()
			return doc.name

	except Exception:
		frappe.throw(_('Quick Add Failed'), _('Could not create closing voucher document'))

@frappe.whitelist()
def process_rejects(self):
	"""move rejected inventory to rejected warehouse pending actual backloading"""
	ps_settings = frappe.get_doc("Pipeline Settings")
	self = frappe.parse_json(self)
	reconciliation_item = frappe.parse_json(self.truckon_reconciliation)
	# create entry
	stock_entry = frappe.new_doc("Stock Entry")
	stock_entry.stock_entry_type = "Material Transfer"
	stock_entry.posting_date = self.posting_date
	stock_entry.posting_time = self.posting_time
	stock_entry.reference_doctype = "Truckon Closing"
	stock_entry.reference_name = self.name
	stock_entry.from_warehouse = ps_settings.lifting_warehouse or self.lifting_warehouse
	stock_entry.to_warehouse = ps_settings.rejected_warehouse # or "Stores - OC"

	for item in reconciliation_item:
		stock_entry.append("items", {
			"item_code": item.get('item'),
			"qty": item.get('difference'),
			"s_warehouse": ps_settings.lifting_warehouse or self.lifting_warehouse,
			"t_warehouse": ps_settings.rejected_warehouse
		})
	stock_entry.insert()

	return stock_entry.name
#
