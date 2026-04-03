/* ============================================================================
   MODAL CAMBIAR ESTADO EMPRESA
   ============================================================================ */

function inicializarModalEliminar() {
    const botones = document.querySelectorAll('.btn-eliminar-empresa');
    if (!botones.length) return;

    botones.forEach((btn) => {
        btn.addEventListener('click', () => {
            const activo = btn.dataset.empresaActiva === 'True';
            document.getElementById('eliminarEmpresaId').value = btn.dataset.empresaId || '';
            document.getElementById('eliminarEmpresaTexto').textContent = activo
                ? `Se bloqueara la empresa ${btn.dataset.empresaNombre}.`
                : `Se activara la empresa ${btn.dataset.empresaNombre}.`;
        });
    });
}
