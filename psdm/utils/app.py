import frappe
from frappe.utils.data import now

def wallet_pay_update(doc, method):
    if (doc.payment_type != 'Pay'):
        return
    
    wp = frappe.new_doc('Pay Wallet')
    wp.posting_date = doc.posting_date
    wp.posting_time = now()
    wp.amount = doc.paid_amount
    wp.ref_number = doc.custom_wallet_bank_ref

    wp.insert()
    # apps.psdm.psdm.utils.app.wallet_pay_update
    frappe.msgprint(f"Pay Wallet {wp.name} has been generated.")
