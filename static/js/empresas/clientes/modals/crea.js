/* ============================================================================
   MODAL CREAR CLIENTE
   ============================================================================ */

function inicializarModalCrear() {
    const modal = document.getElementById('modalCrearCliente');
    const form = document.getElementById('formCrearCliente');
    if (!modal || !form) return;

    modal.addEventListener('show.bs.modal', () => {
        form.reset();
    });
}
