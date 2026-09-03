// Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
// For license information, please see license.txt

frappe.listview_settings["Truckon Closing"] = {
    onload: function(listview) {
        // Add an “Quick Add” button to the list page
        listview.page.add_inner_button(__('Close Truckon'), () => {
            // Define the dialog
            const dialog = new frappe.ui.Dialog({
                title: __('New Truckon Closing'),
                fields: [
                    {
                        label: __('Truckon Close Date'),
                        fieldname: 'truckon_close_date',
                        fieldtype: 'Date',
                        reqd: 1,
                        default: 'Today'
                    },
                    {
                        label: __('Truckon'),
                        fieldname: 'truckon',
                        fieldtype: 'Link',
                        options: 'Truckon',
                        reqd: 1,
                        get_query: () => poc_query(),
                    },
                ]
            });

            // Hook up the Save button
            dialog.set_primary_action(__('Save'), () => {
                const values = dialog.get_values();
                if (!values) return;

                // Call the server‐side method
                frappe.call({
                    method: 'psdm.psd_manager.doctype.truckon_closing.truckon_closing.close_cycle',
                    args: {
                        end: values.truckon_close_date,
                        slip: values.truckon
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