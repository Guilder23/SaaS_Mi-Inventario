(function () {
    const modal = document.getElementById('modalEditarComunicado');
    if (!modal) return;

    $('#modalEditarComunicado').on('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        if (!button) return;

        const id = button.getAttribute('data-id');
        const titulo = button.getAttribute('data-titulo') || '';
        const mensaje = button.getAttribute('data-mensaje') || '';

        const inputId = modal.querySelector('#editarComunicadoId');
        const inputTitulo = modal.querySelector('#editarComunicadoTitulo');
        const inputMensaje = modal.querySelector('#editarComunicadoMensaje');

        if (inputId) inputId.value = id || '';
        if (inputTitulo) inputTitulo.value = titulo;
        if (inputMensaje) inputMensaje.value = mensaje;
    });
})();
