(function () {
    const modal = document.getElementById('modalVerComunicado');
    if (!modal) return;

    $('#modalVerComunicado').on('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        if (!button) return;

        const titulo = button.getAttribute('data-titulo') || '-';
        const mensaje = button.getAttribute('data-mensaje') || '-';
        const publicado = button.getAttribute('data-publicado') === '1';
        const activo = button.getAttribute('data-activo') === '1';
        const fecha = button.getAttribute('data-fecha') || '-';

        const estadoParts = [];
        estadoParts.push(publicado ? 'Publicado' : 'Borrador');
        if (!activo) estadoParts.push('Inactivo');

        const elTitulo = modal.querySelector('#verComTitulo');
        const elMensaje = modal.querySelector('#verComMensaje');
        const elEstado = modal.querySelector('#verComEstado');
        const elFecha = modal.querySelector('#verComFecha');

        if (elTitulo) elTitulo.textContent = titulo;
        if (elMensaje) elMensaje.textContent = mensaje;
        if (elEstado) elEstado.textContent = estadoParts.join(' | ');
        if (elFecha) elFecha.textContent = fecha;
    });
})();
