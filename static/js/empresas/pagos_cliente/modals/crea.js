/* ============================================================================
   MODAL CREAR PAGO CLIENTE
   ============================================================================ */

function inicializarModalCrear() {
    const modal = document.getElementById('modalCrearPago');
    const form = document.getElementById('formCrearPago');
    if (!modal || !form) return;

    const inputMonto = document.getElementById('monto');
    const inputComprobante = document.getElementById('comprobante');
    const inputComentario = document.getElementById('comentario');

    modal.addEventListener('show.bs.modal', () => {
        // Si el monto está bloqueado (precio del plan), no reseteamos todo el form
        // porque algunos navegadores limpian valores default en inputs readonly.
        if (inputMonto && inputMonto.hasAttribute('readonly')) {
            if (inputComprobante) inputComprobante.value = '';
            if (inputComentario) inputComentario.value = '';
            return;
        }

        form.reset();
    });
}
