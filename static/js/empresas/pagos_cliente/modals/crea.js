/* ============================================================================
   MODAL CREAR PAGO CLIENTE
   ============================================================================ */

function inicializarModalCrear() {
    const modal = document.getElementById('modalCrearPago');
    const form = document.getElementById('formCrearPago');
    if (!modal || !form) return;

    modal.addEventListener('show.bs.modal', () => {
        form.reset();
    });
}
