// Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
// For license information, please see license.txt

frappe.listview_settings["Logon Closing"] = {
	/*get_indicator: function (doc) {
		var status_color = {
			Draft: "red",
			Scheduled: "orange",
			Closed: "green",
			Cancelled: "red",
		};
		return [__(doc.status), status_color[doc.status], "status,=," + doc.status];
	},*/
    onload: function(listview) {
        // Add an “Quick Add” button to the list page
        listview.page.add_inner_button(__('Close Logon'), () => {
            // Define the dialog
            const dialog = new frappe.ui.Dialog({
                title: __('New Logon Closing'),
                fields: [
                    {
                        label: __('Logon Close Date'),
                        fieldname: 'logon_close_date',
                        fieldtype: 'Date',
                        reqd: 1,
                        default: 'Today'
                    },
                    {
                        label: __('Logon'),
                        fieldname: 'logon',
                        fieldtype: 'Link',
                        options: 'Logon Slip',
                        reqd: 1,
                        get_query: () => poc_query(),
                    },
                    /*{
                        label: __('Closing Figure Reconciliation'),
                        fieldname: 'closing_figure_reconciliation',
                        fieldtype: 'Table',
                        reqd: 1,
                        fields: [
                            {
                                label: __('Item Code'),
                                fieldname: 'item_code',
                                fieldtype: 'Link',
                                in_list_view: 1,
                                options: 'Item',
                                reqd: 1
                            },
                            {
                                label: __('Quantity'),
                                fieldname: 'qty',
                                fieldtype: 'Float',
                                in_list_view: 1,
                                reqd: 1
                            }
                        ]
                    }*/
                ]
            });

            // Hook up the Save button
            dialog.set_primary_action(__('Save'), () => {
                const values = dialog.get_values();
                if (!values) return;

                // Call the server‐side method
                frappe.call({
                    method: 'psdm.psd_manager.doctype.logon_closing.logon_closing.close_cycle',
                    args: {
                        end: values.logon_close_date,
                        slip: values.logon
                    },
                    callback: (r) => {
                        if (r.message) {
                            frappe.msgprint(__('Created: {0}', [r.message]));
                            dialog.hide();
                            listview.refresh();
                        }
                    }
                });
            });

            dialog.show();
            const poc_query = () => {
                return {
                    filters: { status: "Scheduled"},
                }
            }
        });
    }
};