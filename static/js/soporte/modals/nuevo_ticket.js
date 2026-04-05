document.addEventListener('DOMContentLoaded', function () {
    var modalEl = document.getElementById('modalNuevoTicket');
    var formEl = document.getElementById('formNuevoTicket');
    var asuntoEl = document.getElementById('asuntoTicket');
    var mensajeEl = document.getElementById('mensajeTicket');
    var adjuntoEl = document.getElementById('adjuntoTicket');

    if (modalEl) {
        // Bootstrap 4 dispara eventos via jQuery
        if (window.jQuery) {
            window.jQuery(modalEl).on('shown.bs.modal', function () {
                try {
                    if (asuntoEl) asuntoEl.focus();
                } catch (e) {
                    // ignore
                }
            });
        }
    }

    if (adjuntoEl) {
        adjuntoEl.addEventListener('change', function () {
            var label = adjuntoEl.nextElementSibling;
            if (label && adjuntoEl.files && adjuntoEl.files.length > 0) {
                label.textContent = adjuntoEl.files[0].name;
            }
        });
    }

    if (formEl && mensajeEl && adjuntoEl) {
        formEl.addEventListener('submit', function (e) {
            var texto = (mensajeEl.value || '').trim();
            var tieneAdjunto = adjuntoEl.files && adjuntoEl.files.length > 0;

            if (!texto && !tieneAdjunto) {
                e.preventDefault();
                alert('Debes escribir un mensaje o adjuntar un archivo.');
            }
        });
    }
});
