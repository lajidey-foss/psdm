// Copyright (c) 2026, Pivotage Intergrated Ltd. and Contributors
// For license information, please see license.txt

// render
frappe.listview_settings["Logon Slip"] = {
	get_indicator: function (doc) {
		var status_color = {
			Draft: "red",
			Scheduled: "orange",
			Closed: "green",
			Cancelled: "red",
		};
		return [__(doc.status), status_color[doc.status], "status,=," + doc.status];
	},
};
