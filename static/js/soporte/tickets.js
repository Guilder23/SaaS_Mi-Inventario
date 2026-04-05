document.addEventListener("DOMContentLoaded", function () {
    var form = document.querySelector('form input[name="action"][value="crear_ticket"]');
    if (form) {
        var ticketForm = form.closest("form");
        var mensaje = document.getElementById("mensaje");
        var adjunto = document.getElementById("adjunto");

        if (ticketForm && mensaje && adjunto) {
            ticketForm.addEventListener("submit", function (e) {
                var texto = (mensaje.value || "").trim();
                var tieneAdjunto = adjunto.files && adjunto.files.length > 0;

                if (!texto && !tieneAdjunto) {
                    e.preventDefault();
                    alert("Debes escribir un mensaje o adjuntar un archivo.");
                }
            });
        }
    }

    var fileInput = document.getElementById("adjunto");
    if (!fileInput) {
        return;
    }

    fileInput.addEventListener("change", function () {
        var label = fileInput.nextElementSibling;
        if (label && fileInput.files.length > 0) {
            label.textContent = fileInput.files[0].name;
        }
    });
});
