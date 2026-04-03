/* ============================================================================
   MODAL CREAR EMPRESA
   ============================================================================ */

function inicializarModalCrear() {
    const modal = document.getElementById('modalCrearEmpresa');
    const form = document.getElementById('formCrearEmpresa');
    if (!modal || !form) return;

    modal.addEventListener('show.bs.modal', () => {
        form.reset();
    });
}
