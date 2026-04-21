frappe.ready(function () {
	var form = document.querySelector('.login-content form, .page-card form');
	if (!form) return;

	var existing = document.getElementById('tn-signup-link');
	if (existing) return;

	var wrapper = document.createElement('div');
	wrapper.id = 'tn-signup-link';
	wrapper.style.cssText = 'text-align:center;margin-top:1rem;font-size:0.9rem;';
	wrapper.innerHTML =
		"Don't have an account? " +
		'<a href="/shop#/signup" style="color:#5b5ea6;font-weight:600;">Sign Up Free</a>';

	form.appendChild(wrapper);
});
