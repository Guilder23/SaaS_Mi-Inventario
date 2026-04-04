document.addEventListener('DOMContentLoaded', function () {
	const modal = document.getElementById('modalCrearPlan');
	if (!modal) return;

	// Bootstrap (jQuery): resetear al abrir, para que no queden valores previos.
	if (window.jQuery) {
		window.jQuery(modal).on('show.bs.modal', function () {
			const form = modal.querySelector('form');
			if (form) {
				form.reset();
			}

			const chk = document.getElementById('planActivoCrear');
			if (chk) {
				chk.checked = true;
			}
		});
	}
});
