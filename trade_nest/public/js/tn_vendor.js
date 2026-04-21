frappe.ui.form.on("TN Vendor", {
	refresh(frm) {
		setTimeout(() => {
			let field = frm.fields_dict.phone;

			if (field && field.$input) {
				let current = field.get_value() || "";

				// अगर empty है तो +91 डालो
				if (!current) {
					field.set_value("+91 ");
				}
			}
		}, 300);
	},
});
