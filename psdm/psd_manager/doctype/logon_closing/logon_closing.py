# Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class LogonClosing(Document):

	def on_submit(self):
		self.db_set("status", "Submitted")
		self.reload()

		update_logon_slip(self)
		


def update_logon_slip(self):

	open_slip = frappe.get_doc("Logon Slip", self.logon)
	open_slip.logon_closing = self.name
	open_slip.logon_close_date = self.logon_close_date
	open_slip.status = "Closed"
	open_slip.save()

@frappe.whitelist()
def close_cycle(end, slip):
	try:

		slip_items = frappe.get_all("Logon Slip Detail", filters={"parent": slip}, fields=["name", "item", "qty"] )

		logon_recon = []
		for row in slip_items:
			allotted_qty = frappe.db.sql(
				"""SELECT SUM(accepted_qty) FROM `tabAllocation Detail`
								WHERE lo_detail = %s""", row.name
			)[0][0] or 0
			logon_recon.append({
				"item": row.item,
				"logon_qty": row.qty,
				"delivered_qty": allotted_qty,
				"difference": flt(row.qty) - flt(allotted_qty)
			})
		
		#print(f"==================> \n run : {logon_recon}  \n ")
		doc = frappe.get_doc({
			'doctype': 'Logon Closing',
            'logon_close_date': end,
            'logon': slip,
			"logon_reconciliation": logon_recon
		})
		doc.insert()

		return doc.name
	
	except	Exception:
		frappe.throw(_('Quick Add Failed'), _('Could not create closing voucher document'))
	
@frappe.whitelist()
def process_rejects(self):
	ps_settings = frappe.get_doc('Pipeline Settings')
	"""move rejected inventory to rejected warehouse pending actual backloading"""
	self = frappe.parse_json(self)
	reconciliation_item = frappe.parse_json(self.logon_reconciliation)
	print(f"==================> \n logon default_warehouse :{self.lifting_warehouse} \n ")
	# destination warehouse
	""" target_warehouse = frappe.db.get_single_value("Stock settings", "default_target_warehouse")
	if not target_warehouse:
		frappe.throw("Please configure a default target warehouse in stock settings") """
	# from_warehouse
	# to_warehouse
	
	# create entry
	stock_entry = frappe.new_doc("Stock Entry")
	stock_entry.stock_entry_type = "Material Transfer"
	stock_entry.posting_date = self.posting_date
	stock_entry.posting_time = self.posting_time
	stock_entry.reference_doctype = "Logon Closing"
	stock_entry.reference_name = self.name
	stock_entry.from_warehouse = ps_settings.lifting_warehouse or self.lifting_warehouse
	stock_entry.to_warehouse = ps_settings.rejected_warehouse # or "Stores - OC"

	for item in reconciliation_item:
		#print(f"==================> \n recon :{item} \n ")
		""" if (flt(item.get('difference')) < 1):
			frappe.throw(_("Reject not required")) """

		stock_entry.append("items", {
			"item_code": item.get('item'),
			"qty": item.get('difference'),
			"s_warehouse": ps_settings.lifting_warehouse or self.lifting_warehouse,
			"t_warehouse": ps_settings.rejected_warehouse
		})
		""",
			"uom": item.uom,
			"conversion_factor": item.conversion_factor"""
	stock_entry.insert()
	#stock_entry.insert(ignore_permissions=True)
	# stock_entry.submit()
	#frappe.msgprint(f"Stock Entry  {stock_entry.name} created, awaiting review before submittion")
	return stock_entry.name
