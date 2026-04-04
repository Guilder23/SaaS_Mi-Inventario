(function () {
    // Publicado
    const modalPub = document.getElementById('modalTogglePublicado');
    if (modalPub) {
        $('#modalTogglePublicado').on('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            if (!button) return;

            const id = button.getAttribute('data-id');
            const titulo = button.getAttribute('data-titulo') || '-';
            const publicado = button.getAttribute('data-publicado') === '1';

            const inputId = modalPub.querySelector('#togglePublicadoId');
            const elTitulo = modalPub.querySelector('#togglePublicadoTitulo');
            const elTexto = modalPub.querySelector('#togglePublicadoTexto');
            const btn = modalPub.querySelector('#togglePublicadoBtn');

            if (inputId) inputId.value = id || '';
            if (elTitulo) elTitulo.textContent = titulo;
            if (elTexto) {
                elTexto.textContent = publicado
                    ? '¿Deseas despublicar este comunicado? Ya no se mostrará a los usuarios.'
                    : '¿Deseas publicar este comunicado? Se mostrará a todos los usuarios.';
            }
            if (btn) {
                btn.classList.toggle('btn-primary', !publicado);
                btn.classList.toggle('btn-warning', publicado);
                btn.innerHTML = publicado
                    ? '<i class="fas fa-ban"></i> Despublicar'
                    : '<i class="fas fa-check"></i> Publicar';
            }
        });
    }

    // Activo
    const modalAct = document.getElementById('modalToggleActivo');
    if (modalAct) {
        $('#modalToggleActivo').on('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            if (!button) return;

            const id = button.getAttribute('data-id');
            const titulo = button.getAttribute('data-titulo') || '-';
            const activo = button.getAttribute('data-activo') === '1';

            const inputId = modalAct.querySelector('#toggleActivoId');
            const elTitulo = modalAct.querySelector('#toggleActivoTitulo');
            const elTexto = modalAct.querySelector('#toggleActivoTexto');
            const btn = modalAct.querySelector('#toggleActivoBtn');

            if (inputId) inputId.value = id || '';
            if (elTitulo) elTitulo.textContent = titulo;
            if (elTexto) {
                elTexto.textContent = activo
                    ? '¿Deseas desactivar este comunicado? No se mostrará a los usuarios.'
                    : '¿Deseas activar este comunicado? Podrá mostrarse si está publicado.';
            }
            if (btn) {
                btn.classList.toggle('btn-danger', activo);
                btn.classList.toggle('btn-success', !activo);
                btn.innerHTML = activo
                    ? '<i class="fas fa-ban"></i> Desactivar'
                    : '<i class="fas fa-check"></i> Activar';
            }
        });
    }
})();
