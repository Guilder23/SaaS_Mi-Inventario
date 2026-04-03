/* ============================================================================
   MODAL EDITAR CLIENTE
   ============================================================================ */

function inicializarModalEditar() {
    const botones = document.querySelectorAll('.btn-editar-cliente');
    if (!botones.length) return;

    botones.forEach((btn) => {
        btn.addEventListener('click', () => {
            document.getElementById('editarClienteId').value = btn.dataset.perfilId || '';
            document.getElementById('editFirstName').value = btn.dataset.firstName || '';
            document.getElementById('editLastName').value = btn.dataset.lastName || '';
            document.getElementById('editEmail').value = btn.dataset.email || '';
            document.getElementById('editActivo').checked = btn.dataset.activo === 'True';
        });
    });
}
