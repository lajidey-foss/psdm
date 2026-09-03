# Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class PaymentWallet(Document):
	pass


@frappe.whitelist()
def create_truckon (source_name, target_doc=None):
	def postprocess(source, doc):
		doc.payment_wallet = source.name

	doc = get_mapped_doc(
		"Payment Wallet",
		source_name,
		{
			"Payment Wallet": {
				"doctype": "Truckon",
				"field_map": {
					"name": "payment_wallet",
				},
			},
		},
		target_doc,
		postprocess,
	)

	return doc