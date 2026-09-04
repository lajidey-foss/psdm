# Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Allocation(Document):
	# def on_update(self):
	def on_update(self):
		# just doing
		if self.status == "Recieved" :
			self.create_sales_invoice()
	
	# def create_sales_invoice(self):
	def create_sales_invoice(self):
		""" # Initialize the new Sales Invoice document
        new_si.insert() """
		ps_settings = frappe.get_doc('Pipeline Settings')
		new_si = frappe.new_doc("Sales Invoice")

		# map
		new_si.customer = self.customer
		# new_si.posting_date = self.date or nowdate()
		new_si.company = self.company or frappe.defaults.get_user_default("company")
		new_si.custom_truckon = self.truckon
		new_si.update_stock = True
		new_si.custom_trip = self.name
		new_si.set_warehouse = ps_settings.lifting_warehouse

		for row in self.get("allocation_detail"):
			new_si.append("items", {
				"item_code": row.item,
				"qty": row.accepted_qty,
				"warehouse": ps_settings.lifting_warehouse,
				"income_account": self.get_default_income_account()
			})
		
		new_si.insert()
		# Update the current Trip Allocation record to link the new invoice
        # This requires a 'sales_invoice' link field in your Trip Allocation doctype
		#self.db_set("sales_invoice", new_si.name)

		frappe.msgprint(f"Sales Invoice {new_si.name} has been generated.")

	def get_default_income_account(self):
		""""""
		return frappe.get_cached_value("Company", frappe.defaults.get_user_default("company"), "default_income_account")
