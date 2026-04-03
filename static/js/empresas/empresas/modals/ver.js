/* ============================================================================
   MODAL VER EMPRESA
   ============================================================================ */

function inicializarModalVer() {
    const botones = document.querySelectorAll('.btn-ver-empresa');
    if (!botones.length) return;

    botones.forEach((btn) => {
        btn.addEventListener('click', () => {
            document.getElementById('verNombreEmpresa').textContent = btn.dataset.empresaNombre || '';
            document.getElementById('verPlanEmpresa').textContent = btn.dataset.empresaPlan || '';
            document.getElementById('verEstadoEmpresa').textContent = btn.dataset.empresaActiva === 'True' ? 'Activa' : 'Inactiva';
            document.getElementById('verVencimientoEmpresa').textContent = btn.dataset.empresaVencimiento || '-';
            document.getElementById('verNotasEmpresa').textContent = btn.dataset.empresaNotas || 'Sin notas';
        });
    });
}
