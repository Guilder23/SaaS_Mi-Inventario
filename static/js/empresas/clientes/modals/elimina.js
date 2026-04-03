/* ============================================================================
   MODAL CAMBIAR ESTADO CLIENTE
   ============================================================================ */

function inicializarModalEliminar() {
    const botones = document.querySelectorAll('.btn-eliminar-cliente');
    if (!botones.length) return;

    botones.forEach((btn) => {
        btn.addEventListener('click', () => {
            const activo = btn.dataset.activo === 'True';
            document.getElementById('eliminarClienteId').value = btn.dataset.perfilId || '';
            document.getElementById('eliminarClienteTexto').textContent = activo
                ? `Se bloqueara al admin ${btn.dataset.username}.`
                : `Se activara al admin ${btn.dataset.username}.`;
        });
    });
}
