# Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class PayWallet(Document):
	pass


@frappe.whitelist()
def create_logon(source_name, target_doc=None):
	def postprocess(source, doc):
		doc.pay_wallet = source.name

	doc = get_mapped_doc(
		"Pay Wallet",
		source_name,
		{
			"Pay Wallet": {
				"doctype": "Logon Slip",
				"field_map": {
					"name": "pay_wallet",
				},
			},
		},
		target_doc,
		postprocess,
	)

	return doc