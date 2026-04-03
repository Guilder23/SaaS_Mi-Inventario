/* ============================================================================
   MODAL EDITAR EMPRESA
   ============================================================================ */

function inicializarModalEditar() {
    const botones = document.querySelectorAll('.btn-editar-empresa');
    if (!botones.length) return;

    botones.forEach((btn) => {
        btn.addEventListener('click', () => {
            document.getElementById('editarEmpresaId').value = btn.dataset.empresaId || '';
            document.getElementById('editPlan').value = btn.dataset.empresaPlan || 'basico';
            document.getElementById('editVencimiento').value = btn.dataset.empresaVencimiento || '';
            document.getElementById('editActiva').checked = btn.dataset.empresaActiva === 'True';
            document.getElementById('editNotas').value = btn.dataset.empresaNotas || '';
        });
    });
}
